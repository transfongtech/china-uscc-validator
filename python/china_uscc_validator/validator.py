"""GB 32100-2015 / ISO 7064 MOD 31-3 validation and jurisdiction decoding logic."""

import re
from typing import Any, Dict, Optional

CHARSET = "0123456789ABCDEFGHJKLMNPQRTUWXY"
WEIGHTS = (1, 3, 9, 27, 19, 26, 16, 17, 20, 29, 25, 13, 8, 24, 10, 30, 28)

AUTHORITIES: Dict[str, str] = {
    "1": "Institutional Organization Commission",
    "2": "Foreign Affairs Ministry",
    "3": "Ministry of Justice",
    "4": "Trade Union Organ",
    "5": "Ministry of Civil Affairs",
    "6": "Communist Youth League",
    "7": "All-China Women's Federation",
    "8": "All-China Federation of Industry and Commerce",
    "9": "State Administration for Market Regulation (SAMR)",
    "A": "Central Military Commission",
    "G": "Political and Legal Affairs Commission",
    "N": "Ministry of Agriculture and Rural Affairs",
    "Y": "Other Statutory Authority",
}

ENTITY_TYPES: Dict[str, str] = {
    "11": "Government / Party Organ",
    "12": "Public Institution",
    "13": "Social Group Managed by Public Organ",
    "19": "Other Organ Entity",
    "51": "Social Organization",
    "52": "Private Non-Enterprise Unit",
    "53": "Foundation",
    "59": "Other Civil Affairs Entity",
    "91": "Incorporated Enterprise (Ltd. / LLC / JSC)",
    "92": "Individual Sole Proprietorship",
    "93": "Farmers Professional Cooperative",
    "Y1": "Other Entity",
}

PROVINCES: Dict[str, str] = {
    "11": "Beijing Municipality",
    "12": "Tianjin Municipality",
    "13": "Hebei Province",
    "14": "Shanxi Province",
    "15": "Inner Mongolia Autonomous Region",
    "21": "Liaoning Province",
    "22": "Jilin Province",
    "23": "Heilongjiang Province",
    "31": "Shanghai Municipality",
    "32": "Jiangsu Province",
    "33": "Zhejiang Province",
    "34": "Anhui Province",
    "35": "Fujian Province",
    "36": "Jiangxi Province",
    "37": "Shandong Province",
    "41": "Henan Province",
    "42": "Hubei Province",
    "43": "Hunan Province",
    "44": "Guangdong Province",
    "45": "Guangxi Autonomous Region",
    "46": "Hainan Province",
    "50": "Chongqing Municipality",
    "51": "Sichuan Province",
    "52": "Guizhou Province",
    "53": "Yunnan Province",
    "54": "Tibet Autonomous Region",
    "61": "Shaanxi Province",
    "62": "Gansu Province",
    "63": "Qinghai Province",
    "64": "Ningxia Autonomous Region",
    "65": "Xinjiang Autonomous Region",
}

CITIES: Dict[str, str] = {
    "1101": "Beijing Urban Districts",
    "1201": "Tianjin Urban Districts",
    "3101": "Shanghai Urban Districts",
    "3201": "Nanjing City",
    "3202": "Wuxi City",
    "3204": "Changzhou City",
    "3205": "Suzhou City",
    "3301": "Hangzhou City",
    "3302": "Ningbo City",
    "3303": "Wenzhou City",
    "3307": "Jinhua / Yiwu City",
    "3502": "Xiamen City",
    "3702": "Qingdao City",
    "4401": "Guangzhou City",
    "4403": "Shenzhen City",
    "4406": "Foshan City",
    "4419": "Dongguan City",
    "4420": "Zhongshan City",
    "5001": "Chongqing Urban Districts",
    "5101": "Chengdu City",
}


def normalize_uscc(raw: str) -> str:
    """Strip whitespace/hyphens and convert a USCC string to uppercase."""
    if raw is None:
        return ""
    return re.sub(r"[\s-]+", "", str(raw)).upper()


def compute_check_digit(prefix17: str) -> str:
    """Compute the GB 32100-2015 ISO 7064 MOD 31-3 check digit for a 17-character prefix."""
    normalized = normalize_uscc(prefix17)
    if len(normalized) != 17:
        raise ValueError(f"Expected 17 characters before check digit, got {len(normalized)}.")
    total = 0
    for idx, ch in enumerate(normalized):
        val = CHARSET.find(ch)
        if val == -1:
            raise ValueError(f"Invalid character '{ch}' at position {idx + 1}.")
        total += val * WEIGHTS[idx]
    rem = 31 - (total % 31)
    return "0" if rem == 31 else CHARSET[rem]


def _build_decoded(code: str) -> Dict[str, Any]:
    auth_code = code[0]
    type_code = code[:2]
    region_code = code[2:8]
    province_code = code[2:4]
    city_code = code[2:6]
    org_code = code[8:17]
    province_name = PROVINCES[province_code]
    city_name = CITIES.get(city_code)
    return {
        "authority_code": auth_code,
        "authority_name": AUTHORITIES.get(auth_code, "Registered Administrative Organ"),
        "entity_type_code": type_code,
        "entity_type_name": ENTITY_TYPES.get(type_code, f"Legal Entity Category {type_code}"),
        "region_code": region_code,
        "province_code": province_code,
        "province_name": province_name,
        "city_code": city_code,
        "city_name": city_name,
        "jurisdiction_label": f"{city_name}, {province_name}" if city_name else province_name,
        "organization_code": org_code,
        "check_digit": code[17],
    }


def _invalid_result(
    code: str,
    error: str,
    expected_check_digit: Optional[str] = None,
    actual_check_digit: Optional[str] = None,
) -> Dict[str, Any]:
    return {
        "valid": False,
        "code": code,
        "error": error,
        "expected_check_digit": expected_check_digit,
        "actual_check_digit": actual_check_digit,
        "decoded": None,
    }


def validate_uscc(raw: str) -> Dict[str, Any]:
    """Validate an 18-character Unified Social Credit Code and decode its jurisdiction metadata."""
    code = normalize_uscc(raw)
    if not code:
        return _invalid_result(code, "USCC must not be empty.")
    if len(code) != 18:
        return _invalid_result(code, f"USCC must be exactly 18 characters long (got {len(code)}).")

    for idx, ch in enumerate(code):
        if ch not in CHARSET:
            return _invalid_result(
                code,
                f"Invalid character '{ch}' at position {idx + 1}. GB 32100-2015 excludes I, O, S, V, Z and symbols.",
            )

    expected = compute_check_digit(code[:17])
    actual = code[17]
    if actual != expected:
        return _invalid_result(
            code,
            f"Checksum mismatch under GB 32100-2015 MOD 31-3: expected '{expected}', got '{actual}'.",
            expected_check_digit=expected,
            actual_check_digit=actual,
        )

    prov_code = code[2:4]
    if prov_code not in PROVINCES:
        return _invalid_result(
            code,
            f"Unrecognized Mainland China province code '{prov_code}' in positions 3-4.",
            expected_check_digit=expected,
            actual_check_digit=actual,
        )

    return {
        "valid": True,
        "code": code,
        "error": None,
        "expected_check_digit": expected,
        "actual_check_digit": actual,
        "decoded": _build_decoded(code),
    }


def decode_uscc(raw: str) -> Dict[str, Any]:
    """Validate and return decoded USCC metadata, raising ValueError if invalid."""
    result = validate_uscc(raw)
    if not result["valid"]:
        raise ValueError(result["error"])
    return result["decoded"]
