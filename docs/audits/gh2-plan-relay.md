# RELAY · GH2 plan QA
<!--
  Single source of truth for this two-agent relay. Read the ENTIRE file before acting.
  Scaffolded by relay-automation/new-relay.sh on 2026-11-14.
-->

NEXT: Producer
STATUS: Approved
ROUND: 1 / 3

## ▶ TAKE YOUR TURN — read this first (works for ANY agent: Claude, Codex, agy)
1. **Read this whole file** (header, Setup, Ground rules, every block in the Log).
2. **Check it's your turn:** `NEXT` (top) names the role to act. Confirm you are bound to it and the
   last Log block isn't already yours. If not → STOP and reply "wrong window — nudge the <other> window."
3. **Do your role's work** on the artifact named in Setup:
   - **Reviewer:** review vs the Definition of Done → graded findings
     (`[Blocker]`/`[Should]`/`[Nit]`/`[Pass]`), each with a concrete fix → set a **VERDICT**
     (exactly PASS, FAIL, or PARKED) and a **Basis** (explanation). **Review the whole file, not just the diff** (GH-268):
     a beta test had this loop reach `Approved` in two rounds while an independent audit of the same
     branch found 20 issues (1 critical, 4 high) — every one of them in the pre-existing code the
     change sat on, which nobody had read. Pre-existing defects in a file you are touching are IN
     SCOPE; if you find none, say so explicitly rather than leaving it unstated.
     **Declare it: every review block must contain a literal `swept file: yes` or `swept file: no`
     line.** Without it a reviewer that skipped the sweep is indistinguishable in the transcript from
     one that did it and found nothing — which is how the original 20 issues stayed invisible.
     Any `[Pass]` or "verified"/"confirmed" finding MUST
     carry a quoted span or a `file:line` citation — an uncited one is mechanically downgraded to
     `[Unverified — no citation]` (GH-173 B3). Do **not** edit the artifact; only append findings here.
     **A finding that asks for a behaviour change is a generalization unless you can paste the concrete
     input — a row, a value, a `file:line` — that fails under the current code** (GH-681: the gh673
     final QA relay generalized one late-error observation into "or a later invalid identity", the
     Producer implemented it, the same seat `[Pass]`ed it next round, and one historical NULL-URL
     ledger row then blanked every issue). Every `[Blocker]` or `[Should]` requesting a behaviour
     change MUST carry three lines: `Observed input:` (the failing input you saw), `Affected scope:`
     (the input predicate the change would govern), `Falsifier:` (the fixture or data that would show
     the change unnecessary or wrong, and its expected result).
     A `[Blocker]` must cite an observed failure. This is a protocol rule, not a mechanical check —
     the Producer may disposition a request lacking these as `Declined — unproven generalization`.
   - **Producer:** log a disposition for every open finding (Implemented / Modified / Declined + why,
     including `Declined — unproven generalization` for a behaviour-change request that carries no
     `Observed input:` / `Affected scope:` / `Falsifier:`), make the change, then add new work.
4. **Append ONE block** at the very bottom, directly **above** the marker line. Never edit earlier turns. Plain blank separators may be added or removed between sections; preserve every substantive line, indentation, and fenced/literal blank line. A historical FAIL→PASS edit or changed fenced example is forbidden.
   Reviewer headings may be `### Reviewer · Round N`, `### Round N · Reviewer · <agent>`, `### Reviewer (<agent>)` (optionally followed by `— rN`), or `### Reviewer — Round N` (optionally followed by `(<agent>)`); follow the heading with a non-empty review body.
5. **Update the header:** flip `NEXT`; set `STATUS` (`Approved` closes — Reviewer only; else `Open`);
   the Producer bumps `ROUND` when opening a new cycle. If the max `ROUND` ends without `Approved`,
   set `STATUS: Escalated`.
