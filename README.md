# Marketing Minder

Marketing Minder is a set of agent skills that act as a marketing advisor for a small business. Each skill is one plain `SKILL.md` file, and the business modules read one shared brand file per business, so the agent stops planning every marketing task from scratch. It works with Claude, ChatGPT, Codex, Antigravity and other agents that can read `SKILL.md` files and a local folder.

LinkedIn Amplifier keeps account-scoped network data and can run without a brand file. Marketing Manager can also pass it a business audience, voice and campaign goal, then retain a concise dated research summary in `brands/<business>/linkedin-research.md`. Raw network/contact data stays under `temp/<account>/`.

Keep the whole repository available to your agent, and run helper commands from its root: the skills reference sibling modules and `scripts/`. Copying only one `SKILL.md` does not install those dependencies. No package installation is needed for the Python helpers.

The agent drafts and advises. You post, publish and change your own site. Everything it knows about your business sits in Markdown files on your machine that you can open and edit.

## Modules

| Module | What it does | Status |
|---|---|---|
| [Marketing manager](skills/marketing-manager/SKILL.md) | Reads your website and keeps your brand, ideal customer and offer in `brands/<business>/brand.md`. Start here. | Available |
| [Market fit](skills/market-fit/SKILL.md) | Reviews your value proposition, home page copy, bundles and pricing against the brand file. | Available |
| [LinkedIn Amplifier](skills/linkedin-amplifier/SKILL.md) | Finds experts and conversations worth joining in your first-degree LinkedIn network. | Available |
| [Event minder](skills/event-minder/SKILL.md) | Plans and audits launches, product drops, seasonal campaigns, and optional contests/giveaways as phased campaigns with checklists in `brands/<business>/events/<YYYY-MM-DD>-<event-slug>.md`. | Available |
| SaaS solopreneur recipe | Growth playbook across Product Hunt, Reddit, X, TikTok, LinkedIn and Instagram. | Planned |
| [E-commerce recipe](recipes/ecommerce.md) | Reviews Shopify or WooCommerce store pages, checkout, offers and small-store channels, including print-on-demand. | Available |
| [Results review](skills/results-review/SKILL.md) | Compares two periods of site, social and store results from CSV or a read-only connector and proposes next steps. | Available |
| [Weekly plan](skills/weekly-plan/SKILL.md) | Drafts a Monday–Sunday action plan, carries unfinished work forward and builds toward upcoming events. | Available |
| [Grok Bot content drafts](integrations/grok-bot/SKILL.md) | Drafts X, LinkedIn and Instagram posts from the brand file and active event files, and queues them for approval. | Available |

## Start with the brand file

Point your agent at this folder and ask:

> Use the marketing manager skill to read example.com and create its brand file.

Have a browser session open for the agent: its integrated browser, or a tab you opened for it. Many stores block scripted requests to product pages, so the agent reads through the browser and falls back to a plain fetch only when no browser is available.

The agent reads your public pages and writes `brands/example/brand.md`. Every statement in it is marked as read from the site, told by you, a guess, or unknown, so a guessed customer profile is never read as fact. Correct the guesses, then ask for the next module:

> Use the market fit skill on example.

After the first write, the brand file changes only when you accept a change, and each accepted change is dated in its change log.

## LinkedIn Amplifier

LinkedIn Amplifier finds people in your first-degree network who consistently start useful discussions in your field. It builds a watchlist by topic and suggests fresh posts where you have something specific to contribute.

### Who's this for

Professionals who want to find peers and subject matter experts in their existing LinkedIn network, follow conversations in their field, and contribute from firsthand experience.

### Use cases

- **Find experts by topic.** Build a watchlist of direct connections whose posts regularly draw substantive questions, examples, and replies.
- **Find conversations to join.** Get up to three recent posts with a suggested angle grounded in your experience.
- **Inventory your network.** Import your LinkedIn connections export and prioritize profiles for browser inspection.
- **Follow up on your comments.** Track replies and visible impressions to see which conversations led to further discussion.

The reusable instructions live in [SKILL.md](skills/linkedin-amplifier/SKILL.md). Point your agent at that file and ask it to use your signed-in Chromium session or your open LinkedIn tab.

> Use the LinkedIn Amplifier skill to find first-degree connections who start substantive discussions about AI coding agents and product design. Give me a watchlist and three recent posts where I could add something from my own experience.

The first pass can reuse an existing network scan and sample 15–20 connections. It compares recent original posts, counts distinct people who participate, and looks for follow-up questions, examples, and exchanges between peers. Author replies and follower counts provide separate context. Post suggestions include evidence links and a concrete comment angle for you to review and post.

The skill also supports visible connection counts and follow-up on comments you post. It preserves capped counts such as “500+,” marks incomplete threads, and reports profile-view trends separately from observable replies and impressions.

Browser runs use one tab, space content-loading actions at least 15 seconds apart, and checkpoint after at most 30 such actions. The skill stops if LinkedIn shows a rate limit, verification prompt, or restriction.

To continue a scan, ask the agent to resume from its saved checkpoint (`temp/<account>/checkpoint.json`). It verifies the signed-in account and skips profiles and posts it has already inspected, saving structured outputs (`connections.csv`, `watchlist.csv`, `posts.csv`, `opportunities.csv`, and `outcomes.csv`) in the gitignored `temp/<account>/` directory.

