# RELAY · GH11 shipping audit plan
<!--
  Single source of truth for this two-agent relay. Read the ENTIRE file before acting.
  Scaffolded by relay-automation/new-relay.sh on 2026-11-24.
-->

NEXT: Producer
STATUS: Approved
ROUND: 3 / 4

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
6. **Manual relay: commit only the relay file** (`relay(gh11-shipping-audit-plan): <role> r<N>`); no push.
   **Driven turn (relay-drive, marathon): do not run git — the harness commits the turn.** **Stop** and report one line.
7. **Hand off explicitly — EVERY turn, not just the first** (GH-268). End your turn by naming who acts
   next and what they should do: *"handing off to <other role> — go to the <other> window and say
   'take your turn'"*, or *"relay closed (Approved), no further turn needed"*. (The window wording is
   for a manual relay; in a driven turn, name the next role.) The beta report singled
   this out: the Reviewer turn never told the user to return to the Producer window, so a relay that
   was merely waiting looked stalled. A turn that ends without this line is not finished.

## Setup
- Artifact under review: **.relay-artifacts/GH-11-shipping-audit-plan.md** — the read-only path that
  `relay-drive.sh --artifact-file /Users/noelsaw/Documents/GH Repos/marketing-minder-skill-gh11-shipping-audit-2026-11-24/docs/GH-11-shipping-audit-plan.md` seeds into the isolated worktree (read it there; do NOT edit it).
- Reviewer: codex   ·   Producer: claude-a
- Started: 2026-11-24
- Definition of Done: Before source review paraphrase the plan in 2–5 sentences each under What this proposes and How the existing system works, per this document, plus What it is not. Then examine docs/GH-11-shipping-audit-plan.md and recipes/ecommerce.md and skills/weekly-plan/SKILL.md against issue #11: ten real product/scenario fee tests, trustworthy expectations, defaults and groups, cart restoration, no payment or orders, accurate PASS/FAIL/UNVERIFIED and private output; commensurate docs-only solution. Identify any omitted requirement or contradiction with existing workflow, citing concrete evidence.

## Ground rules
1. This file is the single source of truth. The agents never share memory — read the whole file.
2. Take a turn only if `NEXT` names your role — otherwise reply "not my turn" and stop.
3. One turn = one block appended at the very bottom, above the marker. Never edit earlier turns. Plain blank separators may be added or removed between sections; preserve every substantive line, indentation, and fenced/literal blank line. A historical FAIL→PASS edit or changed fenced example is forbidden.
4. Stay tight — findings are bullets, not essays. Grade every finding.
5. **The Reviewer never edits the artifact.** It proposes graded findings; the Producer implements.
6. The relay ends on **Approved** (Reviewer only). In a manual relay, end each turn by committing just this file; no push. In a driven turn the harness commits.

## Log

### Reviewer · Round 1

**What this proposes**  
Add a dedicated skill for ten representative shipping checks. Compare observed checkout fees with sourced expectations and save the results privately.

**How the existing system works, per this document**  
The ecommerce recipe gives the owner a general checkout walkthrough. Weekly Plan supplies the model for evidence labels and private dated reports.

**What it is not**  
The plan excludes payment, orders, configuration changes and scheduled automation.

swept file: yes

- [Blocker] The proposed inspection can accept a sticker test that never checks whether the **low-cost envelope** is the default, or a mixed cart that records a single amount without reconciling the shipments.
  Observed input: Plan line 10 says “sticker-alone default” and “mixed fulfillment groups where applicable”. Probe `gh issue view 11 --repo noelsaw1/marketing-minder-skill --json title,body` (exit 0) returned “sticker-only low-cost envelope default” and “distinguish individual shipment choices from totals”.
  Affected scope: Spell out both comparisons. Record all offered methods and the selection for each shipment, then reconcile selected charges to checkout shipping. Distinguish an absent expectation from an observed mismatch.
  Falsifier: With a documented envelope default, a sticker cart that offers the envelope but preselects parcel must FAIL. Two selected shipment fees of $3 and $5 should reconcile to $8, with all alternatives still visible.
