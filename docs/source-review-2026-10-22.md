# Source review — 22 October 2026

Purpose: refocus the digest from model and inference news toward how technology organisations adopt, adapt and learn with AI: practices, org structures and careers, adjacent disciplines (product, project, delivery), and regulatory and business risk.

## 1. What the current sources actually produce

Yield over the last 10 digests (14 Sep – 22 Oct 2026). "Retention" is the share of fetched items that survived the signal filter.

| Source | Retained | Excluded | Retention | Avg signal | Assessment |
|---|---|---|---|---|---|
| Pragmatic Engineer (blog) | 6 | 1 | 86% | 6.5 | Best fit for the new focus; low volume because the blog feed is the delayed free version |
| Interconnects | 8 | 3 | 73% | 5.5 | High retention, but open-model and policy commentary, not org practice |
| Latent Space | 47 | 19 | 71% | 6.5 | Strongest single source; the AINews issues carry most model news, the podcasts carry practice |
| LangChain Blog | 31 | 25 | 55% | 6.2 | Vendor, but consistently publishes measured case studies and harness data |
| Simon Willison | 50 | 99 | 34% | 6.2 | High value per retained item; two-thirds of volume is releases, wildlife and link posts |
| Hacker News | 37 | 112 | 25% | 5.9 | Queries are model/tool shaped; retained items were mostly Anthropic business and incident stories |
| r/LocalLLaMA | 56 | 187 | 23% | 5.5 | Dominates volume; almost entirely inference hardware and quantisation, off the new focus |
| LessWrong | 18 | 79 | 19% | 5.6 | Full firehose; most posts are philosophy, meetups or alignment theory |
| GitHub | 19 | 210 | 8% | 6.2 | Same 20 perennial repositories every run; the three genuine breakouts (rea, ponytail, Whiteboard) all came via HN first |
| r/ClaudeAI (RSS) | 0 | 0 | — | — | Feed works but contributed nothing in 10 runs; threads are support and incident chatter |
| The Gradient | 0 | 0 | — | — | No post since 18 Feb 2026 |
| Chip Huyen | 0 | 0 | — | — | No post since 16 Jan 2025 |
| Reddit JSON API (6 subreddits) | 0 | 0 | — | — | HTTP 403 on every run since at least 14 Sep |

Tag mix of retained items over the same runs: LLM Models 65, Agent Engineering 63, Local Inference 56, Tools 52, Security 50, Evaluation 49, Performance 46, AI-Assisted Dev 44, AI Management 42. Local Inference plus Performance plus LLM Models account for about a third of everything retained; organisational and career content appears only when Anthropic or Pragmatic Engineer publish it.

Conclusion: the current source set is built for a model-and-tooling digest. It has no dedicated coverage of engineering management, product management, developer-experience research, regulation, or company-level adoption stories, and two feeds are dead.

## 2. Candidate sources checked

Every candidate feed was fetched and parsed on 22 Oct 2026. "Last 45d" is the number of entries dated in the previous 45 days.

### Engineering leadership and organisational practice

