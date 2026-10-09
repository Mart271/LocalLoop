"""Prevent the exploratory OCR metric from crediting missing or corrupted field text."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "ocr"))
from compare import expected, score


class OcrScoring(unittest.TestCase):
    def setUp(self):
        self.record = {"vendor_name": "Bluefin Office Supplies Co.", "invoice_number": "BOS-2026-0001",
                       "invoice_date": "2026-01-05", "currency": "PHP", "subtotal": "1000.00", "tax": "120.00", "total": "1120.00"}

    def test_exact_rendered_fields_are_credited_without_case_or_punctuation(self):
        text = " ".join(str(v) for v in expected(self.record).values()).upper()
        self.assertTrue(all(score(text, self.record).values()))

    def test_missing_vendor_and_corrupted_invoice_are_not_credited(self):
        values = expected(self.record)
        text = " ".join(str(v) for k, v in values.items() if k not in {"vendor_name", "invoice_number"})
        text += " BOS-2026-9001"
        result = score(text, self.record)
        self.assertFalse(result["vendor_name"])
        self.assertFalse(result["invoice_number"])
        self.assertTrue(result["total"])

    def test_empty_output_never_passes(self):
        self.assertFalse(any(score("", self.record).values()))


if __name__ == "__main__":
    unittest.main()
