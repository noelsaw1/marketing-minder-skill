# RELAY · GH2 final QA
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
6. **Commit only the relay file** (`relay(gh2-final-qa): <role> r<N>`); no push. **Stop** and report one line.
7. **Hand off explicitly — EVERY turn, not just the first** (GH-268). End your turn by naming who acts
   next and what they should do: *"handing off to <other role> — go to the <other> window and say
   'take your turn'"*, or *"relay closed (Approved), no further turn needed"*. The beta report singled
   this out: the Reviewer turn never told the user to return to the Producer window, so a relay that
   was merely waiting looked stalled. A turn that ends without this line is not finished.

## Setup
- Artifact under review: complete diff from 3c8c2e6661651d8f7c4086fe0e9d34f1aac8add4 plus full changed product files. Read docs/audits/gh2-plan.md, gh2-results.md and gh2-plan-relay.md.
- Reviewer: codex   ·   Producer: astra
- Started: 2026-11-14
- Definition of Done: Independently validate the committed implementation against the plan and all F1–F4 acceptance checks and receipts. Read the full three Python utilities, tests, four skills, recipe, README and changelog; ensure no duplicate subsystem, missing launch categories, fabricated evidence or lost private-state boundary. Grade commensurately for a small local stdlib skill repo. No live web/account/server actions; source review is allowed and the synthetic test receipt is supplied. Only write this relay file.
- User requirements: holistic entire-repo QA/sharpening, issue findings, branch -> PR. Preserve local Event Minder handoff. All launch checklist categories must remain; user confirmed phased campaign with checklist, dates/owners/draft copy, default recommended but optional contests/giveaways. No merge/deploy requested.  [Unverified — no citation]
- Plan QA PASS and attestation retained. Baseline five tests; implementation eight pass with baseline red control and disposable-clone CLI main/replay/resume smoke. Verify whether checks actually reject unfixed behavior. Account-specific platform behavior is explicitly unverified. Ratings 65/50/50/65 with unknown trend; no ledger exists.
- Do not require unrequested enterprise protections or a new converter; identify observed failures with concrete source/input. Record any limitation of your independent verification. Approval covers product content; later publication metadata/receipts may be appended without changing product behavior.

## Ground rules
1. This file is the single source of truth. The agents never share memory — read the whole file.
2. Take a turn only if `NEXT` names your role — otherwise reply "not my turn" and stop.
3. One turn = one block appended at the very bottom, above the marker. Never edit earlier turns. Plain blank separators may be added or removed between sections; preserve every substantive line, indentation, and fenced/literal blank line. A historical FAIL→PASS edit or changed fenced example is forbidden.
4. Stay tight — findings are bullets, not essays. Grade every finding.
5. **The Reviewer never edits the artifact.** It proposes graded findings; the Producer implements.
6. The relay ends on **Approved** (Reviewer only). End each turn by committing just this file; no push.

## Log

### Reviewer · Round 1

swept file: yes

VERDICT: PASS
Basis: Ship the product content. Reviewed the complete base-to-current change set and the full three utilities, both test files, four skills, recipe, README and changelog, plus the plan, results and prior relay. No additional pre-existing defect requiring revision was found in the swept product files. F1–F4 are satisfied at the source/probe level; broader runtime evidence remains producer-supplied as specified below.

- [Pass] F1 is repaired in the existing helpers: `scripts/browser_queue.py:26` requires a matching string identity for an existing checkpoint while allowing an absent file; `main` lowercases the account at line 57 and catches malformed-state errors at line 87. `scripts/save_connections.py:34` rejects userinfo, including empty userinfo. The probe below observed both rejection and valid controls. Keep these bounded fixes.
- [Pass] Acceptance checks reject unfixed behavior. `tests/test_inventory_workflows.py`, `test_existing_checkpoint_requires_matching_string_identity`, rejects `{}`, missing/null/numeric/wrong identity and an array while accepting absence and uppercase matching identity. The baseline expression `state.get("account", account).lower()` accepts missing identity and raises AttributeError for null/numeric identity; the added credential URL cases in `tests/test_save_connections.py:54` also fail the old predicate. The queue test checks selected URLs, action estimates, insufficient budget and blocker; the importer test checks replay byte equality and retained enriched name/email/followers. The reported four failed baseline subcases and two errors match these assertions. Independent suite execution is not claimed.
- [Pass] F2 retains all nine categories at `skills/event-minder/SKILL.md:40`: HTML, SEO, favicon, GSC, Analytics, social profiles, LinkedIn, Product Hunt, contests/giveaways. Three intake questions (16), event identity/history (28), separate technical/deliverable statuses (36, 61) and phased output with owners/dates/dependencies (82) meet the campaign request. Independent source walkthrough: a store with only a visible tag leaves account collection/ownership UNCHECKED (43–44); unanswered giveaway stays pending (20); a second seasonal event preserves history and rechecks current readiness (26–30); declined giveaway continues the remaining campaign (65). Keep the full checklist.
- [Pass] Factual-copy constraints at `skills/event-minder/SKILL.md:54`, separate marketing opt-in (71), approved incentives (73), current-rules review (74) and owner-run final walkthrough (84) remove unsupported founder/code/conversion assumptions. Publication/configuration remain user-owned (8). These are instruction contracts, not measured campaign outcomes.
- [Pass] F3 preserves shared ownership and privacy. `skills/marketing-manager/SKILL.md:12` checks Site identity before reuse and provides a distinct collision slug; line 14 checks ignored output and forbids copying private data into tracked reports. Direct consumers inherit this (`skills/market-fit/SKILL.md:14`; `skills/event-minder/SKILL.md:12`). Accepted-change ownership remains at manager line 105. Catalog absence needs complete/owner evidence (143); email-domain/date false positives are removed (137, 147); deployed-copy mutation is forbidden (188). README explains whole-repo dependencies and separate account state; `.gitignore` retains `/brands/` and `/temp/`. LinkedIn identity-repair instructions at `skills/linkedin-amplifier/SKILL.md:67` agree with the code.
- [Pass] F4 removes the pseudo-converter without adding a replacement subsystem. `recipes/insightfulpipe-ahrefs.md:28` stops without a compatible preparation route; lines 31–35 require selected operations, references, security, schema/dialect validation and actual saved UTF-8 bytes. Historical limits are qualified (7), secrets stay user-owned (39), activation stays with the user (43). CHANGELOG replaces the sanitizer-success claim with the validation requirement. No live connector success is asserted.
- [Pass] Architecture remains coherent: `scripts/import_linkedin_export.py` retains `from save_connections import ROOT, merge, normalize` and `merge(path, rows, fill_missing=True)`; `scripts/save_connections.py:64` remains the sole CSV writer with locking, nonblank precedence and atomic replacement; `scripts/browser_queue.py:59` reads state and computes a bounded queue without persisting it. No parallel queue, converter, scheduler or database was introduced. The unchanged importer and pre-existing utility code were swept too.

