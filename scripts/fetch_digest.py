# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "requests>=2.31",
#   "feedparser>=6.0",
# ]
# ///
"""
Fetch AI tool news from free public sources since the last digest.

Outputs a JSON object to stdout. Progress and warnings go to stderr.

Usage:
    uv run scripts/fetch_digest.py [--since YYYY-MM-DD]

If --since is omitted, the date is auto-detected from the most recent file
in the news/ directory. Falls back to 24 hours ago if news/ is empty.
"""

import argparse
import json
import re
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import feedparser
import requests

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

NEWS_DIR = Path("news")

REDDIT_SUBREDDITS = [
    "LocalLLaMA",
    "MachineLearning",
    "ClaudeAI",
    "artificial",
    "singularity",
    "ExperiencedDevs",
]

# Multiple HN queries to cover the topic space; results are deduplicated by ID.
HN_QUERIES = [
    "Claude AI engineering",
    "LLM agent workflow",
    "AI coding assistant",
    "model context protocol MCP",
    "Anthropic",
    "AI software architecture",
    "multimodal model",
    "AI code review",
]

RSS_FEEDS = {
    "Simon Willison": "https://simonwillison.net/atom/everything/",
    "LessWrong": "https://www.lesswrong.com/feed.xml",
    "Latent Space": "https://www.latent.space/feed",
    "The Gradient": "https://thegradient.pub/rss/",
    "Interconnects": "https://www.interconnects.ai/feed",
    # Reddit RSS avoids the JSON API 403 blocks while still providing
    # practitioner-level signal unavailable from other configured sources.
    "r/LocalLLaMA": "https://www.reddit.com/r/LocalLLaMA/.rss",
    "r/ClaudeAI": "https://www.reddit.com/r/ClaudeAI/.rss",
}

# Topics for GitHub repository search (unauthenticated: 60 req/hour).
GITHUB_TOPICS = [
    "llm",
    "ai-agent",
    "mcp-server",
    "claude",
    "prompt-engineering",
    "rag",
]

HTTP_HEADERS = {
    "User-Agent": "digest-bot/1.0 (AI research digest; non-commercial)",
}

HN_MIN_SCORE = 10       # Minimum HN points to include a story
REDDIT_MIN_SCORE = 5    # Minimum Reddit upvotes to include a post

# ---------------------------------------------------------------------------
# Date utilities
# ---------------------------------------------------------------------------


def find_last_digest_date() -> datetime:
    """
    Return the date of the most recently written digest by reading front matter.

    Falls back to 24 hours ago if news/ does not exist or contains no dated files.
    """
    if not NEWS_DIR.exists():
        return datetime.now(timezone.utc) - timedelta(hours=24)

    latest: datetime | None = None
    for md_file in sorted(NEWS_DIR.glob("*.md"), reverse=True):
        try:
            content = md_file.read_text(encoding="utf-8")
            m = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
            if not m:
                continue
            for line in m.group(1).splitlines():
                if line.strip().startswith("date:"):
                    raw = line.split(":", 1)[1].strip().strip("\"'")
                    dt = datetime.fromisoformat(raw)
                    if dt.tzinfo is None:
                        dt = dt.replace(tzinfo=timezone.utc)
                    if latest is None or dt > latest:
                        latest = dt
                    break
        except Exception:
            continue

    return latest or datetime.now(timezone.utc) - timedelta(hours=24)


def parse_since_arg(value: str) -> datetime:
    """
    Parse the --since argument.

    Accepts YYYY-MM-DD or any ISO 8601 datetime string.
    Exits with an error message on invalid input.
    """
    try:
        dt = datetime.fromisoformat(value)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except ValueError:
        print(
            f"Error: --since value '{value}' is not a valid date. Use YYYY-MM-DD.",
            file=sys.stderr,
        )
        sys.exit(1)


# ---------------------------------------------------------------------------
# Source fetchers
# ---------------------------------------------------------------------------


