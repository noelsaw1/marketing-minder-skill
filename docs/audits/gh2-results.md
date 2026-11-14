# GH-2 QA results — 2026-11-14

Issue: https://github.com/noelsaw1/marketing-minder-skill/issues/2
Implementation tested: f9ea49edcbb68c65bdd65fda859288b31b392a0b.
Base: 3c8c2e6661651d8f7c4086fe0e9d34f1aac8add4. Tests used local Python 3.14 and synthetic data, without network or account access. No claim of a Python 3.8 runtime run.

## Audit coverage and dispositions

| Surface | Finding / disposition |
|---|---|
| README | F3 fixed: business modules share brand state; LinkedIn is account-scoped; whole-repo dependencies and verification documented. |
| marketing-manager | F3 fixed: identity check before folder reuse, bounded slug, source-owned updates, contextual contact/date checks, complete-catalog prerequisite for absence claims. Existing accepted-change protocol retained. |
| market-fit | F3 fixed: direct invocation inherits identity/privacy checks. Existing provenance, ranked suggestions and historical runs retained. |
| event-minder (handoff) | F2 fixed: all nine checklist categories, three intake questions, phased campaign with owners, optional default giveaways, evidence-separated checks, per-event history. |
| linkedin-amplifier | F1 documented: existing checkpoint requires account; verified repair only. Existing pacing/action cap and manual posting preserved. |
| save_connections.py | P3 fixed: credentials in a profile URL rejected. Existing normalization, file lock, atomic CSV writer preserved. |
| browser_queue.py | F1 fixed: unowned/malformed/mismatched existing checkpoints rejected; absent checkpoint is valid fresh start. |
| import_linkedin_export.py | No implementation change needed; synthetic duplicate/replay and malformed-input checks added. |
| tests | Five baseline tests passed. Added three focused workflow tests and two URL rejection subcases, no framework/dependency. |
| Ahrefs recipe | F4 fixed: unsafe snippet removed; explicit manifest preparation/validation requirements, dated observations and user-owned secrets/activation. No live connector validation claimed. |
| CHANGELOG | Corrected converter success claim; recorded shipped behavior changes. |
| .gitignore | brands/temp ignored, unchanged. |
| LICENSE | GPL v3 text retained unchanged; no licensing determination part of this audit. |

All product files were inspected. Graph/source evidence and excluded private/cache/tool state are recorded in the plan. This is a bounded source/workflow audit, not proof of absence of all defects. No production servers, business files, LinkedIn sessions, API credentials or campaign accounts were accessed.

## Deterministic checks

- `python3 -B -m unittest discover -s tests -v`: **8 passed**, including absent, unowned, wrong, malformed and matching checkpoint identity; queue budget/blocker/completion; duplicate import and replay preserving enrichment.
- Red control: copied the three `origin/main` scripts into a temporary fixture tree with the new test files, then ran the same unittest discovery. **Exit 1: 4 failed subcases, 2 errors**. Missing account was accepted twice; credential URLs accepted twice; non-string account caused AttributeError rather than the required ValueError. Therefore unchanged code cannot satisfy the new assertions.
- All four skill folders passed skill-creator `quick_validate.py` (frontmatter/structure only, not behavior).
- `git diff --check`: pass. Product Markdown relative-link check: 7 links, none missing. `git check-ignore brands/ temp/`: both ignored.
- Recipe red controls (source-only extraction of its old function definitions): `sanitize({'type':'integer','enum':list(range(51))})` became `{'type':'string','example':'us'}`; absent selected endpoint yielded `{}`; external ref extraction yielded `set()`. These are why removal is preferable to a claimed general converter.

## CLI smoke — disposable full clone

Full independent Git clone of tested task commit, local origin pointing to task clone; HEAD verified before/after as f9ea49e. No linked worktree or live data. `git status --short` empty after exact synthetic files were removed. Required evidence is this receipt; helper retained pending cleanup safety checks.

Commands (all `python3 -B scripts/<name>.py`):

