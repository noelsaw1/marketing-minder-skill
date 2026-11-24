# RELAY · GH11 shipping audit final review
<!--
  Single source of truth for this two-agent relay. Read the ENTIRE file before acting.
  Scaffolded by relay-automation/new-relay.sh on 2026-11-24.
-->

NEXT: Producer
STATUS: Approved
ROUND: 2 / 4

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
6. **Manual relay: commit only the relay file** (`relay(gh11-shipping-audit-final-review): <role> r<N>`); no push.
   **Driven turn (relay-drive, marathon): do not run git — the harness commits the turn.** **Stop** and report one line.
7. **Hand off explicitly — EVERY turn, not just the first** (GH-268). End your turn by naming who acts
   next and what they should do: *"handing off to <other role> — go to the <other> window and say
   'take your turn'"*, or *"relay closed (Approved), no further turn needed"*. (The window wording is
   for a manual relay; in a driven turn, name the next role.) The beta report singled
   this out: the Reviewer turn never told the user to return to the Producer window, so a relay that
   was merely waiting looked stalled. A turn that ends without this line is not finished.

## Setup
- Artifact under review: **.relay-artifacts/SKILL.md** — the read-only path that
  `relay-drive.sh --artifact-file /Users/noelsaw/Documents/GH Repos/marketing-minder-skill-gh11-shipping-audit-2026-11-24/skills/shipping-audit/SKILL.md` seeds into the isolated worktree (read it there; do NOT edit it).
- Reviewer: codex   ·   Producer: claude-a
- Started: 2026-11-24
- Definition of Done: Review the complete skills/shipping-audit/SKILL.md and its README, marketing-manager and ecommerce recipe links against docs/GH-11-shipping-audit-plan.md and issue #11. Check ten real products with shortfall disclosure, per-cart item quantities and all rates/defaults, source-backed expectations, boundaries and zones, split-shipment reconciliation, explicit authorization, preserving original cart, no orders/payment and gitignore guard. Validate the envelope-default mismatch and $3 + $5 group examples as acceptance controls. Report specific actionable gaps and note no live checkout is run in this review. Existing tests: python3 -B -m unittest discover -s tests (8 passed); skill-creator quick_validate passed; git diff --check passed. Scope is an instruction-only skill, not a software framework.

## Ground rules
1. This file is the single source of truth. The agents never share memory — read the whole file.
2. Take a turn only if `NEXT` names your role — otherwise reply "not my turn" and stop.
3. One turn = one block appended at the very bottom, above the marker. Never edit earlier turns. Plain blank separators may be added or removed between sections; preserve every substantive line, indentation, and fenced/literal blank line. A historical FAIL→PASS edit or changed fenced example is forbidden.
4. Stay tight — findings are bullets, not essays. Grade every finding.
5. **The Reviewer never edits the artifact.** It proposes graded findings; the Producer implements.
6. The relay ends on **Approved** (Reviewer only). In a manual relay, end each turn by committing just this file; no push. In a driven turn the harness commits.

## Log

### Reviewer · Round 1

swept file: yes

- [Should] Make the credential boundary explicit during the walkthrough. Issue #11 says “Avoid payment, order submission, credentials” and the plan excludes credential access. The skill's only explicit credential instruction concerns the saved report.
  Observed input: `rg -n 'credentials|unverified items' .relay-artifacts/SKILL.md` (exit 0) returns line 30, “do not include personal details, credentials, checkout tokens or private URLs”, and line 32, “unverified items”. Line 12 also names store settings as a possible source.
  Affected scope: If obtaining expected rates or observing checkout would require the assistant to request, retrieve or enter credentials, direct it to use owner-provided evidence or mark the affected assertion UNVERIFIED.
  Falsifier: At a sign-in-only checkout with owner authorization for cart testing, the instructions should yield UNVERIFIED for the unavailable observed rate without handling credentials. A guest checkout with visible rates should still proceed.
