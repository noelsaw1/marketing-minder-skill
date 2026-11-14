# Changelog

## Unreleased

- Added a Codex skill that finds first-degree LinkedIn connections who consistently draw substantive discussion and recommends up to three recent posts to comment on.
- Added an optional workflow for tracking replies, visible comment impressions, and profile-view trends.
- Preserved exact, capped, and unavailable connection counts as separate categories.
- Added single-tab browsing, a minimum of 15 seconds between content loads, a 30-action budget per run, and checkpoints for resuming. The skill stops on rate limits, verification prompts, and account restrictions.
- Added a resumable full-network inventory and a Python CSV writer that deduplicates by profile permalink and saves privately under `temp/`.
- Hardened `scripts/save_connections.py` to normalize percent-encoded/Unicode and regional LinkedIn `/in/` slugs, reject boolean values and encoded path separators, and added a standard-library `unittest` suite in `tests/test_save_connections.py`.
- Standardized deterministic schemas under `temp/<account>/` (`checkpoint.json`, `watchlist.csv`, `posts.csv`, `opportunities.csv`, `outcomes.csv`) and clarified per-run 30-action budget allocation in `SKILL.md`.
- Added a local LinkedIn Connections.csv importer that seeds the inventory while preserving browser enrichment.
- Added browser queue status and topic-prioritized batch planning within the content-load budget.
- Added audience and use cases near the top of the README.
- Added the marketing manager skill, which reads a business's website and keeps its brand, ideal customer and offer in one local Markdown brand file under the gitignored `brands/<business>/` folder, with every statement marked as read from the site, told by the owner, a guess, or unknown.
- Added the market fit skill, which reviews the value proposition, home page copy, bundles and pricing against the brand file, writes ranked suggestions to `brands/<business>/market-fit.md`, and proposes brand file changes for the user to accept.
- Changed site reading to use a browser session first, with a plain fetch as backup and a catalog export as the most reliable source, after a Shopify store blocked scripted requests to product pages. The marketing manager skill now records the page-reading method that worked, the failures seen, and a rule to add new working methods to the skill in the same session.
- Added a method to the marketing manager skill for connecting the user's accounts to another marketing tool: read-only access, stop at the consent screen, and the user approves.
- Added a consistency check to the marketing manager skill: an audit that compares contact details, shipping, returns and refund statements across the site's pages, flags unfinished template text, and reports each difference with both statements quoted.
- Added a whole-catalog reading method to the marketing manager skill: collect product links from the listing pages, then request each product's data from inside the browser tab, five seconds apart, stopping at the first refusal. It read 50 products on a store that had blocked scripted requests.
- Added a method to the marketing manager skill for filling another marketing tool's brand form from the brand file through the user's browser tab, leaving the save to the user.
- Added a recipe and OpenAPI sanitizer for connecting Ahrefs to Insightful Pipe via the generic REST API connector, overcoming manifest size limits, enum caps, and OpenAPI 3.0 compatibility issues.
- Added the event minder skill (`skills/event-minder/SKILL.md`), which plans and audits brand launches, product drops, and seasonal campaigns, verifies technical readiness (HTML tags, SEO, favicon, GSC, GA4), drafts multi-channel launch copy (LinkedIn, ProductHunt, social bios), designs viral product bundle giveaways, and tracks progress in `brands/<business>/launch-plan.md`.
- Rewrote the README to describe Marketing Minder as a set of modules, with the LinkedIn Amplifier as one of them.
