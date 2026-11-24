# GH-11 storefront shipping audit plan

Issue: https://github.com/noelsaw1/marketing-minder-skill/issues/11
Base: 22624d9 (origin/main). Priority/severity/appeal/effort: 65/45/50/80: checkout errors can suppress sales, no incident trend established, neutral appeal, instruction-only implementation.

## Grounding and outcome
`recipes/ecommerce.md` provides an owner-performed general walkthrough but no reproducible ten-scenario rate comparison. `skills/weekly-plan/SKILL.md` demonstrates skill metadata, evidence labels and private dated reports. Add one dedicated skill to enable an operator or authorized agent to compare actual checkout fees with sourced expectations and report discrepancies without ordering.

## Approach and boundaries
Add `skills/shipping-audit/SKILL.md`, link from README, marketing-manager intent router and ecommerce recipe, and update changelog. Cover 10 distinct scenarios over 10 products where feasible, with justified alternatives and explicit incomplete counts. Include sticker-alone low-cost envelope default versus expected default; boundary quantity, price and weight cases on both sides when known; zones where materially different and mark untested zones. For every mixed cart record every option and selected amount per group and reconcile their sum to checkout shipping. Record test destination, rate labels/amounts/default, tax and other fees, evidence, expected-source provenance, PASS/FAIL/UNVERIFIED, no inferred policy, and restore any preexisting cart. Before writing a dated report under brands/<business>/shipping-audits/, check git check-ignore -q brands/ and stop writing if it fails. Report planned, observed and unverified counts and bound conclusions to tested cases. Honor explicit owner authorization and host capabilities while avoiding checkout payment, actual orders, and real personal data. Preserve the existing ecommerce recipe's owner-performed default; a user may explicitly authorize the assistant to perform cart interactions.

No platform API, credential access, synthetic rates, paid orders, settings changes, new testing framework or automated schedule. A generic walkthrough alone is insufficient because it lacks per-scenario expected-versus-actual fee evidence. Roll back by reverting this documentation change.

## Validation
Read the skill from README/recipe entry points and verify all ten-case and safe-checkout requirements by inspection, including the manager router link. Check that a documented envelope expected as default versus a parcel actually selected is FAIL, and selected group fees $3 and $5 reconcile to $8. Run existing `python3 -B -m unittest discover -s tests`; verify gitignored business path. Check diff and review against issue. Incomplete access or unknown expected rates must not be reported as passing.
