import test from "node:test";
import assert from "node:assert/strict";
import { createRequire } from "node:module";

import * as esm from "../js/index.mjs";

const require = createRequire(import.meta.url);
const cjs = require("../js/index.cjs");

const VERIFIED_SAMPLES = [
  ["91320191250002463L", "Jiangsu Province", "Nanjing City"],
  ["91320100MADM013F56", "Jiangsu Province", "Nanjing City"],
  ["91370214MAKDUGGUXP", "Shandong Province", "Qingdao City"],
  ["91310113671164292D", "Shanghai Municipality", "Shanghai Urban Districts"],
  ["91320200674440635K", "Jiangsu Province", "Wuxi City"],
];

for (const [label, api] of [["ESM", esm], ["CJS", cjs]]) {
  test(`${label}: verified China USCCs pass and decode jurisdiction`, () => {
    for (const [code, provinceName, cityName] of VERIFIED_SAMPLES) {
      const res = api.validateUscc(code);
      assert.equal(res.valid, true, `Expected ${code} valid`);
      assert.equal(res.error, null);
      assert.equal(res.decoded.authorityCode, "9");
      assert.equal(res.decoded.entityTypeCode, "91");
      assert.equal(res.decoded.provinceName, provinceName);
      assert.equal(res.decoded.cityName, cityName);
    }
  });

  test(`${label}: remainder 31 maps to check digit '0'`, () => {
    const base16 = "9132010000000000";
    let zeroPrefix = null;
    for (const ch of api.USCC_CHARSET) {
      if (api.computeCheckDigit(base16 + ch) === "0") {
        zeroPrefix = base16 + ch;
        break;
      }
    }
    assert.ok(zeroPrefix, "Should construct a zero-check-digit prefix");
    const res = api.validateUscc(`${zeroPrefix}0`);
    assert.equal(res.valid, true);
    assert.equal(res.expectedCheckDigit, "0");
  });

  test(`${label}: normalization, invalid checksum, excluded charset, and unknown province`, () => {
    assert.equal(api.normalizeUscc(" 91320191-250002463l "), "91320191250002463L");
    assert.equal(api.decodeUscc("91320191-250002463l").provinceCode, "32");

    const badSum = api.validateUscc("91320191250002463A");
    assert.equal(badSum.valid, false);
    assert.equal(badSum.expectedCheckDigit, "L");
    assert.equal(badSum.actualCheckDigit, "A");
    assert.throws(() => api.decodeUscc("91320191250002463A"));

    for (const badChar of ["I", "O", "S", "V", "Z"]) {
      const res = api.validateUscc(`913201912500024${badChar}3L`);
      assert.equal(res.valid, false);
      assert.match(res.error, /excludes I, O, S, V, Z/);
    }

    assert.equal(api.validateUscc("913201").valid, false);

    const badProvPrefix = "91990191250002463";
    const badProv = badProvPrefix + api.computeCheckDigit(badProvPrefix);
    const badProvRes = api.validateUscc(badProv);
    assert.equal(badProvRes.valid, false);
    assert.match(badProvRes.error, /Unrecognized Mainland China province code '99'/);
  });
}