| Source | Feed | Last 45d | Verdict |
|---|---|---|---|
| Pragmatic Engineer Newsletter (Substack) | newsletter.pragmaticengineer.com/feed | 19 | **Add.** Titles and summaries of the paid issues ("What's the ROI of software engineers' spending on AI?", "The revised rules of engineering management"). Keep the blog feed for the free full-text versions |
| LeadDev | leaddev.com/rss.xml | 10 | **Add.** Engineering management with AI-impact reporting ("Engineers lose 17+ days a year to AI rework") |
| Engineering Enablement (DX, Abi Noda) | newsletter.getdx.com/feed | 10 | **Add.** Quarterly AI-impact data across 500+ teams; the only developer-experience research publisher with a working feed |
| Irrational Exuberance (Will Larson) | lethain.com/feeds/ | 2 | **Add.** Low volume, very high signal on org design under agents |
| charity.wtf (Charity Majors) | charity.wtf/feed/ | 3 | **Add.** Team norms and operations under AI |
| Martin Fowler | martinfowler.com/feed.atom | 17 | **Add.** Thoughtworks practice writing; "Fragments" posts are short link roundups |
| Thoughtworks Insights | thoughtworks.com/rss/insights.xml | 33 | **Add, expect noise.** Consultancy content, but current titles are squarely on-theme ("Why executive judgment decides who wins with AI") |
| MIT Sloan Management Review | sloanreview.mit.edu/feed/ | 18 | **Add.** Management research on AI adoption and responsible AI |
| Kent Beck, Tidy First | tidyfirst.substack.com/feed | 6 | **Add.** Craft under agents |
| Addy Osmani (Substack) | addyo.substack.com/feed | 3 | **Add.** Agentic engineering practice from inside the Claude Code team |
| Elite AI Assisted Coding | elite-ai-assisted-coding.dev/feed | 4 | **Add.** Practitioner case studies ("How Warp builds Warp") |
| Steve Yegge | steve-yegge.medium.com/feed | 0 | Skip; dormant since August |
| Faros AI blog | faros.ai/blog/rss.xml | 100 | Skip; vendor content farm cadence |

### Product, delivery and adjacent disciplines

| Source | Feed | Last 45d | Verdict |
|---|---|---|---|
| Lenny's Newsletter | lennysnewsletter.com/feed | 20 | **Add.** AI is now about two-thirds of its output; the "How I AI" series is directly about adjacent-role adoption |
| SVPG (Marty Cagan) | svpg.com/feed/ | 4 | **Add.** Product operating model and AI ("Experimentation, AI and the Product Model") |
| The Beautiful Mess (John Cutler) | cutlefish.substack.com/feed | 8 | **Add.** Product and organisational systems |
| Reforge blog | reforge.com/blog/rss.xml | — | Skip; feed returns HTTP 500 |
| Atlassian Work Life | atlassian.com/blog/rss | 5 | Skip; current feed is Bitbucket product announcements. Atlassian's State of Developer Experience report is annual and reaches HN |

### Company engineering blogs with adoption stories

| Source | Feed | Last 45d | Verdict |
|---|---|---|---|
| Zalando Engineering | engineering.zalando.com/atom.xml | 3 | **Add.** "Agentic Engineering at Zalando: a snapshot" is the model for the kind of post we want |
| Spotify Engineering | engineering.atspotify.com/feed/ | 4 | **Add.** "AI Changed How Spotify Builds. What We Learned (and Fixed)" |
| Shopify Engineering | shopify.engineering/blog.atom | 7 | **Add.** Open-model specialisation and platform posts |
| GitHub Blog | github.blog/feed/ | 10 | **Add, low priority.** Copilot marketing mixed with Octoverse data and infrastructure posts ("agent-scale Git infrastructure") |
| Netflix TechBlog | netflixtechblog.com/feed | 10 | Skip; ML infrastructure rather than organisational adoption |
| Anthropic Engineering / News | — | — | No RSS feed exists; keep the HN "Anthropic" query |
| OpenAI News | openai.com/news/rss.xml | 106 | Skip; marketing volume, and major items reach HN |
| Monzo, Booking.com, Figma, Cursor | — | — | No working feeds found |

### Industry news and research

| Source | Feed | Last 45d | Verdict |
|---|---|---|---|
| InfoQ AI/ML | feed.infoq.com/ai-ml-data-eng/ | 15 | **Add.** Architecture and practice reporting |
| The New Stack | thenewstack.io/feed/ | 26 | **Add, expect noise.** Industry news with a practitioner angle |
| Stack Overflow Blog | stackoverflow.blog/feed/ | 40 | **Add, expect noise.** Annual survey results and developer-sentiment data are core to the new focus; most other posts will be excluded |
| MIT Technology Review AI | technologyreview.com/topic/artificial-intelligence/feed | 10 | **Add.** "The new economics of enterprise AI" |
| METR | metr.org/feed.xml | 10 | **Add.** Rigorous evaluation and productivity research |
| Stanford HAI | — | — | Feed returns no entries |
| HBR | — | — | Feed endpoints fail |

