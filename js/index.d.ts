export declare const USCC_CHARSET: string;
export declare const USCC_WEIGHTS: readonly number[];
export declare const AUTHORITIES: Readonly<Record<string, string>>;
export declare const ENTITY_TYPES: Readonly<Record<string, string>>;
export declare const PROVINCES: Readonly<Record<string, string>>;
export declare const CITIES: Readonly<Record<string, string>>;

export interface DecodedUscc {
  authorityCode: string;
  authorityName: string;
  entityTypeCode: string;
  entityTypeName: string;
  regionCode: string;
  provinceCode: string;
  provinceName: string;
  cityCode: string;
  cityName: string | null;
  jurisdictionLabel: string;
  organizationCode: string;
  checkDigit: string;
}

export interface UsccValidationResult {
  valid: boolean;
  code: string;
  error: string | null;
  expectedCheckDigit: string | null;
  actualCheckDigit: string | null;
  decoded: DecodedUscc | null;
}

export declare function normalizeUscc(raw: string | null | undefined): string;
export declare function computeCheckDigit(prefix17: string): string | null;
export declare function validateUscc(raw: string | null | undefined): UsccValidationResult;
export declare function decodeUscc(raw: string | null | undefined): DecodedUscc;
