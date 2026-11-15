---
name: weekly-plan
description: Draft a recurring Monday–Sunday marketing plan from the brand file, active event plan and latest results review. Set a configurable minimum of actions per day, carry unfinished work forward, and save a private checklist for the user to review and execute.
---

# Weekly Plan

Turn the brand and recent results into a manageable week of actions. You draft and advise. The user posts, publishes, sends messages and changes their own site and accounts. A planned action is never evidence that it happened.

## Before you start

Read `brands/<business-slug>/brand.md`. If it is missing, send the user to `skills/marketing-manager/SKILL.md` first. Read Brand, Ideal customer, Offer, Voice, Channels in use and Key dates, preserving their evidence labels and dates.

Read the active `launch-plan.md`, the latest dated review under `results/`, and last week's plan under `weekly/`, if present. Note missing or stale inputs and continue from what is known. Use `skills/results-review/SKILL.md` for a fresh comparison when needed; do not invent results to fill a plan.

Confirm the Monday start date, business timezone, available owners and capacity. Default to the next full Monday–Sunday week and a minimum of two actions per day, stating these assumptions. Accept a user-configured positive integer minimum and record it in the plan. Ask only questions that change the schedule; mark unconfirmed owners or deadlines `[unknown]`.

## Evidence labels

Use `[site: /path]` for a public page read this run, `[owner]` for something the user told you, `[guess]` for a recommendation with its basis, and `[unknown]` for missing or unconfirmed information. Carry source dates and labels from the inputs without implying a fresh site read. Mark proposed actions `[guess]` unless the user has explicitly requested them; completion needs evidence or owner confirmation.

## Carry unfinished work forward

Review every prior item not confirmed done, including blocked items and earlier carryovers. Keep its ID, original date, owner and source-plan link. Ask about ambiguous status; lack of an update is not completion.

Place each unfinished item in the new week once, or record it under Carryover decisions with the blocker, next step and proposed deferred or dropped status. Dropping needs owner agreement. Keep the old plan unchanged and do not silently lose work. A carried action counts toward the daily minimum; do not also create a duplicate new action. Split an oversized task into linked steps, each under an hour.

## Build Monday–Sunday

Write all seven named days with their dates. Give each day at least the configured minimum of distinct, concrete actions, each estimated at less than 60 minutes. For each action include ID, owner, channel, estimated minutes, deliverable, done-check, status and evidence/basis. Use pending, blocked or done; start new actions pending.

Balance social, email, site improvements and in-person activity when they fit Channels in use and the owner's capacity. Favor formats supported by the latest review and include a small test when evidence is thin. Drafting a post and publishing it have different done-checks; publication belongs to the user. Avoid empty tasks such as “do marketing.”

Keep the daily workload within the stated capacity. If the minimum cannot fit, show the conflict and request a capacity or minimum decision instead of claiming an impossible schedule is ready. Do not pad days with duplicate actions. Blocked work stays visible but does not satisfy the minimum of actionable items.

## Ramp toward events

Use confirmed event dates, offer terms and shipping cut-offs from Key dates and Event Minder's plan. Map appropriate daily actions to teaser → announcement → countdown → live → last-chance, only for stages that fall in or prepare for this week. A last-chance message needs a confirmed deadline. Without dates, propose preparation tasks and mark timing unknown.

Event Minder owns event readiness, campaign mechanics and its checklist. Reference its milestone or section from each related weekly action; do not copy its checklist or create a competing event timeline. If no event plan exists, suggest `skills/event-minder/SKILL.md` and continue the recurring cadence. Flag conflicting dates for the owner rather than silently changing either source.

## What you write

Before writing, run `git check-ignore -q brands/` from the repository root and stop if it fails. Save `brands/<business-slug>/weekly/<YYYY-MM-DD>.md` using the Monday start date. Keep private details under the gitignored business folder; never stage them or copy them into tracked files.

Use this layout:

```markdown
# <Business name> weekly plan

Week: <Monday date> to <Sunday date>
Timezone: <business timezone>
Minimum actions/day: <user setting, default 2>
Capacity and owners: <confirmed constraints or unknown>
Inputs: <brand date, event plan, results review, previous week>

## Carryover decisions
<Each unfinished ID: scheduled day or blocker and proposed disposition>

## Monday <YYYY-MM-DD>
- [ ] <ID> | <owner> | <channel> | <minutes> | <action and deliverable> | Done: <observable check> | pending | <basis and mark>

<Repeat for Tuesday through Sunday, meeting the daily minimum>

## Event links and conflicts
## Proposed brand or event-plan changes
## Open questions
```

If the week already has a plan, preserve IDs, completed checks and carryover history. Show proposed revisions for acceptance before changing the existing plan. Never mark work done just because its scheduled day passed. Brand and event-plan changes stay proposals; accepted brand changes follow marketing manager's change log protocol.

## Report

Finish with the saved path, action counts and estimated time per day, carried items, blockers and decisions needed. On request, export a plain Markdown checklist in chat for the user to paste into their tracker, preserving IDs, dates, owners and done-checks. Do not write to the tracker or schedule posts yourself.