- [Should] Make case selection cover relevant quantity breaks and destination differences, and bound the conclusion to the sample.
  Observed input: Plan line 10 specifies “quantities, boundary prices/weights” and “one named test destination”. Issue #11 explicitly asks for “boundary quantities/rates” and to “avoid claiming full coverage from samples”.
  Affected scope: Build ten distinct cases from real catalog variants/classes. Where policy changes at a quantity or shipping zone, include cases on both sides or identify the missing coverage. Report planned, observed and unverified counts.
  Falsifier: If a documented rate changes at quantity three, cases at two and three should expose the change. A second zone with a different policy should remain explicitly untested when all observations use the first.
- [Should] Include the existing skill router in discovery and validation.
  Observed input: Plan lines 10 and 15 list README and recipe entry points. Probe `rg -n 'weekly-plan|results-review' skills/marketing-manager/SKILL.md` in the source checkout (exit 0) shows routing entries at lines 128–129, including “A recurring Monday–Sunday marketing plan”.
  Affected scope: Add the shipping-audit intent to that router and inspect its link alongside the README and recipe links.
  Falsifier: Starting at the marketing-manager routing list, a shipping-fee audit request should resolve to the dedicated skill.
- [Should] Carry the private-write safeguard into the skill's run instructions.
  Observed input: Plan line 15 puts “verify gitignored business path” in implementation validation. Both recipes/ecommerce.md:62 and skills/weekly-plan/SKILL.md:44 require the operator to check before writing and stop on failure.
  Affected scope: Require the same runtime check before saving any audit report. Specify a dated path under the business folder.
  Falsifier: In a consumer checkout with the brands ignore rule missing, a run must stop before writing the report.
- [Pass] The documentation-only approach, sourced expectations, cart restoration, and prohibition on ordering are appropriate (plan lines 7, 10–12). Keep the authorization exception scoped to the dedicated skill. The existing walkthrough assigns checkout to the owner and prohibits submitting customer details (recipes/ecommerce.md:28–35).
- [Unverified — needs clone run] The helper suite was not run in this reviewer turn. README.md:116 limits its coverage to Python helpers. The plan's inspection must establish the shipping instructions themselves.

VERDICT: FAIL  
Basis: The plan's validation can succeed while omitting two explicit fee comparisons in issue #11. The scenario coverage, discovery and private-write gaps above also need dispositions. No additional pre-existing defect found in the reviewed plan.

Handing off to Producer (claude-a) to revise the plan and disposition each finding.

### Producer · Round 1 disposition

Implemented all findings in the updated plan: compare expected and actual selected low-cost envelope, record and reconcile each group; exercise documented boundaries and identify untested zones; route from marketing manager; check gitignore before writing dated report. Added explicit failing controls and sample limits. Handing off to Reviewer for re-review.

### Reviewer · Round 2

**What this proposes**

Build a discoverable skill for ten real shipping scenarios. Compare the selected rates and shipment totals with documented expectations and save a private, dated report.

**How the existing system works, per this document**

The ecommerce recipe gives the owner a checkout walkthrough. Weekly Plan provides the conventions for evidence labels and private reports.

**What it is not**

The audit excludes payment, order submission, store changes and scheduled automation.

swept file: yes

- [Pass] Plan lines 10 and 15 now test the envelope default explicitly and reconcile mixed shipments ($3 + $5 = $8). Line 10 covers both sides of known boundaries, untested zones, sample counts, the manager router and a pre-write ignore check consistent with recipes/ecommerce.md:62 and skills/weekly-plan/SKILL.md:44. Keep these controls.
- [Pass] Plan lines 7 and 10–12 keep the change documentation-only, require sourced expectations and cart restoration, and preserve the owner-led walkthrough in recipes/ecommerce.md:28–35. Keep the dedicated skill’s authorization boundary.
- [Should] Extend the observation record to every cart. Record the items and quantities actually tested, every offered method and its amount, the initially selected method, and the shipping fee visible at cart and checkout. Mark a fee unavailable at either step when the storefront does not show it.
  Observed input: Plan line 10 limits “record every option” to “every mixed cart”. Line 7 describes comparing “actual checkout fees”. The sticker control at line 15 can produce the correct FAIL from the selected parcel alone. Probe `gh issue view 11 --repo noelsaw1/marketing-minder-skill --json title,body` (exit 0) returned “customer-visible cart and checkout shipping fees” and “record all shipping choices, selected default, item quantities, taxes and relevant fee totals”.
  Affected scope: The per-scenario record for single- and multi-shipment carts, including cases outside quantity boundaries. Group reconciliation still applies to mixed carts.
  Falsifier: Inspect a completed single-group sticker case with quantity two, an envelope and a parcel option, and different cart and checkout shipping displays. If the current plan already requires both options and amounts, initial selection, tested quantity and both displays to appear, withdraw the finding.
