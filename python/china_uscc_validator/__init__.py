"""Zero-dependency validator and decoder for China's 18-digit USCC (GB 32100-2015)."""

from .validator import (
    AUTHORITIES,
    CHARSET,
    CITIES,
    ENTITY_TYPES,
    PROVINCES,
    WEIGHTS,
    compute_check_digit,
    decode_uscc,
    normalize_uscc,
    validate_uscc,
)

__version__ = "1.0.0"

__all__ = [
    "__version__",
    "CHARSET",
    "WEIGHTS",
    "AUTHORITIES",
    "ENTITY_TYPES",
    "PROVINCES",
    "CITIES",
    "normalize_uscc",
    "compute_check_digit",
    "validate_uscc",
    "decode_uscc",
]
