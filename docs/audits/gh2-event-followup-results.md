# Event Minder follow-up verification

Issue #2 / PR #3. Product revision: 518dc00. Integration base: 5526fba. Prior PR: 6507418. Local verification on 2026-11-14; no real business files, accounts or campaigns accessed.

## Independent plan QA

Fable 5.2 high reviewed d367460: Changes requested, no Blocker, five Should findings. Accepted all: include Results Review/ecommerce readers, check provider preservation and classify decision status, strengthen LinkedIn/account-label rejection controls, make in-file dates authoritative, define legacy precedence. Dispositions and amended plan committed in aca88ef.

Separate Fable 5.2 high review of aca88ef: Approved, no Blocker/Should. Pre-read was limited to the plan: it paraphrased main reconciliation, per-event files with stable IDs, conditional channels, account-only UNCHECKED labels and three reader updates; identified the previous one-ledger architecture; excluded automatic migration, new modules, deployment and merge. Source-backed review confirmed all five closures. Nits accepted: scope provider grep to the skill; verify event IDs in manager/Amplifier handoffs. T3 delegation used the requested model/options; no relay driver exit code is claimed.

## Commands and observed results

- `python3 -B -m unittest discover -s tests`: exit 0, 8 tests, OK. Existing runtime suite; no new test machinery.
- `git diff --check origin/main HEAD`: exit 0.
- `git diff --exit-code 6507418 HEAD -- scripts tests`: exit 0; follow-up/merge preserves previously reviewed runtime fixes and tests byte-for-byte.
- Local Markdown-link inspection of README, Event Minder, manager and all three readers: exit 0; targets exist.
- `git check-ignore brands/example/events/2026-12-01-sale.md`: exit 0, path ignored. No file was created.
- `git grep -n launch-plan.md -- skills recipes README.md`: five matches, all explicitly legacy rules/context. Historical changelog and old audit receipts intentionally retain the former contract.
- Diff of `recipes/ecommerce.md`, `skills/results-review/SKILL.md`, `skills/weekly-plan/SKILL.md` against main changes only event reader/link instructions; all new main modules retained.

Source rejection controls used `git show REV:skills/event-minder/SKILL.md` and predicates scoped to that file (not the plan). These establish instruction presence, not runtime behavior:

| Predicate | 6507418 | 5526fba | 518dc00 |
|---|---|---|---|
| All Justuno/OptiMonk/Poptin examples present | false | true | true |
| Exact UNCHECKED — owner to confirm label | false | false | true |
| Per-event output path contract | false | false | true |
| Explicit no-LinkedIn-draft skip | false | false | true |

Prior PR already had general selected-channel drafting and honest UNCHECKED evidence; those are preserved, not claimed as newly fixed semantic failures. Main's fixed store-opening milestones and mismatched audit vocabulary are removed by retaining the improved PR workflow.

## Manual consumer walkthroughs

These are author instruction read-throughs with synthetic scenarios, not generated campaign executions or live browser checks. Each follows the current README → manager → Event Minder and reader instructions.

1. **New launch:** README routes to the available Event Minder and advertises its per-event path; manager routes launch/drop/seasonal work to it. With target December 1 and slug store-launch, the instruction yields `events/2026-12-01-store-launch.md`, stable ID `2026-12-01-store-launch`, dated criterion evidence, selected-channel drafts and an optional giveaway decision. A public analytics tag establishes only its own observation: collection, GSC ownership and submission each remain UNCHECKED — owner to confirm. PASS cannot collapse these independent checks. Provider selection remains a decision, not a readiness PASS. Verdict: coherent.
2. **Adjacent seasonal campaign:** existing launch plus a Black Friday sale on Instagram/email, no LinkedIn, irrelevant Product Hunt, declined giveaway. Event-scope rules choose offer/inventory/shipping/follow-up; LinkedIn is N/A with reason and no draft; Product Hunt and giveaway are N/A. No store-opening milestone is required. The new event file leaves the launch untouched and starts new readiness observations. Verdict: coherent.
3. **Unknown date/reschedule:** `2026-11-14-holiday-sale.md` uses creation date while target is unknown, later records December 1 in-file. Weekly Plan selects launch-day work for the week of November 30, not November 9. Unknown timing permits preparation only. Rescheduling retains path/ID and changes in-file dates. Results Review and ecommerce use the same in-file date/goal selection. Verdict: coherent.
4. **Legacy-only then rerun:** readers may use an active legacy `launch-plan.md` when no event file represents it. Once the owner confirms identity for a rerun, Event Minder writes a linked event file, preserving dated history but rechecking current readiness; legacy stays unchanged. All three readers prefer the event file for that event, so it is counted/scheduled once. A multi-event ledger link identifies the section/ID. Ambiguity requires clarification. No actual legacy file was migrated or byte-tested. Verdict: explicit contract, execution untested.
5. **Concurrent events/collision:** separate slugs on the same date yield separate paths; collisions cannot overwrite. Weekly reader retains separate links, and results reader keeps event results separate. Manager and Amplifier accept an active event ID without a path assumption, so the filename stem fits their handoff unchanged. Verdict: coherent.

## Remaining state

Final independent QA: Fable 5.2 high **Approved 66f8158**, no Blocker or Should. Reviewer independently checked all four requirements, provider preservation, three consumers, legacy precedence, merge preservation and receipt predicates. Optional product nits deferred; reviewed product content remains unchanged. This closeout changes audit documentation only. No live analytics, platform eligibility, private-file migration or campaign execution verified. No merge/deployment authorized. Lessons Learned: NO_ENTRY; one instruction walkthrough is confounded evidence and does not justify a general lesson.
