# Content drafts

Use the [content-drafts skill](SKILL.md) from any assistant with access to the full checkout and Python. Keep the business’s brand file at `brands/<business>/brand.md` and any Event Minder plans under its `events/` directory. Keep `brands/` gitignored.

Run the skill on demand or give its [weekly batch](routines/weekly-content-batch.md) and optional [daily X idea](routines/daily-x-idea.md) prompts to a scheduler in the business timezone. Return the local exports for review on any host. Recent X reads and remote X draft creation are independent capabilities. Remote drafts require an explicit request and an available draft-only connector.

The [Grok Bot setup](../../integrations/grok-bot/README.md) uses these same instructions.

## Commands

From the repository root, with Python 3.8 or newer and the standard library:

```sh
python3 scripts/content_queue.py calendar --business example --week 2026-11-16 --timezone America/Los_Angeles
# Fill drafts.json with copy for the actual slot IDs per SKILL.md.
python3 scripts/content_queue.py apply --business example --drafts brands/example/content/drafts.json
python3 scripts/content_queue.py validate --business example
python3 scripts/content_queue.py export --business example --format all
```

`--format` accepts `buffer`, `postiz`, `x-drafts`, or `all`.

## Drafts and the optional Postiz command

Default path: the script writes files. You upload the Buffer CSV and choose save as drafts. The X export stays local by default. On request, a draft-only connector can save the X slots filled in the current run. The export can also be handed over for manual use.

`publish` is a separate command. It does nothing unless you pass `--approve-publish` and set `CONTENT_QUEUE_ALLOW_PUBLISH=1`. Even then it only creates Postiz drafts (`type: draft`). It does not send `schedule` or `now`. Any X items sent to Postiz are drafts. It skips items already marked `queued-draft`. `--dry-run` prints the draft bodies and does not call the network.

Postiz `date` values are converted with an explicit offset, because the queue stores local times and this script does not guess a timezone from its name:

```sh
CONTENT_QUEUE_ALLOW_PUBLISH=1 POSTIZ_API_KEY=... POSTIZ_INTEGRATION_X=... \
  python3 scripts/content_queue.py publish --business example --provider postiz \
  --approve-publish --utc-offset -08:00
```

Set `POSTIZ_INTEGRATION_LINKEDIN` and `POSTIZ_INTEGRATION_INSTAGRAM` for those platforms. Self-hosted Postiz uses `POSTIZ_API_BASE` (default `https://api.postiz.com/public/v1`). Put the values in the environment. Do not write them into the repo, the queue file, or the command history you commit.

Buffer remains a CSV you upload. A second publish of a rewritten draft creates another Postiz draft; remove the older one in Postiz if you do not want both.