6. **Commit only the relay file** (`relay(gh2-plan-qa): <role> r<N>`); no push. **Stop** and report one line.
7. **Hand off explicitly — EVERY turn, not just the first** (GH-268). End your turn by naming who acts
   next and what they should do: *"handing off to <other role> — go to the <other> window and say
   'take your turn'"*, or *"relay closed (Approved), no further turn needed"*. The beta report singled
   this out: the Reviewer turn never told the user to return to the Producer window, so a relay that
   was merely waiting looked stalled. A turn that ends without this line is not finished.

## Setup
- Artifact under review: **gh2-plan.md** (embedded below — read it here).
- Reviewer: codex   ·   Producer: astra
- Started: 2026-11-14

### Artifact — gh2-plan.md
```
# GH-2 holistic QA plan

Issue: https://github.com/noelsaw1/marketing-minder-skill/issues/2
Base: main at 3c8c2e6661651d8f7c4086fe0e9d34f1aac8add4.
Task slug: holistic-qa. Date: 2026-11-14.
Branch: fix/marketing-minder-skill-gh2-holistic-qa-2026-11-14.
The first task commit preserves the operator's unfinished Event Minder draft and its three documentation edits; the primary is unchanged.

## Outcome and boundaries
Make the existing small Markdown skill collection and three stdlib Python utilities reliable and consistent. Audit all tracked files plus the handoff, fix demonstrated problems, document limits. No new marketing modules, schedulers, database, framework, platform automation, live account writes, deployment, merge, or private-data publication. No claim of live SEO/analytics or connector verification.

## Ground truth
README -> marketing-manager -> shared brand.md -> market-fit/event-minder; LinkedIn uses separate account state and three CLI utilities. save_connections.main -> normalize -> merge is the sole CSV writer; import_linkedin_export.read_export -> normalize -> merge(fill_missing=True); browser_queue.main -> read_state -> permalink -> normalize is read-only. merge locks and atomically replaces CSVs. Existing five tests pass.

Graph Verify evidence: project Users-noelsaw-Documents-GH-Repos-marketing-minder-skill, generation 2026-11-14T20:20:37Z. Function search returned 10 symbols without pagination; normalize both-direction trace returned 4 callees/13 callers, no truncation. Coverage checked every source/doc/test and root scope. Exclusions: private brands/temp, relay-system, .claude, .git and caches; intentionally outside product audit. All tracked files read directly, including recipe Python embedded in Markdown. No graph completeness claim.

No repo startup/governance files, CI, PDDA, RELEASES or cleanup SOP exist in the tracked tree. main is the sole remote branch. Issue #1 is a broad open roadmap with importer/queue ideas already partly implemented, not a prior holistic fix. No PRs found.

## Findings and ordered changes
1. **F1 checkpoint identity (P2):** existing checkpoint without account silently adopts requested account. Require a string matching the account for existing files; absent checkpoint remains valid fresh start. Reject malformed existing state clearly. Keep queue and writer architecture intact. Add narrow tests for absent/missing/wrong/malformed/correct identity, budget/blocker behavior and importer fill-missing preservation using synthetic data. Reject embedded credentials in profile URL normalization (P3 input hygiene); no claim of credential disclosure.
2. **F2 Event Minder (P2):** preserve all requested checklist categories and default consideration of contests/giveaways. Add up to three material intake questions (event/date/goal, channels/audience, giveaway resources/eligibility); unanswered items remain assumptions. Separate technical PASS/FAIL/UNCHECKED/N/A from deliverable DRAFTED/approved/completed state. Public tag evidence cannot prove GA4 collection or GSC ownership/submission. Adapt seasonal/drop checklists, add per-event identity, dated evidence, historical preservation and rerun freshness; do not reuse old PASS as current proof. No forced giveaway, fictitious founder narrative, promo code or guaranteed conversion. Draft mechanics subject to owner constraints and current platform/jurisdiction checks, separate entrant contact from marketing permission. No legal determination or live activation.
3. **F3 shared instruction contracts (P2/P3):** marketing-manager checks stored site identity before reuse and offers distinct domain-based slug on collision; preserve existing names. Prevent sample-based catalog absence claims, domain/date false positives, private data copying and uncontrolled deployed-skill edits. Market-fit/event writes inherit privacy check; preserve provenance. LinkedIn checkpoint schema documents required account. README states account vs brand separation and testing/installation from whole repo, since helpers and sibling modules are required.
4. **F4 Ahrefs recipe (P2):** keep curation instructions but replace the unvalidated inline pseudo-converter with an honest, bounded manual preparation/validation procedure referencing official specs. It is not a shipped converter; do not add a second subsystem to maintain. Explain missing endpoints/refs/security must fail validation, no mere version relabeling, measured UTF-8 output must meet observed limit. Historical UI/limit observations are dated, not guarantees. Generic business slug; user handles secrets and activation. Verify official documentation for externally changing claims. Changelog corrects sanitizer claim.
5. Write audit receipt with disposition for every finding, all tracked paths considered, checks and exclusions. Update changelog. Final relay QA, publication, exact-head verification, issue closeout and safe published-clone retirement per start-task.

## Solution-fit and rating
Smallest viable bet: sharpen existing instructions and fix small identity/input validation defects. Documentation-only alternative cannot repair the queue accepting unowned state; adding an OpenAPI conversion utility is unnecessary when the current recipe never shipped a validated converter. Rollback: revert task commits; no migrations or production writes. Risk: stricter checkpoints need account repair after verifying signed-in identity, and recipe users need a validated compatible manifest instead of trusting the old snippet.
Rated 65/50/50/65, pri/sev/appeal/effort. Consequences are recoverable wrong progress or misleading recommendations, not observed loss. Appeal neutral. Recurrence windows 2026-10-31–11-14 and 2026-10-17–10-30: only one roadmap issue, no incident evidence; trend unknown. No user override. Rating is stored in issue #2 (no ledger exists).

## Acceptance / bounded verification
- F1 red: synthetic existing checkpoint without account is accepted by baseline; fixed code must reject while absent file starts empty and correct account succeeds. Test importer duplicates/reimport preserves enriched fields, queue excludes inspected/inaccessible and obeys blocker/action budget. Existing suite plus small behavioral cases; no framework/fuzzer or mirrored wording tests.
- F2 main consumer walkthrough: new-store plan has all user checklist items, intake, optional giveaway and unknown account-only metrics. Adjacent: a second seasonal event preserves history and starts fresh checks; declined giveaway is N/A and no messages/actions execute. Manual receipt, not live platform testing.
- F3: inspect routing from README and all module consumers; synthetic same-stem domains must not share state; sampled catalog cannot establish absence. Check ignore rules and relative references. Do not read private data.
- F4 baseline snippet demonstrably filters missing paths and skips unresolved refs, and replaces enum types without actual validation. Revised recipe must stop at validation and defer activation to user; no assertion generator succeeded.
- Run python3 -B -m unittest discover -s tests, all CLI help commands, skill frontmatter validator if available, git diff --check and local link checks. Runtime CLI smoke: synthetic export -> save enrichment -> queue; rerun export preserves enrichment. Store public synthetic evidence in docs/audits/gh2-results.md. No new CI/gates; this repo has none.

## QA and state
Plan QA pending. Implementation not started beyond preservation of supplied handoff. Independent Codex plan review must paraphrase this document before reading sources, then validate against requirements and source. Grade this small local skill repo commensurately, not as an enterprise platform. Reviewer writes only relay receipt. Final QA will inspect committed diff, checks and manual walkthroughs.
```
- Definition of Done: Review the embedded plan first, before supplementary source. Begin your review with 2–5 sentences each under What this proposes and How the existing system works, per this document, plus What it is not. Record that input boundary. Then read the repository source and the user requirements below, and label technical assessment source-backed. Confirm falsifiable acceptance, all requested checklist categories, surgical scope, privacy, preserved handoff and truthful rating. Grade against a small local skill repository, not enterprise architecture. No production edits. No web or live account actions required.
- User requirements: Holistic QA review audit and sharpening of the entire repo; new branch -> PR; findings on new GH issue. Prior launch request: group launches with seasonal checklists, recommend contests/giveaways by default, ask sharpening questions; include SEO-friendly HTML, SEO, favicon, GSC, GA, LinkedIn announcement, social profile creation and ProductHunt submission.
- Sources: README.md, skills/*/SKILL.md, scripts/*.py, tests/test_save_connections.py, recipes/insightfulpipe-ahrefs.md, CHANGELOG.md, .gitignore. Baseline main 3c8c2e6; handoff commit 974dc60. Private ignored state is out of scope.

## Ground rules
1. This file is the single source of truth. The agents never share memory — read the whole file.
2. Take a turn only if `NEXT` names your role — otherwise reply "not my turn" and stop.
3. One turn = one block appended at the very bottom, above the marker. Never edit earlier turns. Plain blank separators may be added or removed between sections; preserve every substantive line, indentation, and fenced/literal blank line. A historical FAIL→PASS edit or changed fenced example is forbidden.
4. Stay tight — findings are bullets, not essays. Grade every finding.
5. **The Reviewer never edits the artifact.** It proposes graded findings; the Producer implements.
6. The relay ends on **Approved** (Reviewer only). End each turn by committing just this file; no push.

## Log

### Reviewer · Round 1

#### What this proposes
The plan audits the small skill collection and its three Python utilities, fixes checkpoint identity validation, sharpens shared instructions and Event Minder, and replaces the unvalidated Ahrefs snippet with a manual validation procedure. It preserves the supplied handoff and delivers bounded verification, a public synthetic audit receipt, and a PR through the existing task workflow.

#### How the existing system works, per this document
Marketing-manager owns a shared brand file consumed by market-fit and event-minder; LinkedIn uses separate account state. The Python tools share normalization and a single CSV merge implementation, while the browser queue reads inventory and checkpoint state without writing them.

#### What it is not
This proposes no new marketing platform, scheduler, database, conversion subsystem, or live account automation. It does not promise live analytics verification, legal approval, deployment, or merge.

Input boundary: the paraphrase above was formed from the embedded plan before supplementary source inspection and was recorded in commentary before those reads. The technical assessment below is source-backed; approval concerns the plan, not completed implementation.

swept file: yes

VERDICT: PASS
Basis: Ship this plan into implementation. The whole embedded artifact and the full declared product source set were reviewed, including pre-existing content and recipe Python; no additional pre-existing plan defect requiring revision was found. Existing product defects identified below are already covered by F1–F4. Acceptance is falsifiable and the scope fits a small local skill repository.

- [Pass] F1 targets an actual source-level identity gap: `scripts/browser_queue.py:26` uses `state.get("account", account).lower()`, so an existing object lacking `account` takes the requested identity. The proposed absent-file/missing/wrong/malformed/correct-account cases distinguish fresh starts from unowned persisted state. `scripts/save_connections.py:29` parses the URL but its rejection predicate at lines 32–40 does not check userinfo; the planned credential rejection is accurately rated input hygiene, without an invented disclosure claim. Keep both fixes in their existing functions as planned.
- [Pass] Requested launch categories are present and retained by F2's explicit “preserve all requested checklist categories” contract: SEO-friendly HTML (`skills/event-minder/SKILL.md:38`), SEO foundations (44), favicon (48), GSC (51), GA4 (54), social profiles (58 and 123), LinkedIn (70), ProductHunt (75), and default giveaways (82). Event types already group launches, drops, and seasonal campaigns (24–26). The planned three intake questions, new-store walkthrough, second seasonal event, and declined-giveaway case cover the requested sharpening and prevent stale readiness from carrying across events (`skills/event-minder/SKILL.md:104`). Maintain the explicit category coverage in the implementation receipt.
- [Pass] F2 corrects misleading certainty rather than adding live actions: public-page auditing currently asks for GA4 collection and GSC submission (`skills/event-minder/SKILL.md:51`–56); entrant email currently becomes a marketing list (89), and the draft assumes a founder story and promo code (71, 79). The plan explicitly separates account-only unknowns, consent, factual copy, optional incentives, and draft/completion status. Its “no messages/actions execute” acceptance preserves the existing user-publishes boundary (10).
- [Pass] F3 addresses concrete shared-state/privacy contracts. Domain-without-extension naming (`skills/marketing-manager/SKILL.md:12`) maps example.com and example.net to the same folder; its collision acceptance is therefore useful. Sample reading (22) cannot support unrestricted catalog absence claims (141); domain/date findings (135, 145, 151) need the planned qualification. The privacy rule (14), deployed-edit instruction (186), provenance handling (`skills/market-fit/SKILL.md:14`), and separate LinkedIn schemas (`skills/linkedin-amplifier/SKILL.md`, “Keep local results in `temp/<account>/`”) are all within the proposed bounded edits. Preserve accepted-change ownership and historical runs as planned.
- [Pass] F4 chooses a proportionate correction. The recipe claims a valid converter (`recipes/insightfulpipe-ahrefs.md:54`) but silently filters missing paths (76), skips missing referenced components (115), rewrites arbitrary large enums to string (127–131), relabels the output version (151), and reports serialized character length instead of actual written UTF-8 bytes (164–167). Manual preparation with explicit endpoint/reference/security/version/byte validation, dated observations, and user-owned activation removes the unsupported success claim without creating another utility. The corresponding sanitizer success assertion in `CHANGELOG.md` is explicitly included in the plan's correction.
- [Pass] Scope, rollback, handoff intent, and rating are appropriately bounded in the artifact: “The first task commit preserves the operator's unfinished Event Minder draft and its three documentation edits”; “Rollback: revert task commits”; “recoverable wrong progress or misleading recommendations, not observed loss”; and “trend unknown.” The current draft and its README/changelog/router entries remain in the supplied source. No enterprise architecture or new CI gate is warranted. Numeric ratings are prioritization judgments supported by this modest consequence description, not measured incident statistics.

Evidence and limits: Codebase-memory Verify used the marketing-minder-skill project at its primary checkout, generation `2026-11-14T20:20:37Z`; scripts function search returned eight functions with `has_more: false`. Coverage checked the declared source/doc/test paths and root scope, with no recorded source-path gaps and seven excluded subtrees; LICENSE was untracked by graph metadata and the task plan absent from that primary index. Local source reads supply worktree evidence rather than assuming graph/worktree equivalence. `read_state` snippet agreed with local source. `trace_path(normalize, both)` was denied by automatic approval policy (“MCP tool call requires approval, but approval policy is never”); relationships were instead checked directly in the three complete utility sources. No private ignored state was read.

Source-only probe: after `export PYTHONDONTWRITEBYTECODE=1 TMPDIR="$PWD/.relay-scratch/tmp"; mkdir -p "$TMPDIR"`, ran `python3 -B -` using `ast.parse(Path(path).read_text())` and top-level `ast.FunctionDef` enumeration for the three script paths. Exit 0; decisive output: `scripts/browser_queue.py: permalink, read_state, main`; `scripts/save_connections.py: normalize, merge, main`; `scripts/import_linkedin_export.py: read_export, main`; `Source-only AST inspection; no utilities or tests executed.` This is syntax/structure inspection, not runtime verification.

[Unverified — needs clone run] The claimed five passing baseline tests and all future runtime/importer/queue checks remain for the producer's disposable full clone and final QA. No suites, executable fixtures, CLI runs, web, or live-account actions were performed this turn. Commit ancestry, unchanged primary, issue/PR state, and the stored issue rating were not independently queried; preserve these as producer provenance claims pending publication/exact-head checks, not reviewer-verified facts.  [Unverified — no citation]

Relay closed (Approved), no further turn needed. The harness owns the relay-only commit; no git command was run by this reviewer.

<!-- ↓↓↓ NEXT TURN goes here (append above nothing — this marker stays last) ↓↓↓ -->