- [Pass] The seeded artifact matched the source plan. Probe from the relay root: `cmp .relay-artifacts/GH-11-shipping-audit-plan.md '/Users/noelsaw/Documents/GH Repos/marketing-minder-skill-gh11-shipping-audit-2026-11-24/docs/GH-11-shipping-audit-plan.md'` (exit 0, no output). Source inspection covered the plan and both workflow documents. No other pre-existing plan defect found.

VERDICT: FAIL  
Basis: The round-one fixes are present. Issue #11 still requires observations that the single-shipment validation can omit. This is a plan review by inspection. No suite or checkout ran.

Handing off to Producer (claude-a) to specify the per-scenario record and its single-shipment validation.

### Producer · Round 2 disposition

Implemented: per-scenario record explicitly covers both cart and checkout, all groups and methods, quantities, taxes and totals, with unavailable values marked. Added the single-shipment falsifier. Handing off to Reviewer.

### Reviewer · Round 3

**What this proposes**

Add a discoverable skill for comparing shipping fees across ten representative storefront scenarios. Record the shopper-visible evidence and save a private, dated report.

**How the existing system works, per this document**

The ecommerce recipe assigns the checkout walkthrough to the owner. Weekly Plan supplies the conventions for evidence labels and private reports.

**What it is not**

The audit ends before payment or order submission and excludes store configuration changes.

swept file: yes

- [Pass] The round-two finding is resolved. Plan line 10 now requires “For every scenario record actual items and quantities, all offered methods and amounts per group, initial selection, cart and checkout shipping fees (or unavailable at either step), taxes and relevant totals.” Line 15 tests that rule with two units, two methods and different cart and checkout displays. Retain this single-shipment check alongside the envelope-default and mixed-shipment checks.
- [Pass] Against issue #11, plan lines 7, 10 and 15 cover ten distinct cases, documented expectations, known boundaries and zones, restoration of the shopper’s cart, and reporting limits. The parcel-default FAIL and $3 + $5 reconciliation give the implementer concrete expected outcomes. Keep the explicit incomplete counts and the rule for unknown expected rates.
- [Pass] Plan lines 10–12 preserve the owner-led checkout in recipes/ecommerce.md:28–35, scope agent cart interactions to explicit authorization, and adopt the private-write check from recipes/ecommerce.md:62 and skills/weekly-plan/SKILL.md:44. The README, recipe and manager router give the documentation-only change identifiable entry points. Retain the planned link inspection.
- [Pass] The reviewed copy matches the producer’s plan. Probe: `cmp .relay-artifacts/GH-11-shipping-audit-plan.md '/Users/noelsaw/Documents/GH Repos/marketing-minder-skill-gh11-shipping-audit-2026-11-24/docs/GH-11-shipping-audit-plan.md'` (exit 0, no output). The GitHub issue connector supplied the acceptance criteria after `gh issue view 11 --repo noelsaw1/marketing-minder-skill --json body,title` exited 1 with “error connecting to api.github.com”.

VERDICT: PASS  
Basis: The full plan addresses the issue and closes the prior observation gap. No additional pre-existing plan defect found. Approval covers the plan by inspection. Implementation checks and storefront observations belong to subsequent work.

Relay closed (Approved), no further turn needed.

<!-- ↓↓↓ NEXT TURN goes here (append above nothing — this marker stays last) ↓↓↓ -->
