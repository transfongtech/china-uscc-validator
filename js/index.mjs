import cjs from "./index.cjs";

export const {
  USCC_CHARSET,
  USCC_WEIGHTS,
  AUTHORITIES,
  ENTITY_TYPES,
  PROVINCES,
  CITIES,
  normalizeUscc,
  computeCheckDigit,
  validateUscc,
  decodeUscc,
} = cjs;

export default cjs;
