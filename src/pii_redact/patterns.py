from __future__ import annotations

import re


SUPPORTED_PII_TYPES = (
    "name",
    "address",
    "zip",
    "ssn",
    "ein",
    "state_id",
    "control_number",
    "email",
    "phone",
)
DEFAULT_PII_TYPES = SUPPORTED_PII_TYPES

TYPE_ALIASES = {
    "tin": "ein",
    "zipcode": "zip",
    "zip_code": "zip",
}

PII_PATTERNS: dict[str, re.Pattern[str]] = {
    "ssn": re.compile(r"\b(?:\d{3}-\d{2}-\d{4}|\d{9})\b"),
    "ein": re.compile(r"\b(?:\d{2}-\d{7}|\d{9})\b"),
    "email": re.compile(r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b"),
    "phone": re.compile(
        r"\b(?:\+?1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)\d{3}[-.\s]?\d{4}\b"
    ),
    "zip": re.compile(r"\b\d{5}(?:-\d{4})?\b"),
    "state_id": re.compile(r"\b[A-Z0-9-]{4,20}\b"),
    "control_number": re.compile(r"\b[A-Z0-9-]{4,20}\b"),
}


def normalize_pii_types(raw_types: list[str] | None) -> list[str]:
    if not raw_types:
        return list(DEFAULT_PII_TYPES)

    normalized: list[str] = []
    for pii_type in raw_types:
        value = TYPE_ALIASES.get(pii_type.strip().lower(), pii_type.strip().lower())
        if not value:
            continue
        if value not in SUPPORTED_PII_TYPES:
            supported = ", ".join((*SUPPORTED_PII_TYPES, *TYPE_ALIASES))
            raise ValueError(f"Unsupported PII type '{pii_type}'. Supported: {supported}")
        if value not in normalized:
            normalized.append(value)
    return normalized