Evidence and limits:

- Graph Verify used `Users-noelsaw-Documents-GH-Repos-marketing-minder-skill`, generation `2026-11-14T20:20:37Z`. Function search returned ten nodes (two builtins), `has_more: false`. Coverage checked all twelve product/doc/test paths and root scope: no recorded source gaps, but the primary index lacks the new workflow test and excludes seven private/tool/cache subtrees. Its `read_state` snippet is baseline code. Full local reads supply current evidence. Both-direction normalize trace returned `MCP tool call requires approval, but approval policy is never`; direct source supplied relationships. No private ignored state was read.
- Source comparison: command `python3 -B -` read the specified base commit/tree/blob objects directly, resolved loose/packed objects, checked each SHA-1, and used `difflib.unified_diff` against local files. Two initial loose-only attempts exited 1 on packed objects; the completed reader exited 0: `Base objects verified by SHA-1; base files: 12 diff lines: 956`. The change list contains the expected product files, added Event Minder/workflow test and four audit documents; importer, ignore rules and LICENSE are unchanged. Output stayed in `.relay-scratch/tmp/base.diff`. The Event Minder handoff was additionally compared with the preserved primary draft. No Git executable or Git write was used.
- [Unverified — needs clone run] `docs/audits/gh2-results.md`, “Deterministic checks” and “CLI smoke — disposable full clone”, supplies eight passing tests, baseline red control, validator/link checks, CLI help and import/enrich/replay/resume receipts for `f9ea49edcbb68c65bdd65fda859288b31b392a0b`. Source supports the described checks; they were not independently rerun here. The post-turn harness and publication checks own fresh runtime/exact-head evidence. No suite, executable fixture, validate.sh, CLI main, web, account or server action ran this turn. Live platform behavior, current external docs/UI, campaign outcomes, issue rating storage and PR/publication state remain unverified by this reviewer. The receipt labels walkthroughs as author evidence and outcomes as confounded; no fabricated success was identified within that supplied scope.

Narrow probe command (synthetic checkpoints beneath scratch only):

```sh
export PYTHONDONTWRITEBYTECODE=1 TMPDIR="$PWD/.relay-scratch/tmp"
mkdir -p "$TMPDIR"
python3 -B - <<'PY'
import sys,json,tempfile
from pathlib import Path
sys.path.insert(0,str(Path('scripts').resolve()))
import browser_queue,save_connections
with tempfile.TemporaryDirectory(dir=Path('.relay-scratch/tmp')) as tmp:
 p=Path(tmp)
 print('absent:',browser_queue.read_state(p,'owner')[1])
 for value in ({},{'account':None},{'account':42},{'account':'other'},[],{'account':'OWNER'}):
  (p/'checkpoint.json').write_text(json.dumps(value))
  try: print('checkpoint',repr(value),'->',repr(browser_queue.read_state(p,'owner')[1]))
  except ValueError as e:print('checkpoint',repr(value),'->',type(e).__name__,str(e))
for url in ('https://user:secret@www.linkedin.com/in/alice/','https://@www.linkedin.com/in/alice/','https://uk.linkedin.com/in/ALICE/?trk=contact'):
 try:print('url',url,'->',save_connections.normalize({'linkedin_permalink':url})['linkedin_permalink'])
 except ValueError as e: print('url',url,'->',type(e).__name__,str(e))
print('Narrow function probe only; no main(), suite, browser or account access.')
PY
```

Exit 0. Decisive output: `absent: {}`; missing/null/numeric/wrong identity and array each produced `ValueError Checkpoint does not belong to the requested account`; `{'account': 'OWNER'} -> {'account': 'OWNER'}`; both userinfo URLs produced `ValueError Expected an HTTPS LinkedIn /in/ profile permalink`; valid regional uppercase URL produced `https://www.linkedin.com/in/alice/`.

Relay closed (Approved), no further turn needed. The harness owns the relay-only commit. Publication metadata/receipts may follow without changing this product-content verdict.


### Attestation · relay-drive — 2026-11-14T20:35:30Z
task: RELAY-marketing-gh2-final
reviewer: codex
status: Approved
reviewed-head: c8b052f0a6d908cab350e6643e63d8ea786425f6
added-range: 7156+8576
added-sha256: f5a127ae550e3f7723f7a52716dce083916a2738b4c8b20d2b6a50c993b6963a
gate-run: undeclared
<!-- ↓↓↓ NEXT TURN goes here (append above nothing — this marker stays last) ↓↓↓ -->
