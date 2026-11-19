"""Zero-dependency CLI entrypoint for china-uscc-validator."""

import argparse
import json
import sys
from typing import List, Optional

from .validator import validate_uscc


def main(argv: Optional[List[str]] = None) -> int:
    """Validate a Chinese USCC from the CLI and print JSON or human-readable output."""
    parser = argparse.ArgumentParser(
        prog="china_uscc_validator",
        description="Validate China's 18-digit Unified Social Credit Code (GB 32100-2015).",
    )
    parser.add_argument("uscc", help="18-character Unified Social Credit Code to validate")
    parser.add_argument("--json", action="store_true", help="Emit structured JSON result")
    args = parser.parse_args(argv)

    result = validate_uscc(args.uscc)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif result["valid"]:
        dec = result["decoded"]
        print(f"VALID   {result['code']}")
        print(f"  Authority : {dec['authority_code']} ({dec['authority_name']})")
        print(f"  Category  : {dec['entity_type_code']} ({dec['entity_type_name']})")
        print(f"  Region    : {dec['region_code']} ({dec['jurisdiction_label']})")
        print(f"  Org Code  : {dec['organization_code']}")
        print(f"  Checksum  : {dec['check_digit']} (MOD 31-3 verified)")
    else:
        print(f"INVALID {result['code']}: {result['error']}", file=sys.stderr)

    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
