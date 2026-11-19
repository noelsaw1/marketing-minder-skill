"""Queue, limit and event-date tests for the Grok Bot content drafts script."""

import csv
import datetime
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import urllib.error

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import content_queue  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "content_queue.py"
WEEK = datetime.date(2026, 11, 16)

BRAND = """# Example brand file

Site: https://example.com
Last read from site: 2026-11-01
Pages read: /

## Brand
Example makes widgets.

## Ideal customer
People who need widgets. [guess]

## Offer
A widget for 20.

## Voice
"Plain and specific."

## Channels in use
X, LinkedIn and Instagram. [owner]

## Key dates
2026-11-17 - Order cut-off for the holiday drop [owner]

## Site notes
None.

## Open questions
None.

## Change log
2026-11-01 | Brand | created | [site: /] | marketing-manager
"""

EVENT = """# Holiday sale

## 1. Event brief
- Stable ID: 2026-11-14-holiday-sale
- Filename-date basis: 2026-11-14
- Date/timezone: 2026-12-01 America/Los_Angeles
- Goal/metric: orders during launch week

## 3. Phased campaign
- T-14 days: preparation
- T-1 day: final walkthrough
- Launch Day: store opens
- T+3 days: follow-up email
"""

LEGACY = """# Example Launch Plan

Target launch date: 2026-11-20

## 5. Timeline & Milestones
- T-1 day: final walkthrough
- Launch Day: store opens
"""


def item(**overrides):
    base = {
        "id": "2026-11-17-x-1",
        "platform": "x",
        "status": "draft",
        "scheduled_local": "2026-11-17T09:15",
        "purpose": "test",
        "campaign_stage": "none",
        "text": "Hello from the queue",
        "thread": [],
        "hashtags": [],
        "link": "",
        "image_url": "",
        "alt_text": "",
        "visual_brief": "",
        "carousel": [],
        "source": "brand.md",
        "basis": "[guess]",
        "events": [],
    }
    base.update(overrides)
    return base


def queue_with(*items):
    queue = content_queue.empty_queue("example", "UTC", WEEK)
    queue["items"] = list(items)
    return queue


