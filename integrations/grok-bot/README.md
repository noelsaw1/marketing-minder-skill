# Grok Bot content drafts

This folder is the Grok Bot setup for drafting X, LinkedIn and Instagram posts from a Marketing Minder brand file. The files here are the source. Saving a skill or a routine inside one Grok Bot account copies them. When you change a prompt in the bot, copy that change back into this folder.

The agent writes drafts and queues them. You approve and publish.

## File layout

```
integrations/grok-bot/
  SKILL.md                          how to draft a batch
  README.md                         this setup
  platforms/x.md                    X length and thread rules
  platforms/linkedin.md             LinkedIn tone and length
  platforms/instagram.md            caption, hashtags, image brief
  routines/weekly-content-batch.md  Monday prompt and schedule
  routines/daily-x-idea.md          optional weekday X prompt
scripts/content_queue.py            queue, validation, export
tests/test_content_queue.py
brands/<business>/content/          gitignored, created on first run
  queue.json
  calendar.md
  drafts.json
  exports/
```

`brands/<business>/events/<YYYY-MM-DD>-<event-slug>.md` is an Event Minder file. The script reads the target date inside it. The date in the filename is the event's stable ID, not the day the posts go out. A legacy `launch-plan.md` is used only when no event file represents that event.

## Install the skill

Keep this whole repository where the bot can read it. The skill calls `scripts/content_queue.py` and reads the platform files beside it. Copying only `SKILL.md` leaves those out.

In the bot, ask it to read `integrations/grok-bot/SKILL.md` and save that process as a skill named content drafts. The description in the frontmatter is the "use this when" line. The private skill library is shared across your bots; enable it for this bot under Connect apps if it does not appear.

## Install a routine

Set the bot timezone under Settings, Bot, Timezone, to the business timezone. Grok Bot stores the schedule in that zone.

Create the weekly routine with the prompt in `routines/weekly-content-batch.md`. The schedule is the five-field cron `0 7 * * 1`, which is every Monday at 7:00 AM. Ask for it in those words if the routine editor wants a sentence, then open the routine and check When to run.

The daily X idea is optional. Its cron is `0 8 * * 1-5`, every weekday at 8:00 AM. The two Monday runs are an hour apart.

A new routine waits for the next scheduled time. Use Test on the routine to run it once while the repository checkout is open. Test does the real drafting work and stops at drafts. A routine that runs in the cloud still needs this checkout and the brand file. If either is missing, the skill tells the bot to stop.

## Connectors

Look up tools on each run. The prompts name the job, not a fixed tool schema.

- X drafts: create a draft of the exported text. This does not publish. Discard a draft only when you name it.
- X reading: optional, so the batch can skip posts you already made.
- Buffer: you upload the CSV for LinkedIn and Instagram and choose save as drafts. There is no Buffer token in this repo, and the script does not call Buffer.
- Postiz: optional, and off. See below.
- Google Drive, Docs or Sheets: only if you keep a copy of the brand file there. The queue still goes under `brands/`.
- Slack: optional review note, only in a channel you name.

## Commands

From the repository root, with Python 3.8 or newer and the standard library:

```sh
python3 scripts/content_queue.py calendar --business example --week 2026-11-16 --timezone America/Los_Angeles
python3 scripts/content_queue.py validate --business example
python3 scripts/content_queue.py export --business example --format all
```

`--format` accepts `buffer`, `postiz`, `x-drafts`, or `all`.

## Drafts and the optional Postiz command

Default path: the script writes files. You upload the Buffer CSV and choose save as drafts. The X export stays local by default. On request, a draft-only connector can save the X slots filled in the current run. The export can also be handed over for manual use.

`publish` is a separate command. It does nothing unless you pass `--approve-publish` and set `CONTENT_QUEUE_ALLOW_PUBLISH=1`. Even then it only creates Postiz drafts (`type: draft`). It does not send `schedule` or `now`. It does not post to X. It skips items already marked `queued-draft`. `--dry-run` prints the draft bodies and does not call the network.

Postiz `date` values are converted with an explicit offset, because the queue stores local times and this script does not guess a timezone from its name:

```sh
CONTENT_QUEUE_ALLOW_PUBLISH=1 POSTIZ_API_KEY=... POSTIZ_INTEGRATION_X=... \
  python3 scripts/content_queue.py publish --business example --provider postiz \
  --approve-publish --utc-offset -08:00
```

Set `POSTIZ_INTEGRATION_LINKEDIN` and `POSTIZ_INTEGRATION_INSTAGRAM` for those platforms. Self-hosted Postiz uses `POSTIZ_API_BASE` (default `https://api.postiz.com/public/v1`). Put the values in the environment. Do not write them into the repo, the queue file, or the command history you commit.

Buffer remains a CSV you upload. A second publish of a rewritten draft creates another Postiz draft; remove the older one in Postiz if you do not want both.