def fetch_hn(since_dt: datetime) -> list[dict]:
    """
    Fetch Hacker News stories via the Algolia search API.

    Runs multiple topic queries and deduplicates results by story ID, keeping
    the highest-scoring entry when a story appears in multiple query results.
    """
    since_ts = int(since_dt.timestamp())
    seen: dict[str, dict] = {}

    for query in HN_QUERIES:
        url = (
            "https://hn.algolia.com/api/v1/search"
            f"?tags=story"
            f"&query={requests.utils.quote(query)}"
            f"&numericFilters=created_at_i>{since_ts}"
            "&hitsPerPage=20"
        )
        try:
            resp = requests.get(url, headers=HTTP_HEADERS, timeout=10)
            resp.raise_for_status()
            for hit in resp.json().get("hits", []):
                points = hit.get("points", 0) or 0
                if points < HN_MIN_SCORE:
                    continue
                oid = hit["objectID"]
                if oid not in seen or points > seen[oid]["score"]:
                    seen[oid] = {
                        "title": hit.get("title", ""),
                        "url": (
                            hit.get("url")
                            or f"https://news.ycombinator.com/item?id={oid}"
                        ),
                        "date": hit.get("created_at", ""),
                        "source": "Hacker News",
                        "score": points,
                        "comments": hit.get("num_comments", 0) or 0,
                        "snippet": "",
                    }
        except Exception as exc:
            print(f"  Warning: HN query '{query}' failed: {exc}", file=sys.stderr)
        time.sleep(0.15)

    return list(seen.values())


def fetch_reddit(since_dt: datetime) -> list[dict]:
    """
    Fetch recent posts from configured subreddits using the public JSON API.

    Fetches the 100 newest posts per subreddit and filters by date and score
    client-side (Reddit's public API does not support server-side date filtering).
    """
    since_ts = since_dt.timestamp()
    items: list[dict] = []

    for sub in REDDIT_SUBREDDITS:
        url = f"https://www.reddit.com/r/{sub}/new.json?limit=100"
        try:
            resp = requests.get(url, headers=HTTP_HEADERS, timeout=10)
            resp.raise_for_status()
            for post in resp.json().get("data", {}).get("children", []):
                d = post.get("data", {})
                if d.get("created_utc", 0) < since_ts:
                    continue
                if (d.get("score", 0) or 0) < REDDIT_MIN_SCORE:
                    continue
                items.append({
                    "title": d.get("title", ""),
                    "url": d.get("url", ""),
                    "date": datetime.fromtimestamp(
                        d["created_utc"], tz=timezone.utc
                    ).isoformat(),
                    "source": f"r/{sub}",
                    "score": d.get("score", 0) or 0,
                    "comments": d.get("num_comments", 0) or 0,
                    "snippet": (d.get("selftext") or "")[:400],
                })
        except Exception as exc:
            print(f"  Warning: r/{sub} fetch failed: {exc}", file=sys.stderr)
        time.sleep(0.5)

    return items


def fetch_rss(since_dt: datetime) -> list[dict]:
    """
    Fetch entries from configured RSS/Atom feeds published after since_dt.
    """
    items: list[dict] = []

    for feed_name, feed_url in RSS_FEEDS.items():
        try:
            parsed = feedparser.parse(feed_url)
            for entry in parsed.entries:
                pub = entry.get("published_parsed") or entry.get("updated_parsed")
                if pub is None:
                    continue
                entry_dt = datetime(*pub[:6], tzinfo=timezone.utc)
                if entry_dt <= since_dt:
                    continue
                raw_snippet = entry.get("summary", "") or ""
                snippet = re.sub(r"<[^>]+>", "", raw_snippet)[:400].strip()
                items.append({
                    "title": entry.get("title", ""),
                    "url": entry.get("link", ""),
                    "date": entry_dt.isoformat(),
                    "source": feed_name,
                    "score": 0,
                    "comments": 0,
                    "snippet": snippet,
                })
        except Exception as exc:
            print(f"  Warning: RSS feed '{feed_name}' failed: {exc}", file=sys.stderr)

    return items


