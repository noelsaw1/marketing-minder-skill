---
name: shipping-audit
description: Audit customer-visible cart and checkout shipping rates across ten representative store products and scenarios, comparing choices, defaults and fees with documented expectations.
---

# Shipping Audit

Check the actual customer buying path for a store's shipping costs and choices. The default is an owner-led walkthrough; an assistant may operate the cart and checkout when the owner authorizes that work. Do not alter store settings, submit an order, enter payment information or use a real person's contact or address details. Use a non-sensitive, appropriate test destination; record its region and postal code, not private checkout links or tokens. Follow the active host's browser and permission rules, and stop on a block or verification challenge.

## Prepare the sample and expectations

Read `brands/<business-slug>/brand.md` and any relevant e-commerce or event review when available. Identify the storefront, applicable market, currency, date, active offers and authoritative expected rates or promises from the owner, store settings, supplier or published policy. Record the source and date of each expectation, including which destination, variants, weights, quantities and discount conditions it covers. A displayed checkout rate is an observation, not proof of the intended rate or supplier cost. Missing or conflicting expectations are `[unknown]`; do not invent a rate or claim cost matching without supplier evidence.

Plan **ten distinct product cases** from the real catalog, recording product, variant, quantity and destination. Cover different shipping classes and fulfillment sources, single-item and multi-item quantities, mixed profiles and relevant discounts where available. Add carts on both sides of known quantity, price or weight thresholds and a different zone if its documented rate differs; name untested boundaries and zones. If fewer than ten distinct products are available, test the available products and useful additional cart scenarios, report the shortfall and do not imply ten products were tested. If the store offers stickers or another low-cost envelope product, include it alone and a mixed cart; establish whether the envelope is expected to be the initial default, rather than assuming it.

Preserve the preexisting cart: record its variants, quantities and applicable entered discounts before changes, and restore and verify it after testing. If it cannot be safely restored, use an isolated session where available or stop before changing it and report the blocker. Treat cart changes as test interactions, not authorization to purchase. Prefer the storefront browser and checkout tools available in the active host. Do not bypass store access controls. Use the e-commerce recipe for the broader owner-led funnel and merchandising review.

## Observe and compare

For each case start with the intended cart only, verify its contents and quantities, and proceed through the actual cart to checkout far enough for rates to load. If needed, supply the test destination using the host's supported checkout interface. Wait for rates to settle; distinguish an unavailable or pending result from a zero charge. Stop before order placement or payment. Record:

- Product and variant, quantity, destination, date/device, offers or codes and evidence location; cart and checkout product subtotals, discounts, taxes, other fees and shipping total. Mark a value unavailable if not displayed at that step.
- Every offered shipping method and amount for **each** shipment/group, its initially selected method, delivery estimate when shown, and the shipping amount displayed at both cart and checkout. Don't silently carry a choice from an earlier case as the initial default; use a fresh checkout or disclose that it may be retained.
- Expected choices, initial default and fees with source and date, and the observed results. For split fulfillment, list each group's items and selection and reconcile the sum of selected charges with the displayed checkout shipping total; report discrepancies rather than assuming a combined rate.

Assign **PASS** only when each applicable, sourced expectation matches an observed result; **FAIL** when an observed result contradicts a sourced expectation; **UNVERIFIED** for missing expectations, inaccessible or incomplete observations, or unresolved selection state. Separate individual assertion results if a case has both a proven failure and unknowns. For example, if the documented default is the low-cost envelope but checkout initially selects a parcel method, default selection fails even if the envelope is offered. For selected group charges of $3 and $5, compare their $8 sum to the displayed shipping total; record alternatives too.

## Report and restore

Restore the original cart and verify its contents and applicable entered discounts; say explicitly if restoration fails or is incomplete. Never submit payment or an order. Before saving, run `git check-ignore -q brands/` from the repository root and stop writing if it fails. Save a dated report under `brands/<business-slug>/shipping-audits/<YYYY-MM-DD>.md`; retain prior runs rather than overwriting them. Keep private observations in the gitignored business folder and do not include personal details, credentials, checkout tokens or private URLs.

Include the market, date, device, policy/expectation sources, planned and observed product and scenario counts, each case's expected and observed values and assertion verdicts, group reconciliation, evidence references, failures, unverified items, untested boundaries/zones and cart-restoration result. Mark source facts `[site: /path]`, owner-provided facts `[owner]`, inferences `[guess]` with their basis, and missing facts `[unknown]`. Summarize impact and proposed next actions without changing settings. State that results apply only to the tested products, variants, destinations and time; sampled passes do not prove the whole catalog or cost parity.
