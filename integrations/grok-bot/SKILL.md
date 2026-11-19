---
name: grok-content-drafts
description: Draft a batch of X, LinkedIn and Instagram posts from the brand file and any active event files, then queue them for a person to approve. Use for a weekly content batch, a daily X idea, or platform-specific social drafts. Saves drafts; a person publishes.
---

# Content drafts

Turn the brand file into a week of social drafts. You write the words. `scripts/content_queue.py` builds the slots, checks the platform limits, and writes export files. A person approves and publishes.

Run the commands from the repository root. The business slug is the lowercase folder under `brands/`. Keep private copy under `brands/`; the script refuses to write there when `brands/` is not gitignored.

## Before you start

Read `brands/<business-slug>/brand.md`. If it is missing, send the person to `skills/marketing-manager/SKILL.md`. Read Brand, Ideal customer, Offer, Voice, Channels in use and Key dates, and keep each statement's mark.

Read the platform guide for every channel you will draft:

- `integrations/grok-bot/platforms/x.md`
- `integrations/grok-bot/platforms/linkedin.md`
- `integrations/grok-bot/platforms/instagram.md`

Read event files under `brands/<business-slug>/events/`. Event Minder owns those plans (`skills/event-minder/SKILL.md`). The filename looks like `2026-11-14-holiday-sale.md`, and that stem is the stable event ID. Schedule from the target date and milestone dates written inside the file. The date in the filename is only an ID. A file created on 14 November and later aimed at 1 December schedules the launch week of 30 November.

Use a legacy `brands/<business-slug>/launch-plan.md` only when the queue command says it used that file. When the command reports that the legacy file was left unused, ask which event it is and do not schedule it a second time. Keep concurrent events separate. When a slot's stage is `mixed`, say which event each line belongs to.

If `brands/<business-slug>/results/` has a review, read its recommended tests and prefer those formats. Do not invent metrics to fill a gap.

Look up tools on this run. Describe the job and let the runtime match a connector. Do not paste a remembered tool schema into the prompt.

- When an X reading connector is available, read this account's recent posts so the batch does not repeat them. If none is available, say so and draft from the brand file.
- LinkedIn and Instagram have no direct connector here. Leave them in the Buffer CSV.
- Read a Google Doc or Sheet only when the person says the brand file or calendar lives there. The queue still belongs in `brands/<business-slug>/content/`.
- Post a Slack note only when the person has named a channel. List draft ids and platforms, and say they are drafts waiting for approval.

## Write the drafts

Ask the script for the slots, then write `brands/<business-slug>/content/drafts.json` and apply it:

```sh
python3 scripts/content_queue.py calendar --business BUSINESS_SLUG --week WEEK_MONDAY --timezone TIMEZONE
python3 scripts/content_queue.py apply --business BUSINESS_SLUG --drafts brands/BUSINESS_SLUG/content/drafts.json
python3 scripts/content_queue.py validate --business BUSINESS_SLUG
python3 scripts/content_queue.py export --business BUSINESS_SLUG --format all
```

`WEEK_MONDAY` is the Monday of the week you are filling, as `YYYY-MM-DD`. `TIMEZONE` is a label such as `America/Los_Angeles`. It is stored on the queue. It does not convert clocks by itself.

The calendar command keeps text that is already in a slot. Running it again refreshes empty slots and adds the next week without deleting drafts.

`drafts.json` is a list, or an object with `items`. Each item needs the slot `id` from the queue. Set the fields you are filling:

```json
{
  "items": [
    {
      "id": "2026-11-17-x-1",
      "text": "One specific observation.",
      "hashtags": [],
      "basis": "[guess]"
    }
  ]
}
```

Use `thread` for an X thread, a list of post strings. Use `visual_brief` for every Instagram item, and `carousel` for a list of slide briefs. Leave `image_url` empty until the image has a public `https` link ending in `.jpg`, `.png`, `.webp` or `.gif`. A path inside `brands/` is not that link.

Set `basis` to `[site: /path]`, `[owner]`, `[guess]` or `[unknown]`. A line you composed from the brand voice is a `[guess]` unless the person supplied it.

For one extra X idea on a given day:

```sh
python3 scripts/content_queue.py idea --business BUSINESS_SLUG --date YYYY-MM-DD --timezone TIMEZONE
```

If that day already has an X slot, the command leaves it in place. Fill that slot when it is still empty. Do not add a second post beside it.

Pass `--x-premium` to `calendar` only after the person says the X account can publish long posts. The default limit is 280 weighted characters.

## What a draft may claim

Use claims the brand file or the event file already states, and carry their marks. Leave a blank the person can fill when a price, date, stock figure or customer proof is missing.

A last-chance line needs a cut-off or last-chance note on that day in the brand file or the event file. A countdown mentions the in-file event date. Do not invent a deadline, a follower count, a review, or a founder story the files do not contain.

Event Minder keeps the checklist and the giveaway rules. This skill drafts the social posts that point at that plan. Weekly Plan keeps the Monday–Sunday action list. Link a post to an event ID instead of copying the checklist into the caption.

## Hand the drafts over

Validate before you export. When validation fails, fix the drafts and apply again. Leave the export files unwritten until the batch passes.

The export writes three kinds of file under `brands/<business-slug>/content/exports/`:

- `*-buffer-x.csv`, `*-buffer-linkedin.csv`, and `*-buffer-instagram.csv`, when a row exists. Buffer's columns are `Text`, `Image URL`, `Tags`, and `Posting Time` (`YYYY-MM-DD HH:mm`). Tags are Buffer labels, so this column stays empty; hashtags stay in the text. An X thread contributes its first post to the CSV and the full thread to the X file. An Instagram row without a public image URL is listed in the manifest and left out of the CSV.
- `*-postiz-drafts.json`, a wrapper of Postiz draft bodies. `date` is the queue's local time. It is not a UTC instant.
- `*-x-drafts.json`, ordered post text for the X drafts connector.

Treat the X export as a queue snapshot. Return its path for review by default. Only save remote X drafts when the person has requested it and a draft-only X connector is available. Otherwise leave the export for manual handoff.

For an authorized connector handoff, use only the slot IDs filled in this run, intersected with the X export. If no X slot was filled, skip the connector. Save exact text in order. For a thread, save one draft per post and tell the person the order. Keep the confirmed connector draft IDs with the local review record, keyed by slot ID and post position. On retry, skip confirmed posts and stop for reconciliation if a previous attempt might have saved a post without returning a draft ID. Discard a draft only when the person names the draft to drop.

Tell the person the Buffer CSV paths and that they upload each file in Buffer and choose save as drafts. Instagram rows still need a public image before that upload will accept them.

Do not run `publish` unless the person asked, in this run, to create Postiz drafts. That command is off until both `--approve-publish` and `CONTENT_QUEUE_ALLOW_PUBLISH=1` are set, and it only creates Postiz drafts. X is never sent by that command. Setup, schedules and environment variables are in `integrations/grok-bot/README.md`.

## Report

Reply with the queue path, the count per platform, warnings, event IDs whose in-file date drove the week, any legacy-file warning, and the drafts that still need an image. Paste a full post only when the person asks to review it. Do not paste the brand file or the queue into a tracked issue or pull request.