def fetch_github(since_dt: datetime) -> list[dict]:
    """
    Fetch recently pushed AI-related repositories from the GitHub Search API.

    Uses unauthenticated requests (60 req/hour limit). Deduplicates by full
    repository name across topic queries.
    """
    since_date = since_dt.strftime("%Y-%m-%d")
    seen: dict[str, dict] = {}

    for topic in GITHUB_TOPICS:
        url = (
            "https://api.github.com/search/repositories"
            f"?q=topic:{topic}+pushed:>{since_date}"
            "&sort=stars&order=desc&per_page=5"
        )
        try:
            resp = requests.get(
                url,
                headers={**HTTP_HEADERS, "Accept": "application/vnd.github.v3+json"},
                timeout=10,
            )
            resp.raise_for_status()
            for repo in resp.json().get("items", []):
                name = repo["full_name"]
                if name in seen:
                    continue
                desc = repo.get("description") or ""
                seen[name] = {
                    "title": f"{name}: {desc}".rstrip(": "),
                    "url": repo["html_url"],
                    "date": repo.get("pushed_at", ""),
                    "source": "GitHub",
                    "score": repo.get("stargazers_count", 0) or 0,
                    "comments": 0,
                    "snippet": desc,
                }
        except Exception as exc:
            print(f"  Warning: GitHub topic '{topic}' failed: {exc}", file=sys.stderr)
        time.sleep(1.2)  # Stay well under the unauthenticated rate limit

    return list(seen.values())


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Fetch AI tool news from free public sources. "
            "Outputs JSON to stdout; progress to stderr."
        )
    )
    parser.add_argument(
        "--since",
        metavar="YYYY-MM-DD",
        help=(
            "Fetch items published after this date (ISO 8601). "
            "Defaults to the date of the most recent file in news/."
        ),
    )
    args = parser.parse_args()

    since_dt = parse_since_arg(args.since) if args.since else find_last_digest_date()
    fetched_at = datetime.now(timezone.utc)

    print(f"Fetching since: {since_dt.strftime('%Y-%m-%d %H:%M UTC')}", file=sys.stderr)

    fetchers = [
        ("Hacker News", fetch_hn),
        ("Reddit", fetch_reddit),
        ("RSS Feeds", fetch_rss),
        ("GitHub", fetch_github),
    ]

    sources_attempted: list[str] = []
    sources_succeeded: list[str] = []
    all_items: list[dict] = []

    for source_name, fetcher in fetchers:
        sources_attempted.append(source_name)
        print(f"Fetching {source_name}...", file=sys.stderr)
        try:
            items = fetcher(since_dt)
            all_items.extend(items)
            sources_succeeded.append(source_name)
            print(f"  {len(items)} items", file=sys.stderr)
        except Exception as exc:
            print(f"  Failed: {exc}", file=sys.stderr)

    print(
        f"\nDone: {len(all_items)} total items from {len(sources_succeeded)} sources",
        file=sys.stderr,
    )

    output = {
        "fetched_at": fetched_at.isoformat(),
        "since": since_dt.isoformat(),
        "sources_attempted": sources_attempted,
        "sources_succeeded": sources_succeeded,
        "item_count": len(all_items),
        "items": sorted(all_items, key=lambda x: x.get("date", ""), reverse=True),
    }

    # Write via the binary buffer to bypass Windows cp1252 stdout encoding.
    output_bytes = json.dumps(output, indent=2, ensure_ascii=False).encode("utf-8")
    sys.stdout.buffer.write(output_bytes)
    sys.stdout.buffer.write(b"\n")
    sys.stdout.buffer.flush()


if __name__ == "__main__":
    main()
