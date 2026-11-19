# Content drafts portability plan

Issue #9 builds on PR #8 at 0e0cea4. This repository uses main and has no PDDA or RELEASES ledger. The follow-up targets the PR #8 head branch so the diff can be built and reviewed now. Retarget to main once #8 lands and the stacked changes have been reconciled.

## Current flow

The Grok skill and two routines load the shared brand and dated Event Minder files, call calendar or idea, apply, validate and export, then return files or optionally hand new X drafts to a draft-only connector. The same Python entry point and gitignored queue work with any host with checkout access and Python. The canonical instructions, paths and routine setup language still assume Grok.

## Changes

1. Move the canonical skill, platform guides and routine prompts into skills/content-drafts. Keep schedules and business timezone requirements portable. Document prerequisites and a manual run in the canonical README. Keep the existing Grok skill (with its frontmatter), platform guide and routine paths as thin pointers so previously configured hosts can resolve the same workflow. Keep Grok UI settings in its integration README.
2. Update the root module directory, Marketing Manager link, CHANGELOG and existing guide checks. Point limit and cron assertions at the canonical paths, and check that each Grok pointer names its canonical file. Clarify that local file exports are complete deliverables and that X draft reading and writing are separate optional capabilities. Preserve current-run slot scoping and retry instructions.
3. Keep the CLI, files and schemas unchanged. A scoped export format, further connectors, scheduler implementation and publishing changes are outside this issue. A rename alone would leave Grok UI steps and old paths unresolved. Revert the follow-up commits to roll back.

## Acceptance

Run `python3 -B -m unittest discover -s tests` and `git diff --check`. Verify root and compatibility links resolve and the canonical prompts do not use Grok settings UI. The unchanged follow-up base (PR #8 head `0e0cea4`) lacks the canonical path, and both old routine prompts contain `Settings, Bot`. The new canonical routines must have zero matches. Run the documented local path with temporary brand/event fixtures and no connector credentials, including apply with nonempty X text and export, and inspect the `"publish": false` in both queue.json and the X export and the intended draft content. Check the existing daily idea and weekly schedule paths resolve to the canonical workflow.

Ratings for intake are priority 2/5 (useful for onboarding), severity 2/5 (core runs today), appeal 3/5 (neutral), effort 2/5 (primarily documentation and path checks).