1. `--help` for save_connections, import_linkedin_export and browser_queue: exit 0.
2. Import a temporary English-header CSV with Alice Example, `https://linkedin.com/in/alice/`, `alice@example.com`, using `--account qa-synthetic`: exit 0; one unique profile.
3. Save JSONL `{"linkedin_permalink":"https://linkedin.com/in/alice/","followers":"42"}`: exit 0; still one row.
4. Reimport same CSV: exit 0; connections.csv byte-identical, follower enrichment retained.
5. Queue `status --account qa-synthetic`: inventory=1, pending=1.
6. `next-batch --account qa-synthetic --actions-used 26`: remaining_actions=4, estimated_actions=4, one profile.
7. Existing checkpoint `{}`: `status` exit 1, `Queue failed: Checkpoint does not belong to the requested account`.
8. Checkpoint with account `qa-synthetic` and Alice inspected: `next-batch` exit 0, inspected=1, pending=0, profiles=[].
9. Full unittest discovery in helper: eight passed.

Main path, replay and resume/rejection checks **PASS**. No emails, profile visits or external requests occurred.

## Instruction walkthroughs (author, not independent behavioral testing)

Read from README -> marketing-manager -> Event Minder and its referenced rules.

**New launch:** synthetic `example.com` business, requested store launch, date unknown, owner has GA tag evidence but no property access; giveaway decision unanswered. The resulting plan specification has event ID, timezone/date/owners TBD, preparation/launch/review phases and all nine rows: HTML, SEO, favicon, GSC, Analytics, social profile creation, LinkedIn, Product Hunt, contests/giveaways. Observed tag can pass its narrow criterion; GSC ownership/submission and GA collection remain UNCHECKED. Giveaway is recommended/pending. No invented founder story/code, no forced channel creation, no publication. This follows Start from the business, Readiness checklist and Write the plan.

**Adjacent seasonal event:** existing launch has historical PASS and completed announcements; new holiday sale has a distinct ID and owner declines giveaway. New section goes above preserved launch history, current site checks begin UNCHECKED until observed, giveaway is N/A/declined. Existing social accounts are reviewed, not recreated; Product Hunt can be N/A with reason. Offer/date-specific drafts and shipping cut-off milestones replace the first-launch story. Same-event rerun keeps completed actions and appends/rechecks dated evidence. No old PASS represents new verification.

**Identity and consistency:** existing `brands/example/brand.md` identifies example.com, request names example.net. Manager must resolve whether same business before reuse; distinct business uses e.g. example-net. Two sampled products cannot prove a policy's product category absent. Different email domain or old policy date alone produces no defect. Direct market-fit/Event Minder invocation inherits identity and ignored-output checks.

**Recipe:** consumer follows current docs -> select required GETs -> prepare compatible manifest -> validate endpoints/references/security/schema/actual bytes -> preview -> user activation. Missing endpoint/unresolved ref stops preparation. No converter success or live connection claim survives. Official Ahrefs API/MCP and OpenAPI documents were read on 2026-11-14; public docs support the procedure, not account-specific verification.

## Decisions and limitations

Operator confirmed phased campaign plus checklist and default optional giveaway. Plan QA approved in `gh2-plan-relay.md`; all findings were in reviewed scope. No extra architecture or automated conversion utility added. Live browser flows, hosted checks (none configured), marketing outcomes, legal/platform eligibility and the connector's current UI limits remain unverified.

Edit verdicts: account validation **helped** (red/green controls); URL input rejection **helped** (red/green); Event Minder, shared instructions and recipe **confounded** for real-world outcomes (author walkthrough/source evidence only). Lessons writer: **NO_ENTRY**; fixes/receipts suffice and no repository lessons system exists. Rating unchanged at 65/50/50/65, recurrence unknown.

## Independent review closeout

Plan and final Codex relay reviews both returned PASS/Approved with exit 0 and harness attestations. Final reviewed head c8b052f; subsequent commits contain only review/publication documentation, no product changes. Final reviewer independently probed checkpoint identity and URL controls; complete suite/CLI results remain producer evidence. See `gh2-final-relay.md` for full scope and limits.
