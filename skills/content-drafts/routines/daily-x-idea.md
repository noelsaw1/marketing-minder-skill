# Daily X idea

Optional. Skip it when the weekly batch is enough.

Run the schedule in the business timezone.

- Cron, five fields: `0 8 * * 1-5`
- The same schedule in words: every weekday at 8:00 AM

Monday’s weekly routine runs at 7:00 AM. Replace `BUSINESS_SLUG` and `TIMEZONE`.

The routine adds at most one X draft. The person publishes.

## Prompt

```
Run the content-drafts skill at skills/content-drafts/SKILL.md for BUSINESS_SLUG, timezone TIMEZONE.

Create one X idea for today:

python3 scripts/content_queue.py idea --business BUSINESS_SLUG --date TODAY --timezone TIMEZONE

TODAY is today's date as YYYY-MM-DD. If the command says an X item already exists for today, fill that slot only when it is still empty. Do not add a second X post.

Write the post or a short thread from brands/BUSINESS_SLUG/brand.md and from any event file whose in-file date makes today a teaser, countdown, announcement or follow-up. Ignore the date in the filename.

Apply the draft, validate, and export with --format x-drafts. Return the export path. If I have requested a remote X draft and a draft-only connector is available, follow the skill’s handoff rules for only the slot filled this run. If today’s slot was already filled, leave it in place and report that no new draft was created.

Reply with the draft id and whether you created a new X draft.
```
