import argparse
import unittest

from pr_why.cli import explain


class ExplainTests(unittest.TestCase):
    def test_offline_summary_counts_changes_and_paths(self):
        diff = "diff --git a/a.py b/a.py\n+++ b/a.py\n+added\n-removed\n"
        args = argparse.Namespace(api_key=None, base_url="", model="", max_chars=100)
        report = explain(diff, args)
        self.assertIn("1 file(s)", report)
        self.assertIn("1 addition(s)", report)
        self.assertIn("1 deletion(s)", report)
        self.assertIn("a.py", report)

    def test_empty_diff_is_rejected(self):
        args = argparse.Namespace(api_key=None, base_url="", model="", max_chars=100)
        with self.assertRaises(ValueError):
            explain("  ", args)


if __name__ == "__main__":
    unittest.main()
