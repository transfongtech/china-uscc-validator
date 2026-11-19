"use strict";

const USCC_CHARSET = "0123456789ABCDEFGHJKLMNPQRTUWXY";
const USCC_WEIGHTS = Object.freeze([1, 3, 9, 27, 19, 26, 16, 17, 20, 29, 25, 13, 8, 24, 10, 30, 28]);

const AUTHORITIES = Object.freeze({
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
  "Y": "Other Statutory Authority"
});

const ENTITY_TYPES = Object.freeze({
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
  "Y1": "Other Entity"
});

const PROVINCES = Object.freeze({
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
  "65": "Xinjiang Autonomous Region"
});

const CITIES = Object.freeze({
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
  "5101": "Chengdu City"
});

function normalizeUscc(raw) {
  if (raw === null || raw === undefined) return "";
  return String(raw).replace(/[\s-]+/g, "").toUpperCase();
}

function computeCheckDigit(prefix17) {
  const normalized = normalizeUscc(prefix17);
  if (normalized.length !== 17) return null;
  let total = 0;
  for (let i = 0; i < 17; i += 1) {
    const val = USCC_CHARSET.indexOf(normalized.charAt(i));
    if (val === -1) return null;
    total += val * USCC_WEIGHTS[i];
  }
  const rem = 31 - (total % 31);
  return rem === 31 ? "0" : USCC_CHARSET.charAt(rem);
}

function buildDecoded(code) {
  const authorityCode = code.charAt(0);
  const entityTypeCode = code.slice(0, 2);
  const regionCode = code.slice(2, 8);
  const provinceCode = code.slice(2, 4);
  const cityCode = code.slice(2, 6);
  const organizationCode = code.slice(8, 17);
  const provinceName = PROVINCES[provinceCode];
  const cityName = CITIES[cityCode] || null;

  return {
    authorityCode,
    authorityName: AUTHORITIES[authorityCode] || "Registered Administrative Organ",
    entityTypeCode,
    entityTypeName: ENTITY_TYPES[entityTypeCode] || `Legal Entity Category ${entityTypeCode}`,
    regionCode,
    provinceCode,
    provinceName,
    cityCode,
    cityName,
    jurisdictionLabel: cityName ? `${cityName}, ${provinceName}` : provinceName,
    organizationCode,
    checkDigit: code.charAt(17)
  };
}

function invalidResult(code, error, expectedCheckDigit = null, actualCheckDigit = null) {
  return {
    valid: false,
    code,
    error,
    expectedCheckDigit,
    actualCheckDigit,
    decoded: null
  };
}

function validateUscc(raw) {
  const code = normalizeUscc(raw);
  if (!code) {
    return invalidResult(code, "USCC must not be empty.");
  }
  if (code.length !== 18) {
    return invalidResult(code, `USCC must be exactly 18 characters long (got ${code.length}).`);
  }
  for (let i = 0; i < 18; i += 1) {
    const ch = code.charAt(i);
    if (USCC_CHARSET.indexOf(ch) === -1) {
      return invalidResult(
        code,
        `Invalid character '${ch}' at position ${i + 1}. GB 32100-2015 excludes I, O, S, V, Z and symbols.`
      );
    }
  }
  const expected = computeCheckDigit(code.slice(0, 17));
  const actual = code.charAt(17);
  if (actual !== expected) {
    return invalidResult(
      code,
      `Checksum mismatch under GB 32100-2015 MOD 31-3: expected '${expected}', got '${actual}'.`,
      expected,
      actual
    );
  }
  const provinceCode = code.slice(2, 4);
  if (!PROVINCES[provinceCode]) {
    return invalidResult(
      code,
      `Unrecognized Mainland China province code '${provinceCode}' in positions 3-4.`,
      expected,
      actual
    );
  }
  return {
    valid: true,
    code,
    error: null,
    expectedCheckDigit: expected,
    actualCheckDigit: actual,
    decoded: buildDecoded(code)
  };
}

function decodeUscc(raw) {
  const result = validateUscc(raw);
  if (!result.valid) {
    throw new Error(result.error);
  }
  return result.decoded;
}

module.exports = {
  USCC_CHARSET,
  USCC_WEIGHTS,
  AUTHORITIES,
  ENTITY_TYPES,
  PROVINCES,
  CITIES,
  normalizeUscc,
  computeCheckDigit,
  validateUscc,
  decodeUscc
};
