---
name: market-fit
description: Review how well a business's offer fits its customer, using the brand file, and write ranked suggestions for the value proposition, home page copy, product bundles and pricing. Use when the user asks why the site is not converting, wants a better headline or home page, wants bundle ideas, or asks whether prices make sense.
---

# Market Fit

Work from the brand file that the marketing manager keeps. You compare what the business offers with who it says it sells to, and write suggestions the user can act on. You draft and advise. The user changes their own site, prices and products.

## Before you start

Read `brands/<business-slug>/brand.md`. If it does not exist, stop and send the user to `skills/marketing-manager/SKILL.md` to create it. If `Last read from site` is more than 90 days old, say so and offer a refresh first.

Before writing any report, apply the marketing manager's business identity and `brands/` privacy checks, even when invoked directly.

Read these sections: Brand, Ideal customer, Offer, Voice, Site notes and Open questions. Carry each statement's mark with it. A suggestion that rests on a `[guess]` is itself a guess, and you say so.

Read live pages only for the home page and up to three product or pricing pages, under the reading rules in the marketing manager skill: a browser session first, signed out, one page at a time, and stop for the whole site on an HTTP 429 or 403, a CAPTCHA or a login wall.

Ask the user at most three questions, and only ones that change a suggestion. The useful ones are usually: which products sell best, what each product costs to make and ship, and what customers say when they buy or complain. If the user does not answer, continue and mark what you could not check.

## What you review

**Value proposition.** State in one sentence who it is for, what they get, and why this instead of the nearest alternative. Test the current line and your own: if a competitor could say the same sentence unchanged, it is a description, not a value proposition. Offer at most three alternatives, each using words the site or the owner already uses.

**Home page copy.** Check the page title, meta description, main heading, first line under it, the main button, and the order of sections. Give the current text and the proposed text side by side. Keep to the voice in the brand file. Compare what the page leads with against what the catalog actually holds.

**Bundles.** Propose bundles only from products in the Offer section. Good bundles pair things one buyer wants together, such as items for the same model, team or use. Show the arithmetic for each: list prices, bundle price, and the saving in money and percent.

**Pricing.** Report what the prices show: the price points, odd endings, items priced alike that differ in cost or scarcity, and how shipping changes the total for the cheapest item. Check that any stated discount matches its own numbers.

## Rules for suggestions

- Without the owner's costs, never say a price is profitable or unprofitable. Say what you would need to know.
- Quote a competitor's price or wording only if you read it on their public page this run, and give the page.
- Never write a testimonial, review, sales figure, customer count or stock claim that the brand file does not hold as `[site]` or `[owner]`. Leave a marked placeholder for the owner to fill.
- Do not invent urgency. A limited run is limited only if the site or owner says so.
- Each suggestion states the change, where it goes, the brand file line it rests on, what to watch afterwards to see whether it worked, and its mark.
- Rank the suggestions and keep the top five. Put what would do the most for the least work first.

## What you write

Write `brands/<business-slug>/market-fit.md`. If the file exists, add a new dated run at the top and keep the earlier runs below it.

```markdown
# <Business name> market fit

## Run <YYYY-MM-DD>
Brand file read: <its Last read from site date>
Pages read this run: <paths, or none>

### Top five
Ranked list. One line each, pointing at the section below.

### Value proposition
### Home page copy
### Bundles
### Pricing

### Proposed brand file changes
Numbered. Section, current line, new line, mark. Status: pending, accepted or declined.

### Could not check
What you would need from the owner or the site.
```

## Brand file changes

You never edit `brand.md` yourself on your own judgment. When the review turns up a fact the brand file lacks or has wrong, list it under Proposed brand file changes and show it to the user. On acceptance, apply it under the rules in the marketing manager skill: change that one line, append a dated Change log line naming `market-fit` as the proposer, and set the status here to accepted. On refusal, leave `brand.md` untouched and set the status to declined.

Suggestions about the site itself, such as a new headline, are not brand file changes. They stay in `market-fit.md` until the owner makes the change on the site and the brand file is refreshed.

## Report

Finish with the path to `market-fit.md`, the top five in one line each, the number of brand file changes waiting for a decision, and the one question whose answer would improve the review most. Do not paste the file into the chat.

Last checked: 2026-11-14
