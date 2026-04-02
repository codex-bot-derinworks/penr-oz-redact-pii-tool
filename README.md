# penr-oz-redact-pii-tool

Offline CLI tool to securely redact PII from PDF tax-like documents using Python.

## Features

- Secure PDF redaction using PyMuPDF `add_redact_annot` plus `apply_redactions`
- Default redaction coverage for names, addresses, ZIP codes, SSNs, EINs/TINs, employer state IDs, W-2 control numbers, emails, and phone numbers
- Word-level extraction with line reconstruction to catch multi-token matches, including split SSN and EIN fields
- Optional OCR fallback for scanned pages using `pdf2image` and `pytesseract`
- Local-only processing with no external API calls

## Installation

Recommended Python version: `3.10`

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

OCR fallback also requires native tools:

- `tesseract` must be installed and available on `PATH`
- `poppler` must be installed so `pdf2image` can render PDF pages

## Usage

```bash
pii-redact input.pdf --output out.pdf
pii-redact input.pdf --output out.pdf --types ssn,email,phone --ocr-fallback
pii-redact input.pdf --output out.pdf --types name,address,zip,state_id,control_number
```

Defaults:

- PII types: all supported types
- OCR fallback: disabled

## Development

Run tests with:

```bash
pytest
```
