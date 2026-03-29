from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import fitz

from .detector import Detection, detect_direct_text_pii, detect_pii, detect_widget_pii, extract_page_words
from .ocr import extract_ocr_words
from .patterns import normalize_pii_types


@dataclass(frozen=True)
class PageResult:
    page_number: int
    source: str
    detections: list[Detection]


@dataclass(frozen=True)
class RedactionResult:
    output_path: Path
    pages: list[PageResult]

    @property
    def total_redactions(self) -> int:
        return sum(len(page.detections) for page in self.pages)


def redact_pdf(
    input_path: str | Path,
    output_path: str | Path,
    pii_types: list[str] | None = None,
    ocr_fallback: bool = False,
) -> RedactionResult:
    input_path = Path(input_path)
    output_path = Path(output_path)
    normalized_types = normalize_pii_types(pii_types)

    pages: list[PageResult] = []
    fitz.TOOLS.mupdf_display_errors(False)
    fitz.TOOLS.mupdf_display_warnings(False)
    with fitz.open(input_path) as document:
        for page_number, page in enumerate(document):
            word_boxes = extract_page_words(page)
            page_widgets = list(page.widgets() or [])
            widget_detections = detect_widget_pii(page, normalized_types)
            widget_xrefs = {item.xref for item in widget_detections}
            source = "text"
            if widget_detections:
                source = "widget"
                detections = [item.detection for item in widget_detections]
            elif page_widgets:
                direct_types = [pii_type for pii_type in normalized_types if pii_type in {"ssn", "ein", "email", "phone"}]
                detections = detect_direct_text_pii(word_boxes, direct_types, source)
            elif word_boxes:
                detections = detect_pii(word_boxes, normalized_types, source)
            elif ocr_fallback:
                source = "ocr"
                ocr_words = extract_ocr_words(input_path, page_number, page.rect)
                detections = detect_pii(ocr_words, normalized_types, source)
            else:
                detections = []

            for detection in detections:
                page.add_redact_annot(detection.rect, fill=(0, 0, 0))
            if detections:
                page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE)
            if widget_xrefs:
                for widget in list(page.widgets() or []):
                    if widget.xref in widget_xrefs:
                        page.delete_widget(widget)

            pages.append(PageResult(page_number=page_number, source=source, detections=detections))

        output_path.parent.mkdir(parents=True, exist_ok=True)
        document.save(
            output_path,
            garbage=3,
            deflate=True,
        )

    return RedactionResult(output_path=output_path, pages=pages)
