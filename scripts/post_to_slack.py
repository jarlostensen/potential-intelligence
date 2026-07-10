# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "requests>=2.31",
# ]
# ///
"""
Post a composed digest message to Slack.

Reads the message text from a file (or stdin) and delivers it via one of two
mechanisms, chosen automatically:

  1. Bot token  — if SLACK_BOT_TOKEN and a channel are set, posts with
                  chat.postMessage (lets you choose the channel, thread, etc).
  2. Webhook    — else, if SLACK_WEBHOOK_URL is set, posts to that webhook's
                  fixed channel.
  3. Skip       — if neither is configured, prints a warning and exits 0 so the
                  surrounding digest run is NOT treated as failed (the HTML
                  artifact has already been produced).

Credentials are read from the environment first, then from a .env file in the
project root (which is gitignored). Never commit tokens or webhook URLs.

Usage:
    uv run scripts/post_to_slack.py --message-file path/to/message.txt
    uv run scripts/post_to_slack.py --message-file msg.txt --channel "#ai-digest"
    uv run scripts/post_to_slack.py --message-file msg.txt --dry-run
    cat msg.txt | uv run scripts/post_to_slack.py

Exit codes:
    0  posted successfully, OR skipped because no credentials are configured
    1  a delivery was attempted and failed (bad token, HTTP error, Slack error)
    2  usage / input error (e.g. empty message)
"""

import argparse
import json
import os
import sys
from pathlib import Path

import requests

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = PROJECT_ROOT / ".env"
POST_MESSAGE_URL = "https://slack.com/api/chat.postMessage"
TIMEOUT = 20


def log(msg: str) -> None:
    """Progress and diagnostics go to stderr; stdout is reserved for a result line."""
    print(msg, file=sys.stderr, flush=True)


def load_env_file(path: Path) -> None:
    """Populate os.environ from a .env file WITHOUT overriding real env vars."""
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def read_message(args) -> str:
    if args.message_file:
        text = Path(args.message_file).read_text(encoding="utf-8")
    elif not sys.stdin.isatty():
        text = sys.stdin.read()
    else:
        log("ERROR: no --message-file given and nothing piped on stdin.")
        sys.exit(2)
    text = text.strip("\n")
    if not text.strip():
        log("ERROR: message is empty.")
        sys.exit(2)
    return text


def post_via_bot_token(token: str, channel: str, message: str) -> None:
    resp = requests.post(
        POST_MESSAGE_URL,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8",
        },
        json={"channel": channel, "text": message, "unfurl_links": False},
        timeout=TIMEOUT,
    )
    # chat.postMessage always returns HTTP 200; success is in the JSON body.
    try:
        body = resp.json()
    except ValueError:
        log(f"ERROR: Slack returned non-JSON (HTTP {resp.status_code}).")
        sys.exit(1)
    if not body.get("ok"):
        log(f"ERROR: Slack API rejected the message: {body.get('error', 'unknown_error')}")
        # Common causes: not_in_channel (invite the bot), invalid_auth,
        # channel_not_found, missing_scope (needs chat:write).
        sys.exit(1)
    log(f"Posted to Slack channel {channel} via bot token (ts={body.get('ts')}).")
    print(json.dumps({"delivered": True, "method": "bot_token", "channel": channel}))


def post_via_webhook(webhook_url: str, message: str) -> None:
    resp = requests.post(
        webhook_url,
        json={"text": message, "unfurl_links": False},
        timeout=TIMEOUT,
    )
    if resp.status_code != 200 or resp.text.strip().lower() != "ok":
        log(f"ERROR: webhook delivery failed (HTTP {resp.status_code}): {resp.text[:200]}")
        sys.exit(1)
    log("Posted to Slack via incoming webhook.")
    print(json.dumps({"delivered": True, "method": "webhook"}))


def main() -> None:
    parser = argparse.ArgumentParser(description="Post a digest message to Slack.")
    parser.add_argument("--message-file", help="Path to a UTF-8 text file with the message.")
    parser.add_argument("--channel", help="Channel override for bot-token mode (e.g. '#ai-digest').")
    parser.add_argument("--dry-run", action="store_true", help="Resolve config and print what would be sent, but do not post.")
    args = parser.parse_args()

    message = read_message(args)
    load_env_file(ENV_FILE)

    bot_token = os.environ.get("SLACK_BOT_TOKEN", "").strip()
    channel = (args.channel or os.environ.get("SLACK_CHANNEL", "")).strip()
    webhook_url = os.environ.get("SLACK_WEBHOOK_URL", "").strip()

    if bot_token and channel:
        method = "bot_token"
    elif webhook_url:
        method = "webhook"
    else:
        # Graceful skip — not an error. The artifact still exists.
        log("Slack not configured (need SLACK_BOT_TOKEN + SLACK_CHANNEL, or SLACK_WEBHOOK_URL). Skipping post.")
        print(json.dumps({"delivered": False, "reason": "not_configured"}))
        sys.exit(0)

    if args.dry_run:
        target = f"channel {channel}" if method == "bot_token" else "webhook channel"
        log(f"[dry-run] Would post {len(message)} chars via {method} to {target}.")
        print(json.dumps({"delivered": False, "reason": "dry_run", "method": method}))
        sys.exit(0)

    if method == "bot_token":
        post_via_bot_token(bot_token, channel, message)
    else:
        post_via_webhook(webhook_url, message)


if __name__ == "__main__":
    main()
