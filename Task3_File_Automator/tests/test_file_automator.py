"""
Basic unit tests for file_automator.py

Run with:
    python -m unittest tests/test_file_automator.py -v
(run from the project root directory)
"""

import shutil
import sys
import tempfile
import unittest
from pathlib import Path

# Allow importing file_automator.py from the project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import file_automator as fa  # noqa: E402


class TestGetCategory(unittest.TestCase):
    def test_known_extension(self):
        self.assertEqual(fa.get_category(Path("photo.jpg")), "Images")
        self.assertEqual(fa.get_category(Path("report.pdf")), "Documents")
        self.assertEqual(fa.get_category(Path("script.py")), "Scripts")

    def test_unknown_extension_defaults_to_others(self):
        self.assertEqual(fa.get_category(Path("mystery.xyz")), "Others")


class TestPatternExtraction(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def _write(self, name, content):
        path = self.tmp_dir / name
        path.write_text(content, encoding="utf-8")
        return path

    def test_email_extraction(self):
        f = self._write("a.txt", "Reach me at test@example.com please.")
        rows = fa.extract_matches(f, fa.logging.getLogger("test"))
        emails = [r["match_value"] for r in rows if r["match_type"] == "email"]
        self.assertIn("test@example.com", emails)

    def test_transaction_id_extraction(self):
        f = self._write("b.txt", "Payment ref TXN123456 confirmed.")
        rows = fa.extract_matches(f, fa.logging.getLogger("test"))
        txns = [r["match_value"] for r in rows if r["match_type"] == "transaction_id"]
        self.assertIn("TXN123456", txns)

    def test_ip_extraction(self):
        f = self._write("c.txt", "Blocked login from 192.168.1.10")
        rows = fa.extract_matches(f, fa.logging.getLogger("test"))
        ips = [r["match_value"] for r in rows if r["match_type"] == "ip_address"]
        self.assertIn("192.168.1.10", ips)

    def test_no_matches_returns_empty(self):
        f = self._write("d.txt", "Nothing interesting here.")
        rows = fa.extract_matches(f, fa.logging.getLogger("test"))
        self.assertEqual(rows, [])


class TestUniqueDestination(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_no_collision_returns_same_path(self):
        target = self.tmp_dir / "file.txt"
        self.assertEqual(fa.unique_destination(target), target)

    def test_collision_renames_file(self):
        target = self.tmp_dir / "file.txt"
        target.write_text("existing")
        new_path = fa.unique_destination(target)
        self.assertNotEqual(new_path, target)
        self.assertTrue(new_path.stem.startswith("file_"))


if __name__ == "__main__":
    unittest.main()
