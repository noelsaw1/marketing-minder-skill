# Weekly content batch

Schedule, in the bot timezone (Settings, Bot, Timezone). Set that timezone to the business timezone.

- Cron, five fields, minute hour day-of-month month day-of-week: `0 7 * * 1`
- The same schedule in words: every Monday at 7:00 AM

Replace `BUSINESS_SLUG` and `TIMEZONE` before saving the routine. `TIMEZONE` is the label stored on the queue, such as `America/Los_Angeles`, and it should match the bot timezone.

The routine writes drafts. The person publishes. After you save it, open the routine, check When to run, and use Test once while this repository is available.

## Prompt

```
Run the content-drafts skill at integrations/grok-bot/SKILL.md for BUSINESS_SLUG, timezone TIMEZONE.

Use the Monday of the current week in that timezone. If today is Monday, use today. Read brands/BUSINESS_SLUG/brand.md. Read event files under brands/BUSINESS_SLUG/events/ and schedule from the target date inside each file, not from the date in the filename. If the queue command reports a legacy launch-plan.md, follow that report. Keep concurrent events separate.

Look up connectors on this run. Read recent X posts when a reading connector is available. Do not assume a tool schema from memory.

From the repository root, run the calendar, apply, validate and export commands in the skill. Write brands/BUSINESS_SLUG/content/drafts.json before apply. python3 scripts/content_queue.py is the queue script.

Save each validated X post with the X drafts connector, in order. Leave the Buffer CSVs for me to upload as drafts. Do not upload them and do not schedule them.

Do not run the publish command unless I asked you to create Postiz drafts in this run.

If the checkout or the brand file is missing, stop and tell me. Do not invent a brand, and do not keep the queue only inside this bot.

Reply with counts per platform, warnings, event IDs, export paths, and any draft that still needs an image.
```
