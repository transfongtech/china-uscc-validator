"""Unit tests for china_uscc_validator Python package and CLI."""

import json
import subprocess
import sys
import unittest

from china_uscc_validator import (
    CHARSET,
    compute_check_digit,
    decode_uscc,
    normalize_uscc,
    validate_uscc,
)
from china_uscc_validator.__main__ import main as cli_main

VERIFIED_SAMPLES = [
    ("91320191250002463L", "Jiangsu Province", "Nanjing City"),
    ("91320100MADM013F56", "Jiangsu Province", "Nanjing City"),
    ("91370214MAKDUGGUXP", "Shandong Province", "Qingdao City"),
    ("91310113671164292D", "Shanghai Municipality", "Shanghai Urban Districts"),
    ("91320200674440635K", "Jiangsu Province", "Wuxi City"),
]


class TestChinaUsccValidator(unittest.TestCase):
    def test_verified_real_entities_pass_and_decode(self) -> None:
        for uscc, expected_prov, expected_city in VERIFIED_SAMPLES:
            res = validate_uscc(uscc)
            self.assertTrue(res["valid"], f"Expected {uscc} valid, got {res}")
            self.assertIsNone(res["error"])
            dec = res["decoded"]
            self.assertEqual(dec["authority_code"], "9")
            self.assertEqual(dec["entity_type_code"], "91")
            self.assertEqual(dec["province_name"], expected_prov)
            self.assertEqual(dec["city_name"], expected_city)

    def test_rem_31_maps_to_zero_check_digit(self) -> None:
        base16 = "9132010000000000"
        zero_prefix = next(base16 + ch for ch in CHARSET if compute_check_digit(base16 + ch) == "0")
        res = validate_uscc(zero_prefix + "0")
        self.assertTrue(res["valid"])
        self.assertEqual(res["expected_check_digit"], "0")

    def test_whitespace_hyphen_and_lowercase_normalization(self) -> None:
        res = validate_uscc(" 91320191-250002463l ")
        self.assertEqual(normalize_uscc(" 91320191-250002463l "), "91320191250002463L")
        self.assertTrue(res["valid"])
        self.assertEqual(decode_uscc("91320191250002463L")["province_code"], "32")

    def test_invalid_check_digit_reports_expected_character(self) -> None:
        res = validate_uscc("91320191250002463A")
        self.assertFalse(res["valid"])
        self.assertEqual(res["expected_check_digit"], "L")
        self.assertEqual(res["actual_check_digit"], "A")
        self.assertIn("expected 'L'", res["error"])
        with self.assertRaises(ValueError):
            decode_uscc("91320191250002463A")

    def test_excluded_letters_and_bad_length_and_unknown_province(self) -> None:
        for ch in ("I", "O", "S", "V", "Z"):
            bad = f"913201912500024{ch}3L"
            res = validate_uscc(bad)
            self.assertFalse(res["valid"])
            self.assertIn("excludes I, O, S, V, Z", res["error"])

        short_res = validate_uscc("913201")
        self.assertFalse(short_res["valid"])
        self.assertIn("18 characters", short_res["error"])

        bad_prov_prefix = "91990191250002463"
        bad_prov = bad_prov_prefix + compute_check_digit(bad_prov_prefix)
        prov_res = validate_uscc(bad_prov)
        self.assertFalse(prov_res["valid"])
        self.assertIn("Unrecognized Mainland China province code '99'", prov_res["error"])

    def test_cli_exit_codes_and_json_output(self) -> None:
        self.assertEqual(cli_main(["91320191250002463L"]), 0)
        self.assertEqual(cli_main(["91320191250002463A"]), 1)
        proc = subprocess.run(
            [sys.executable, "-m", "china_uscc_validator", "91320191250002463L", "--json"],
            capture_output=True,
            text=True,
            check=True,
        )
        payload = json.loads(proc.stdout)
        self.assertTrue(payload["valid"])
        self.assertEqual(payload["decoded"]["province_name"], "Jiangsu Province")


if __name__ == "__main__":
    unittest.main()
