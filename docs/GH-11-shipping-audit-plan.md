# GH-11 storefront shipping audit plan

Issue: https://github.com/noelsaw1/marketing-minder-skill/issues/11
Base: 22624d9 (origin/main). Priority/severity/appeal/effort: 65/45/50/80: checkout errors can suppress sales, no incident trend established, neutral appeal, instruction-only implementation.

## Grounding and outcome
`recipes/ecommerce.md` provides an owner-performed general walkthrough but no reproducible ten-scenario rate comparison. `skills/weekly-plan/SKILL.md` demonstrates skill metadata, evidence labels and private dated reports. Add one dedicated skill to enable an operator or authorized agent to compare actual checkout fees with sourced expectations and report discrepancies without ordering.

## Approach and boundaries
Add `skills/shipping-audit/SKILL.md`, link from README and ecommerce recipe, and update changelog. Cover 10 distinct scenarios over 10 products where feasible, with justified alternatives and explicit incomplete counts. Include sticker-alone default, quantities, boundary prices/weights, mixed fulfillment groups where applicable, one named test destination, rate labels/amounts/default, tax and other fees, evidence, expected-source provenance, PASS/FAIL/UNVERIFIED, no inferred policy, and restore any preexisting cart. Results go only to gitignored business data. Honor explicit owner authorization and host capabilities while avoiding checkout payment, actual orders, and real personal data. Preserve the existing ecommerce recipe's owner-performed default; a user may explicitly authorize the assistant to perform cart interactions.

No platform API, credential access, synthetic rates, paid orders, settings changes, new testing framework or automated schedule. A generic walkthrough alone is insufficient because it lacks per-scenario expected-versus-actual fee evidence. Roll back by reverting this documentation change.

## Validation
Read the skill from README/recipe entry points and verify all ten-case and safe-checkout requirements by inspection. Run existing `python3 -B -m unittest discover -s tests`; verify gitignored business path. Check diff and review against issue. Incomplete access or unknown expected rates must not be reported as passing.
