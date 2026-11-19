"""Synthetic identity, import and action-budget regressions; no network access."""
import csv
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import browser_queue
import import_linkedin_export
import save_connections

ALICE = "https://www.linkedin.com/in/alice/"
BOB = "https://www.linkedin.com/in/bob/"
CAROL = "https://www.linkedin.com/in/carol/"


class InventoryWorkflowTests(unittest.TestCase):
    def test_existing_checkpoint_requires_matching_string_identity(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            self.assertEqual(browser_queue.read_state(directory, "owner")[1], {})
            checkpoint = directory / "checkpoint.json"
            for state in ({}, {"account": None}, {"account": 42},
                          {"account": "someone-else"}, [],
                          {"inspected_urls": [ALICE]}):
                with self.subTest(state=state):
                    checkpoint.write_text(json.dumps(state), encoding="utf-8")
                    with self.assertRaisesRegex(ValueError, "requested account"):
                        browser_queue.read_state(directory, "owner")
            checkpoint.write_text(json.dumps({"account": "OWNER", "inspected_urls": [ALICE]}))
            self.assertEqual(browser_queue.read_state(directory, "owner")[2]["inspected"], {ALICE})
            checkpoint.write_text('{"account":')
            with self.assertRaises(ValueError):
                browser_queue.read_state(directory, "owner")

    def test_queue_excludes_completed_profiles_and_honors_budget_and_blocker(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            directory = root / "temp" / "owner"
            save_connections.merge(directory / "connections.csv", [
                save_connections.normalize({"linkedin_permalink": url})
                for url in (ALICE, BOB, CAROL)
            ])
            checkpoint = directory / "checkpoint.json"
            state = {"account": "owner", "inspected_urls": [ALICE],
                     "inaccessible_urls": [BOB], "pending_urls": [ALICE, BOB, CAROL]}
            def run(*options):
                output = io.StringIO()
                with patch.object(browser_queue, "ROOT", root), patch.object(
                    sys, "argv", ["browser_queue.py", "next-batch", "--account", "owner", *options]
                ), redirect_stdout(output):
                    browser_queue.main()
                return json.loads(output.getvalue())
            checkpoint.write_text(json.dumps(state))
            result = run("--actions-used", "26")
            self.assertEqual(result["profiles"], [CAROL])
            self.assertEqual(result["estimated_actions"], 4)
            self.assertEqual(result["pending"], 1)
            self.assertEqual(run("--actions-used", "27")["profiles"], [])
            state["blocker"] = "verification required"
            checkpoint.write_text(json.dumps(state))
            self.assertEqual(run()["profiles"], [])

    def test_export_reimport_preserves_enrichment_and_deduplicates(self):
        export = ('Notes from export\n\nFirst Name,Last Name,URL,Email Address\n'
                  'Alice,Example,https://linkedin.com/in/ALICE,alice@example.com\n'
                  'Alice,Example,https://www.linkedin.com/in/alice/,\n'
                  'Bad,URL,https://example.com/in/bad/,\n')
        rows, skipped = import_linkedin_export.read_export(io.StringIO(export))
        self.assertEqual((len(rows), skipped), (1, 1))
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "connections.csv"
            save_connections.merge(path, rows, fill_missing=True)
            save_connections.merge(path, [save_connections.normalize({
                "linkedin_permalink": ALICE, "name": "Observed Alice", "followers": "42"
            })])
            before = path.read_bytes()
            save_connections.merge(path, rows, fill_missing=True)
            self.assertEqual(path.read_bytes(), before)
            with path.open(newline="") as source:
                actual = list(csv.DictReader(source))
            self.assertEqual(actual[0]["name"], "Observed Alice")
            self.assertEqual(actual[0]["email"], "alice@example.com")
            self.assertEqual(actual[0]["followers"], "42")
        with self.assertRaisesRegex(ValueError, "Missing Connections.csv header"):
            import_linkedin_export.read_export(io.StringIO(""))
        with self.assertRaisesRegex(ValueError, "Unexpected column count"):
            import_linkedin_export.read_export(io.StringIO("First Name,Last Name,URL\nAlice,Only\n"))


if __name__ == "__main__":
    unittest.main()
