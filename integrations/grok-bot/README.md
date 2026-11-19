# Grok Bot setup for content drafts

The [content-drafts skill](../../skills/content-drafts/SKILL.md) is the shared source for drafting, validation and handoff. Keep the whole repository available to the bot so it can read the brand, platform guides and queue script. Existing paths in this folder point to the shared instructions.

1. Ask the bot to read `skills/content-drafts/SKILL.md` and save it as a skill. Enable the private skill library under Connect apps if the skill is missing. Refresh any saved prompt copies so they use the current handoff rules.
2. Set Settings → Bot → Timezone to the business timezone.
3. Create a routine from the [weekly batch prompt](../../skills/content-drafts/routines/weekly-content-batch.md). It runs Monday at 7:00 AM (`0 7 * * 1`). The optional [daily X idea](../../skills/content-drafts/routines/daily-x-idea.md) runs weekdays at 8:00 AM (`0 8 * * 1-5`).
4. Open the routine, check When to run, and use Test once while the checkout and brand file are available. The test creates drafts for review. Local exports work without connectors. Enable an X reading connector for deduplication if desired, or a draft-only X connector when you want the bot to save authorized remote drafts.

See the [shared setup and commands](../../skills/content-drafts/README.md) for local runs, export formats and optional Postiz drafts.
