import tempfile
import unittest
from pathlib import Path
from demo import generate, parse_amount


class PortfolioDemoTests(unittest.TestCase):
    def test_records_and_reconciliation(self):
        with tempfile.TemporaryDirectory() as folder:
            report = generate(Path(folder))
            self.assertEqual(report["input_rows"], 6)
            self.assertEqual(report["valid_rows"], 3)
            self.assertEqual(report["rejected_rows"], 3)
            self.assertEqual(report["reconciliation_statuses"], {
                "matched": 1, "partial": 1, "unpaid": 1, "unmatched_payment": 1
            })
            self.assertTrue((Path(folder) / "quality_summary.json").is_file())

    def test_invalid_amount(self):
        for value in ["NaN", "-2.00", "1.234", "oops"]:
            with self.assertRaises(ValueError):
                parse_amount(value)


if __name__ == "__main__":
    unittest.main()
