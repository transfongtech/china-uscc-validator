# china-uscc-validator

Zero-dependency **Python** and **JavaScript / TypeScript** validator, CLI, and jurisdiction decoder for China's 18-digit **Unified Social Credit Code** (`统一社会信用代码`, GB 32100-2015 / ISO 7064 MOD 31-3).

> Interactive browser tool (no installation required):
> **[Try the Free 0-Credit Online USCC Validator &rarr;](https://chinaentitycheck.com/tools/uscc-checker/)**

---

## What is a Chinese USCC (GB 32100-2015)?

Under China's *Three-Certificates-in-One* corporate reform, every legally registered enterprise in Mainland China carries an 18-character **Unified Social Credit Code (USCC)** replacing legacy business license numbers, organization codes, and tax IDs:

| Positions | Length | Field | Common Values |
| :--- | :---: | :--- | :--- |
| **1** | 1 | Registration Authority | `9` = SAMR (Market Regulation), `1` = Institutional Organ, `5` = Civil Affairs |
| **2** | 1 | Entity Category | `1` = Enterprise (`91`), `2` = Sole Proprietorship (`92`), `3` = Cooperative (`93`) |
| **3–8** | 6 | Administrative Division (`GB/T 2260`) | First 2 digits = province (e.g., `44` Guangdong, `32` Jiangsu, `33` Zhejiang, `31` Shanghai) |
| **9–17** | 9 | Organization Code | Unique 9-character legacy organization code |
| **18** | 1 | Check Digit | ISO 7064 MOD 31-3 weighted checksum across positions 1–17 |

### Checksum Formula (ISO 7064 MOD 31-3)

- **Alphabet (31 characters)**: `0123456789ABCDEFGHJKLMNPQRTUWXY` *(omits `I`, `O`, `S`, `V`, `Z` to prevent visual ambiguity with `1`, `0`, `5`, `2`)*
- **Position Weights (1–17)**: `[1, 3, 9, 27, 19, 26, 16, 17, 20, 29, 25, 13, 8, 24, 10, 30, 28]`
- **Calculation**:
  1. Compute $S = \sum_{i=0}^{16} \text{index}(c_i) \times w_i$
  2. Remainder $r = 31 - (S \bmod 31)$
  3. Expected check digit is `'0'` when $r = 31$, otherwise `alphabet[r]`.

---

## Python Usage

Requires Python 3.8+ with **zero third-party dependencies**.

```python
from china_uscc_validator import validate_uscc, decode_uscc, compute_check_digit

result = validate_uscc("91320191250002463L")
# {
#   "valid": True,
#   "code": "91320191250002463L",
#   "error": None,
#   "expected_check_digit": "L",
#   "actual_check_digit": "L",
#   "decoded": {
#     "authority_code": "9",
#     "authority_name": "State Administration for Market Regulation (SAMR)",
#     "entity_type_code": "91",
#     "entity_type_name": "Incorporated Enterprise (Ltd. / LLC / JSC)",
#     "region_code": "320191",
#     "province_name": "Jiangsu Province",
#     "city_name": "Nanjing City",
#     "jurisdiction_label": "Nanjing City, Jiangsu Province",
#     ...
#   }
# }

bad = validate_uscc("91320191250002463A")
# {"valid": False, "expected_check_digit": "L", "actual_check_digit": "A", ...}
```

### CLI Usage

```bash
python -m china_uscc_validator 91320191250002463L
python -m china_uscc_validator 91320191250002463L --json
```

Returns exit code `0` for valid USCCs and `1` for invalid codes.

---

## JavaScript / TypeScript Usage

Supports both **ESM** (`import`) and **CommonJS** (`require`) with built-in `.d.ts` TypeScript definitions and **zero runtime dependencies**.

```js
import { validateUscc, decodeUscc, computeCheckDigit } from "./js/index.mjs";

const res = validateUscc("91320191250002463L");
if (res.valid) {
  console.log(res.decoded.jurisdictionLabel); // "Nanjing City, Jiangsu Province"
}
```

```js
// CommonJS
const { validateUscc } = require("./js/index.cjs");
```

---

## Important Note: Format Validity vs. Active Legal Standing

A valid GB 32100-2015 checksum confirms only that an 18-digit USCC obeys China's statutory formatting math and maps to a real administrative division—it does **not** prove whether the supplier is currently **Active (`存续` / `在业`)**, **Revoked (`吊销`)**, **Cancelled (`注销`)**, or listed in Supreme People's Court dishonest debtor registries.

To complete statutory KYB verification in English without a Mainland `+86` phone number, GSXT slider CAPTCHA, or annual contract:

- **[Online USCC Validator & Jurisdiction Decoder (Free, 0 Credits)](https://chinaentitycheck.com/tools/uscc-checker/)** — browser version of this tool.
- **[How to Check Company Registration in China (Official SAMR & GSXT Guide)](https://chinaentitycheck.com/guides/china-company-registration-search-samr-gsxt-guide/)** — step-by-step English guide to interpreting SAMR statuses, paid-in capital, and customs records.
- **[Live Chinese Company Verification (`$0` Free Screen / `$39` Essential / `$149` Full)](https://chinaentitycheck.com/?utm_source=github&utm_medium=oss&utm_campaign=china_uscc_validator)** — query official SAMR filings, Supreme People's Court litigation, and GACC customs registration.
- **[Public Chinese Entity Directory](https://chinaentitycheck.com/directory/)** — browse indexed verified exporters and manufacturers.

---

## Running Tests

```bash
PYTHONPATH=python python3 -m unittest discover -s tests -v
node --test tests/test_uscc.mjs
```

## License

MIT &copy; 2026 [Transfong Ventures Pte. Ltd.](https://www.transfong.com/)