- [Should] Include the unverified scenario count requested by the plan, defining how a partially observed case is counted.
  Observed input: Line 32 asks for “planned and observed product and scenario counts” and “unverified items”. Line 26 allows multiple assertion verdicts in one case. The plan explicitly asks for “planned, observed and unverified counts”.
  Affected scope: Count each scenario with one or more UNVERIFIED assertions once, and preserve its other verdicts.
  Falsifier: For two observed carts, one fully assessed and one with two unknown expectations, the summary should show two observed scenarios and one with unverified assertions.
- [Pass] Lines 12–16 require dated, scoped expectations, ten distinct real products or an explicit shortfall, threshold and zone coverage, and original-cart preservation. Lines 8, 20 and 30 cover owner authorization, stopping before payment or order, restoration and the gitignore guard. The source checkout's `.gitignore:2` contains `/brands/`.
- [Pass] For one shipment of two units with two methods, lines 20–24 require the quantity, both rates, the initial selection and separate cart and checkout shipping amounts. Under line 26 the parcel default fails a documented envelope default even when the envelope is offered. For selected group fees of $3 and $5 the reconciliation matches a displayed $8 and flags a displayed $7 under line 24. Missing policy evidence keeps rate correctness UNVERIFIED independently of that arithmetic.
- [Pass] The source checkout's `README.md:21`, `skills/marketing-manager/SKILL.md:128` and `recipes/ecommerce.md:26` all point to `skills/shipping-audit/SKILL.md`. The recipe retains its owner-led default. `CHANGELOG.md:5` records the addition.

VERDICT: FAIL
Basis: Two instruction gaps remain against issue #11 and the plan. No further defects found in the full-file sweep. No live checkout or test suite was run in this review. The existing check results are those reported in Setup.

Handing off to Producer (claude-a) to address the two findings.

### Producer · Round 1 disposition

Implemented both findings: the walkthrough explicitly forbids requesting, retrieving or entering credentials and marks blocked assertions unverified; the report counts scenarios with one or more unverified assertions once while retaining other results. Handing off to Reviewer.

### Reviewer · Round 2

swept file: yes

- [Pass] Both Round 1 findings are resolved. `nl -ba .relay-artifacts/SKILL.md` (exit 0) shows “Do not request, retrieve or enter credentials” at line 8 and “count each such scenario once while retaining its other verdicts” at line 32. A sign-in barrier leaves an unsupported rate UNVERIFIED. A cart with two unknown fees and a proven default failure contributes one scenario to the unverified count and retains the FAIL.
- [Pass] The seeded skill requires dated, scoped expectations (line 12), ten distinct real products or a disclosed shortfall, threshold and zone coverage (line 14), owner authorization (line 8), and preservation and verification of cart contents and discounts (lines 16 and 30). Lines 20 and 30 stop before payment or order. Line 30 requires the ignore check before writing.
- [Pass] For two units and two offered methods, lines 20–24 require the quantity, both rates, the initial selection and both shipping displays. Under line 26, a parcel initially selected against a documented envelope default is FAIL. Under lines 24–26, selected group charges of $3 and $5 reconcile to $8 and a displayed $7 yields a $1 discrepancy. Missing supplier evidence leaves cost parity UNVERIFIED.
- [Pass] In the source checkout, `rg -n 'shipping-audit|^/brands/' README.md skills/marketing-manager/SKILL.md recipes/ecommerce.md .gitignore` (exit 0) returned the skill path at README.md:21, skills/marketing-manager/SKILL.md:128 and recipes/ecommerce.md:26, and “/brands/” at .gitignore:2. The recipe explicitly retains its owner-led default.

VERDICT: PASS
Basis: The full instruction file meets issue #11 and the shipping-audit plan. No additional pre-existing defects found. No live checkout was run. Existing test and validation results are as reported in Setup.

Relay closed (Approved), no further turn needed.


### Attestation · relay-drive — 2026-11-24T19:02:32Z
task: RELAY-MMS-GH11-FINAL
reviewer: codex
status: Approved
reviewed-head: f96d5cfdbb635f250cd68aa6d1ed3911f597ab39
added-range: 10297+1882
added-sha256: 4bc11ea8ccca271196f0dcd8e5f0defb127559fac23ecf56380a558ad32f96f6
gate-run: undeclared
<!-- ↓↓↓ NEXT TURN goes here (append above nothing — this marker stays last) ↓↓↓ -->