### Start with your LinkedIn export

In LinkedIn, go to **Me → Settings & Privacy → Data Privacy → Download your data** (also labeled **Get a copy of your data**). Request the archive that includes connections, download it, and extract `Connections.csv`. LinkedIn includes email addresses according to each connection's export privacy settings. [LinkedIn export instructions](https://www.linkedin.com/help/recruiter/answer/a566336)

From the repository root, run:

```sh
python3 scripts/import_linkedin_export.py --account your-profile-slug "/path/to/Connections.csv"
```

Use the export owner's profile slug, the part after `/in/` in their profile URL. The importer reads the extracted English-header CSV, including its optional notes and UTF-8 BOM. It reports skipped rows with missing or invalid profile links and seeds `temp/<account>/connections.csv` without browser visits. Reimporting fills missing values and preserves existing nonblank data, including follower counts. Company, position, and connection date remain in the original export. Imported profiles are candidates for browser inspection.

### Inventory your full network

Start the first batch overnight if convenient. Keep the signed-in browser available and ask Codex to use the skill with this prompt:

> Inventory my entire first-degree LinkedIn network. Save each completed profile locally and stop at the browsing limit. Resume from the same checkpoint when I ask for the next batch.

Plan to resume in batches over several days or longer for a large network. Each run keeps the 30-action limit and 15-second spacing, even overnight. Stop when LinkedIn presents a warning or checkpoint. These limits manage browsing volume.

Python 3.8+ on macOS or Linux saves one CSV row per canonical profile URL in `temp/<account>/connections.csv`. The columns are name, LinkedIn permalink, email visible under Contact info, and follower count. Missing values stay blank. The directory is created on first save and Git ignores its contents.

```sh
python3 scripts/save_connections.py --account your-profile-slug < /path/to/observations.jsonl
```

Each input line is a JSON object with keys `name`, `linkedin_permalink`, `email`, and `followers`. Replaying observations produces the same rows. A new nonblank value updates the corresponding field and a blank observation preserves the last known value.

### Plan a browser batch

```sh
python3 scripts/browser_queue.py status --account your-profile-slug
python3 scripts/browser_queue.py next-batch --account your-profile-slug \
  --actions-used 2 --actions-per-profile 4 \
  --priority-url https://www.linkedin.com/in/topic-match/
```

Both commands return JSON. Status separates inventory rows awaiting inspection from profiles marked inspected or inaccessible in the checkpoint. Inventory rows can come from an export or browser observation. The CSV has no source column. The queue also includes pending URLs from the checkpoint.

Pass repeatable `--priority-url` flags in preference order for people with evidence of topic fit, such as a relevant role in the original export or a post you've already seen. The CLI fills the rest of the batch in permalink order. It defaults to 30 actions per run and reserves four per profile. Set the cost for your workflow and pass actions already used in the current run. Continue enforcing the actual action cap while browsing. A saved blocker yields an empty batch until resolved.

## Grok Bot content drafts

[Grok Bot content drafts](integrations/grok-bot/SKILL.md) turns the brand file, and any Event Minder files under `brands/<business>/events/`, into a week of X, LinkedIn and Instagram drafts. A routine can run that draft on a schedule. You approve and publish. The queue is files you can open, not a setup that lives only inside one bot account.

The skill, platform rules and routine prompts are in [`integrations/grok-bot/`](integrations/grok-bot/README.md). `scripts/content_queue.py` reads the brand file, schedules from the target date written inside each event file, checks platform limits, and exports a Buffer CSV, a Postiz draft file, and an X drafts file. The queue lands in gitignored `brands/<business>/content/`.

```sh
python3 scripts/content_queue.py calendar --business example --week 2026-11-16 --timezone America/Los_Angeles
python3 scripts/content_queue.py validate --business example
python3 scripts/content_queue.py export --business example --format all
```

Install steps, the Monday and weekday schedules, and the optional Postiz draft command are in the [setup notes](integrations/grok-bot/README.md). The planned SaaS solopreneur recipe still covers Product Hunt, Reddit and TikTok. This module is the draft queue for X, LinkedIn and Instagram.

## Your data and backups

Your business data stays on your machine, in two gitignored folders: `brands/<business>/` for each company you work on (for example `brands/mangajdm/`) and `temp/<account>/` for LinkedIn network data. Git does not track either folder, so cloning, pushing or pulling this repository never saves or restores them.

**Back these folders up yourself.** Use Time Machine or another backup system that covers the repository folder. If the folder is deleted, overwritten or lost with the machine, a backup is the only way to get the files back.

This software is provided "as is", without warranty of any kind, under the terms of the [license](LICENSE). The authors are not responsible for your data, including its loss, its accuracy, or where you store, share or publish it. If you fork this repository, keep `brands/` and `temp/` in `.gitignore` so private business data is not pushed.

## Local verification

Run `python3 -B -m unittest discover -s tests` from the repository root. Tests use synthetic data; no LinkedIn session or API key is needed. This checks the Python helpers, not live platform behavior or marketing outcomes.

See the [changelog](CHANGELOG.md) for changes to the skills.