class EventSelectionTests(unittest.TestCase):
    def test_in_file_date_schedules_and_filename_date_does_not(self):
        event = content_queue.parse_event_document(
            EVENT, "2026-11-14-holiday-sale", "2026-11-14"
        )
        self.assertEqual(event["target_date"], "2026-12-01")
        self.assertEqual(event["filename_date"], "2026-11-14")
        self.assertEqual(event["timezone"], "America/Los_Angeles")
        brand = content_queue.parse_brand(BRAND)
        early = content_queue.build_week_items(datetime.date(2026, 11, 9), brand, [event])
        self.assertNotIn("announcement", [slot["campaign_stage"] for slot in early])
        saturday = early[5]
        self.assertNotEqual(saturday["campaign_stage"], "announcement")
        launch_week = content_queue.build_week_items(datetime.date(2026, 11, 30), brand, [event])
        self.assertEqual(launch_week[0]["campaign_stage"], "countdown")
        self.assertIn("T-1", launch_week[0]["purpose"])
        self.assertEqual(launch_week[1]["campaign_stage"], "announcement")
        self.assertIn("launch day", launch_week[1]["purpose"])
        self.assertEqual(launch_week[1]["events"][0]["target_date"], "2026-12-01")
        self.assertIn("T+3", launch_week[4]["purpose"])

    def test_unknown_target_does_not_fall_back_to_the_filename(self):
        text = "## 1. Event brief\n- Date/timezone: TBD\n"
        event = content_queue.parse_event_document(text, "2026-11-14-holiday-sale", "2026-11-14")
        self.assertEqual(event["target_date"], "")
        self.assertTrue(event["date_unknown"])
        slots = content_queue.build_week_items(WEEK, content_queue.parse_brand(BRAND), [event])
        self.assertTrue(all(slot["campaign_stage"] in ("none", "last-chance") for slot in slots))
        self.assertEqual(slots[1]["campaign_stage"], "last-chance")

    def test_disagreeing_target_dates_are_not_scheduled(self):
        text = "- Target date: 2026-12-01\n- Launch date: 2026-11-20\n"
        event = content_queue.parse_event_document(text, "2026-11-14-holiday-sale", "2026-11-14")
        self.assertEqual(event["target_date"], "")
        self.assertTrue(event["conflicts"])
        slots = content_queue.build_week_items(WEEK, {"key_dates": []}, [event])
        self.assertTrue(all(slot["campaign_stage"] == "none" for slot in slots))

    def test_concurrent_events_stay_separate(self):
        first = content_queue.parse_event_document(
            "- Target date: 2026-11-16\n", "2026-11-16-launch", "2026-11-16"
        )
        second = content_queue.parse_event_document(
            "- Target date: 2026-11-20\n", "2026-11-20-drop", "2026-11-20"
        )
        slots = content_queue.build_week_items(WEEK, {"key_dates": []}, [first, second])
        monday = slots[0]
        self.assertEqual(monday["campaign_stage"], "mixed")
        self.assertEqual(
            {ref["id"] for ref in monday["events"]},
            {"2026-11-16-launch", "2026-11-20-drop"},
        )

    def test_legacy_file_is_used_only_when_no_event_represents_it(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            business = root / "brands" / "example"
            events = business / "events"
            events.mkdir(parents=True)
            legacy = business / "launch-plan.md"
            legacy.write_text(LEGACY, encoding="utf-8")
            alone, warning = content_queue.select_events(root, "example", None, None)
            self.assertEqual(warning, "")
            self.assertEqual([event["id"] for event in alone], ["launch-plan"])
            self.assertEqual(alone[0]["target_date"], "2026-11-20")

            event_path = events / "2026-11-14-holiday-sale.md"
            event_path.write_text(EVENT, encoding="utf-8")
            (events / "notes.md").write_text("not an event", encoding="utf-8")
            unlinked, warning = content_queue.select_events(root, "example", None, None)
            self.assertEqual([event["id"] for event in unlinked], ["2026-11-14-holiday-sale"])
            self.assertIn("launch-plan.md was left unused", warning)
            self.assertIn("notes.md", warning)
            slots = content_queue.build_week_items(WEEK, {"key_dates": []}, unlinked)
            self.assertNotEqual(slots[4]["campaign_stage"], "announcement")

            event_path.write_text(
                EVENT + "\n- Legacy source: brands/example/launch-plan.md\n",
                encoding="utf-8",
            )
            linked, warning = content_queue.select_events(root, "example", None, None)
            self.assertEqual([event["id"] for event in linked], ["2026-11-14-holiday-sale"])
            self.assertNotIn("left unused", warning)
            self.assertTrue(linked[0]["legacy_link"])

    def test_brand_parser_keeps_key_dates_out_of_the_change_log(self):
        brand = content_queue.parse_brand(BRAND)
        self.assertEqual(brand["title"], "Example brand file")
        self.assertEqual(brand["site"], "https://example.com")
        self.assertEqual([item["date"] for item in brand["key_dates"]], ["2026-11-17"])
        self.assertIn("Plain and specific.", brand["sections"]["Voice"])

    def test_daily_idea_does_not_add_a_second_x_post(self):
        queue = content_queue.empty_queue("example", "UTC", WEEK)
        created, idea_id, _reason = content_queue.add_idea(queue, datetime.date(2026, 11, 18), "x")
        self.assertTrue(created)
        self.assertEqual(idea_id, "2026-11-18-x-idea")
        created, existing, reason = content_queue.add_idea(queue, datetime.date(2026, 11, 18), "x")
        self.assertFalse(created)
        self.assertEqual(existing, idea_id)
        self.assertIn("already exists", reason)
        queue["items"] = [item()]
        created, existing, reason = content_queue.add_idea(queue, datetime.date(2026, 11, 17), "x")
        self.assertFalse(created)
        self.assertEqual(existing, "2026-11-17-x-1")

    def test_calendar_merge_keeps_draft_text(self):
        brand = content_queue.parse_brand(BRAND)
        event = content_queue.parse_event_document(EVENT, "2026-11-14-holiday-sale", "2026-11-14")
        first = content_queue.build_week_items(WEEK, brand, [event])
        first[0]["text"] = "Kept"
        first[0]["status"] = "draft"
        again = content_queue.build_week_items(WEEK, brand, [event])
        merged = content_queue.merge_items(first, again)
        self.assertEqual(merged[0]["text"], "Kept")
        self.assertEqual(len(merged), 7)
        later = content_queue.build_week_items(datetime.date(2026, 11, 23), brand, [event])
        merged = content_queue.merge_items(merged, later)
        self.assertEqual(len(merged), 14)
        self.assertEqual(merged[0]["text"], "Kept")


class DraftValidationTests(unittest.TestCase):
    def test_x_weighted_length_counts_urls_emoji_and_wide_text(self):
        self.assertEqual(content_queue.x_weighted_length("a" * 280), 280)
        self.assertEqual(content_queue.x_weighted_length("https://example.com/" + "b" * 80), 23)
        self.assertEqual(content_queue.x_weighted_length("hi https://example.com"), 26)
        self.assertEqual(content_queue.x_weighted_length("你"), 2)
        self.assertEqual(content_queue.x_weighted_length("😀" * 140), 280)
        long_link = "https://example.com/" + "b" * 100
        result = content_queue.validate_item(
            item(text="a" * 250, link=long_link)
        )
        self.assertEqual(result["errors"], [])
        self.assertEqual(result["lengths"], [274])
        over = content_queue.validate_item(item(text="a" * 281))
        self.assertFalse(content_queue.validate_queue(queue_with(item(text="a" * 281)))["ok"])
        self.assertIn("280", over["errors"][0])
        premium = content_queue.validate_item(item(text="a" * 281), x_premium=True)
        self.assertEqual(premium["errors"], [])

    def test_linkedin_and_instagram_limits(self):
        linkedin = content_queue.validate_item(
            item(platform="linkedin", text="a" * 3001, id="li")
        )
        self.assertIn("3000", linkedin["errors"][0])
        hook = content_queue.validate_item(
            item(platform="linkedin", text="a" * 211, id="li")
        )
        self.assertEqual(hook["errors"], [])
        self.assertTrue(any("see more" in warning for warning in hook["warnings"]))
        missing = content_queue.validate_item(
            item(platform="instagram", text="A caption", id="ig")
        )
        self.assertIn("visual_brief", missing["errors"][0])
        tags = ["t{0}".format(index) for index in range(6)]
        recommended = content_queue.validate_item(
            item(platform="instagram", text="A caption", hashtags=tags, visual_brief="A widget on a table", id="ig")
        )
        self.assertEqual(recommended["errors"], [])
        self.assertTrue(any("5 or fewer" in warning for warning in recommended["warnings"]))
        too_many = ["t{0}".format(index) for index in range(31)]
        capped = content_queue.validate_item(
            item(
                platform="instagram",
                text="A caption",
                hashtags=too_many,
                visual_brief="A widget on a table",
                id="ig",
            )
        )
        self.assertTrue(any("30" in error for error in capped["errors"]))
        slides = ["slide {0}".format(index) for index in range(21)]
        carousel = content_queue.validate_item(
            item(platform="instagram", text="A caption", visual_brief="", carousel=slides, id="ig")
        )
        self.assertTrue(any("20" in error for error in carousel["errors"]))
        local = content_queue.validate_item(
            item(
                platform="instagram",
                text="A caption",
                visual_brief="A widget",
                image_url="brands/example/widget.png",
                id="ig",
            )
        )
        self.assertTrue(any("https" in error for error in local["errors"]))

    def test_prepare_queue_cannot_mark_itself_published(self):
        queue = queue_with(item(status="published"))
        queue["publish"] = True
        prepared = content_queue.prepare_queue(queue)
        self.assertFalse(prepared["publish"])
        self.assertEqual(prepared["items"][0]["status"], "draft")

    def test_apply_updates_known_ids_and_reopens_exported_copy(self):
        queue = queue_with(item(status="exported"))
        content_queue.apply_drafts(queue, {"items": [{"id": "2026-11-17-x-1", "text": "Hello from the queue"}]})
        self.assertEqual(queue["items"][0]["status"], "exported")
        content_queue.apply_drafts(queue, {"items": [{"id": "2026-11-17-x-1", "text": "Rewritten"}]})
        self.assertEqual(queue["items"][0]["status"], "draft")
        self.assertEqual(queue["items"][0]["text"], "Rewritten")
        with self.assertRaises(ValueError):
            content_queue.apply_drafts(queue, {"items": [{"id": "missing", "text": "no"}]})

    def test_exports_are_draft_files_and_skip_invalid_batches(self):
        ready = queue_with(
            item(),
            item(
                id="2026-11-18-instagram-1",
                platform="instagram",
                text="A widget, still on the bench.\nSecond line",
                visual_brief="Square photo of the widget",
                scheduled_local="2026-11-18T11:00",
            ),
            item(
                id="2026-11-19-x-1",
                platform="x",
                text="",
                thread=["First post", "Second post https://example.com/very/long"],
                scheduled_local="2026-11-19T12:30",
            ),
        )
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            manifest = content_queue.export_queue(ready, directory, ["buffer", "postiz", "x-drafts"], "2026-11-16")
            self.assertFalse(manifest["publish"])
            buffer_x = directory / "exports" / "2026-11-16-buffer-x.csv"
            self.assertFalse(buffer_x.read_bytes().startswith(b"\xef\xbb\xbf"))
            with buffer_x.open(encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(list(rows[0].keys()), ["Text", "Image URL", "Tags", "Posting Time"])
            self.assertEqual(rows[0]["Text"], "Hello from the queue")
            self.assertEqual(rows[0]["Posting Time"], "2026-11-17 09:15")
            self.assertEqual(rows[1]["Text"], "First post")
            self.assertIn("2026-11-19-x-1", manifest["thread_first_post_only"])
            self.assertIn("2026-11-18-instagram-1", manifest["omitted_instagram"])
            self.assertFalse((directory / "exports" / "2026-11-16-buffer-instagram.csv").exists())
            postiz = json.loads((directory / "exports" / "2026-11-16-postiz-drafts.json").read_text(encoding="utf-8"))
            self.assertFalse(postiz["publish"])
            self.assertTrue(all(entry["body"]["type"] == "draft" for entry in postiz["items"]))
            self.assertEqual(postiz["dates_are"], "local")
            drafts = json.loads((directory / "exports" / "2026-11-16-x-drafts.json").read_text(encoding="utf-8"))
            self.assertFalse(drafts["publish"])
            self.assertEqual(drafts["items"][1]["posts"][0], "First post")
            broken = queue_with(item(text="a" * 281))
            with self.assertRaises(content_queue.ValidationFailed):
                content_queue.export_queue(broken, directory / "nope", ["buffer"], "2026-11-16")
            self.assertFalse((directory / "nope").exists())


class PublishGuardTests(unittest.TestCase):
    def test_postiz_send_requires_opt_in_and_stays_a_draft(self):
        queue = queue_with(item())
        calls = []

        def opener(request, timeout=30):
            calls.append(request)
            body = request.data.decode("utf-8")
            self.assertNotIn("super-secret", body)
            self.assertNotIn("from-the-file", body)
            payload = json.loads(body)
            self.assertEqual(payload["type"], "draft")
            self.assertEqual(payload["date"], "2026-11-17T17:15:00.000Z")
            self.assertEqual(request.get_header("Authorization"), "super-secret")
            self.assertEqual(request.get_method(), "POST")

            class Response:
                def read(self):
                    return b'[{"postId": "post-1"}]'

                def __enter__(self):
                    return self

                def __exit__(self, *_args):
                    return False

            return Response()

        queue["api_key"] = "from-the-file"
        saved = []
        with self.assertRaises(ValueError):
            content_queue.queue_postiz_drafts(
                queue,
                approve=True,
                allow_publish="",
                api_key="super-secret",
                api_base="https://api.postiz.com/public/v1",
                integration_ids={"x": "int-x", "linkedin": "", "instagram": ""},
                utc_offset="-08:00",
                dry_run=False,
                opener=opener,
                save=lambda updated: saved.append(updated),
            )
        self.assertEqual(calls, [])
        dry = content_queue.queue_postiz_drafts(
            queue,
            approve=False,
            allow_publish="",
            api_key="super-secret",
            api_base="https://api.postiz.com/public/v1",
            integration_ids={"x": "int-x", "linkedin": "", "instagram": ""},
            utc_offset="-08:00",
            dry_run=True,
            opener=opener,
            save=lambda updated: saved.append(updated),
        )
        self.assertNotIn("super-secret", json.dumps(dry))
        self.assertEqual(dry["requests"][0]["type"], "draft")
        self.assertEqual(calls, [])
        result = content_queue.queue_postiz_drafts(
            queue,
            approve=True,
            allow_publish="1",
            api_key="super-secret",
            api_base="https://api.postiz.com/public/v1",
            integration_ids={"x": "int-x", "linkedin": "", "instagram": ""},
            utc_offset="-08:00",
            dry_run=False,
            opener=opener,
            save=lambda updated: saved.append(updated),
        )
        self.assertEqual(result["queued"], [{"id": "2026-11-17-x-1", "post_id": "post-1"}])
        self.assertEqual(queue["items"][0]["status"], "queued-draft")
        self.assertFalse(queue["publish"])
        self.assertEqual(len(calls), 1)
        with self.assertRaisesRegex(ValueError, "No drafts"):
            content_queue.queue_postiz_drafts(
                queue,
                approve=True,
                allow_publish="1",
                api_key="super-secret",
                api_base="https://api.postiz.com/public/v1",
                integration_ids={"x": "int-x", "linkedin": "", "instagram": ""},
                utc_offset="-08:00",
                dry_run=False,
                opener=opener,
                save=lambda updated: saved.append(updated),
            )

        original = content_queue.build_postiz_body

        def scheduled(*args, **kwargs):
            payload = original(*args, **kwargs)
            payload["type"] = "schedule"
            return payload

        content_queue.build_postiz_body = scheduled
        queue["items"][0]["status"] = "draft"
        try:
            with self.assertRaises(ValueError):
                content_queue.queue_postiz_drafts(
                    queue,
                    approve=True,
                    allow_publish="1",
                    api_key="super-secret",
                    api_base="https://api.postiz.com/public/v1",
                    integration_ids={"x": "int-x", "linkedin": "", "instagram": ""},
                    utc_offset="-08:00",
                    dry_run=False,
                    opener=opener,
                    save=None,
                )
        finally:
            content_queue.build_postiz_body = original
        self.assertEqual(len(calls), 1)

    def test_http_error_does_not_echo_the_key(self):
        queue = queue_with(item(), item(id="2026-11-19-x-1", text="Second", scheduled_local="2026-11-19T12:30"))

        def opener(request, timeout=30):
            if len(opener.calls) == 0:
                opener.calls.append(request)
                class Response:
                    def read(self):
                        return b'[{"postId": "post-1"}]'

                    def __enter__(self):
                        return self

                    def __exit__(self, *_args):
                        return False

                return Response()
            raise urllib.error.HTTPError(
                request.full_url, 400, "bad", hdrs=None, fp=io.BytesIO(b"rejected")
            )

        opener.calls = []
        with self.assertRaises(ValueError) as caught:
            content_queue.queue_postiz_drafts(
                queue,
                approve=True,
                allow_publish="1",
                api_key="super-secret",
                api_base="https://api.postiz.com/public/v1",
                integration_ids={"x": "int-x", "linkedin": "", "instagram": ""},
                utc_offset="+00:00",
                dry_run=False,
                opener=opener,
                save=lambda _updated: None,
            )
        self.assertNotIn("super-secret", str(caught.exception))
        self.assertIn("HTTP 400", str(caught.exception))
        self.assertEqual(queue["items"][0]["status"], "queued-draft")


class CommandTests(unittest.TestCase):
    def test_calendar_refuses_bad_input_and_writes_a_private_queue(self):
        bad_slug = subprocess.run(
            [sys.executable, str(SCRIPT), "calendar", "--business", "../example", "--week", "2026-11-16"],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertNotEqual(bad_slug.returncode, 0)
        self.assertIn("lowercase domain slug", bad_slug.stderr)
        bad_week = subprocess.run(
            [sys.executable, str(SCRIPT), "calendar", "--business", "example", "--week", "2026-11-17", "--root", "/tmp"],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertIn("not a Monday", bad_week.stderr)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.check_call(
                ["git", "init", "-q"],
                cwd=str(root),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            brand = root / "brand.md"
            brand.write_text(BRAND, encoding="utf-8")
            refused = subprocess.run(
                [sys.executable, str(SCRIPT), "calendar", "--business", "example", "--week", "2026-11-16",
                 "--root", str(root), "--brand", str(brand)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(refused.returncode, 0)
            self.assertIn("not gitignored", refused.stderr)
            self.assertFalse((root / "brands").exists())
            (root / ".gitignore").write_text("brands/\n", encoding="utf-8")
            event = root / "2026-11-14-holiday-sale.md"
            event.write_text(EVENT, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "calendar", "--business", "example", "--week", "2026-11-30",
                 "--timezone", "America/Los_Angeles", "--root", str(root), "--brand", str(brand),
                 "--event", str(event)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertFalse(payload["publish"])
            self.assertEqual(payload["events"], ["2026-11-14-holiday-sale"])
            saved = json.loads((root / "brands" / "example" / "content" / "queue.json").read_text(encoding="utf-8"))
            self.assertFalse(saved["publish"])
            self.assertEqual(saved["events"][0]["target_date"], "2026-12-01")
            self.assertEqual(saved["events"][0]["filename_date"], "2026-11-14")
            self.assertIn("Publish: no", (root / "brands" / "example" / "content" / "calendar.md").read_text(encoding="utf-8"))

    def test_publish_help_has_no_secret_flag(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "publish", "--help"],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("approve-publish", result.stdout)
        self.assertNotIn("api-key", result.stdout.lower())
        self.assertNotIn("token", result.stdout.lower())

    def test_guides_and_routines_name_the_validator_limits(self):
        guides = ROOT / "integrations" / "grok-bot"
        x_guide = (guides / "platforms" / "x.md").read_text(encoding="utf-8")
        linkedin = (guides / "platforms" / "linkedin.md").read_text(encoding="utf-8")
        instagram = (guides / "platforms" / "instagram.md").read_text(encoding="utf-8")
        self.assertIn("280", x_guide)
        self.assertIn("25,000", x_guide)
        self.assertIn("23", x_guide)
        self.assertIn("3,000", linkedin)
        self.assertIn("2,200", instagram)
        self.assertIn("5 or fewer", instagram)
        self.assertIn("30", instagram)
        self.assertIn("20", instagram)
        weekly = (guides / "routines" / "weekly-content-batch.md").read_text(encoding="utf-8")
        daily = (guides / "routines" / "daily-x-idea.md").read_text(encoding="utf-8")
        self.assertIn("0 7 * * 1", weekly)
        self.assertIn("content_queue.py", weekly)
        self.assertIn("events/", weekly)
        self.assertIn("0 8 * * 1-5", daily)
        skill = (guides / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("events/", skill)
        self.assertIn("filename", skill.lower())


if __name__ == "__main__":
    unittest.main()