### Regulation, policy and business risk

| Source | Feed | Last 45d | Verdict |
|---|---|---|---|
| Luiza's Newsletter | luizasnewsletter.com/feed | 16 | **Add.** EU AI Act and governance for practitioners ("The EU's First AI Standard Is Here") |
| Import AI (Jack Clark) | importai.substack.com/feed | 6 | **Add.** Policy and capability strategy for leaders |
| AI Policy Perspectives | aipolicyperspectives.com/feed | 5 | **Add, low priority.** Research-adjacent policy |
| Platformer | platformer.news/rss/ | 13 | **Add, low priority.** Tech policy and platform business news; AI share varies |
| One Useful Thing (Ethan Mollick) | oneusefulthing.org/feed | 3 | **Add.** Adoption practice for non-engineering leaders |
| Tech Policy Press | — | — | Feed returns no entries |

## 3. Recommended changes to the fetcher

Applied to `scripts/fetch_digest.py` on 22 Oct 2026:

- **Remove** The Gradient and Chip Huyen (dead feeds).
- **Replace** the LessWrong firehose with the karma-filtered community feed (`karmaThreshold=30`), which keeps the research posts and drops meetups and essays.
- **Keep** r/LocalLLaMA RSS but treat it as the hardware-and-inference tail; it returned HTTP 429 during this review and will be intermittent. **Remove** r/ClaudeAI (zero yield in 10 runs).
- **Disable** the Reddit JSON API fetcher; it has returned 403 on every subreddit since September. The function stays in the script so it can be re-enabled.
- **Add** 28 feeds listed above, grouped in the config by theme.
- **Rebalance Hacker News queries** toward the new focus: engineering management, product management, careers and hiring, regulation, productivity studies, enterprise adoption; drop "multimodal model".
- **Change the GitHub search** from "topic + pushed since" (which returns the same perennial repositories every run) to "topic + created in the last 60 days", so it surfaces genuinely new breakouts; cut topics to `ai-agent`, `claude`, `mcp-server`, `developer-tools`.
- **Send a User-Agent** on RSS fetches (feedparser previously sent none), which helps with Reddit and some Substack hosts.

Expected effect: roughly 60–80 extra RSS items per weekly run, mostly from Lenny's, Stack Overflow, The New Stack and Thoughtworks; the signal filter will exclude most of them, but the retained set should shift toward AI Management, AI-Assisted Dev, product and regulation tags.

## 4. Follow-ups (approved and applied 22 Oct 2026)

All four items below were applied the same day: the digest skill's sections and tag vocabulary were replaced, an annual-reports checklist was added as Step 1b of the skill, and CLAUDE.md's mission, research objectives, sources, topics, and high-priority questions were rewritten to match.

1. **Digest sections.** The skill's seven sections are model-and-tooling shaped. Suggested replacement set: Organisations, Roles and Careers; Engineering Practice and Delivery; Product, Project and Adjacent Disciplines; Regulation, Risk and Governance; Models and Platforms (merged Claude/Anthropic and LLM Models); Agent Engineering; Tools and Infrastructure.
2. **Tag vocabulary.** Add "Product Management", "Careers", "Regulation" and "Org Design" as first-class tags so trends on the new focus can be measured; the ledger currently folds all of them into "AI Management".
3. **CLAUDE.md mission.** The "Sources To Monitor" and "Topics To Track" sections still describe the old scope; they should be edited to match this review so future runs score items against the right criteria.
4. **Annual reports.** Stack Overflow Developer Survey, Atlassian State of Developer Experience, DORA, JetBrains State of Developer Ecosystem and Anthropic's Agentic Coding Trends report are not feed-shaped. Add a short checklist to the digest skill to look for them in their publication months (June–October).
