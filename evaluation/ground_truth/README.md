# Ground Truth Dataset

## Purpose

Phase 2 dataset scaffold for Production OCR.

The current GCCK dataset contains:

- members: 5
- PDF document instances: 19
- total pages discovered: 143

The PDF names `T1.pdf` ... `T4.pdf` are treated as **weekly document
instances**, not automatically as form IDs or form versions.

Current form profile used to generate the row/field template:

```text
T1/v1
```

## Files

### `manifest.json`

Inventory of all members, PDFs and page counts.

### `page_annotations.jsonl`

One JSON record per source page.

Each page contains fixed row slots and the canonical OCR fields.
Human annotators fill the values.

## Annotation rules

- Do not invent unreadable text.
- Use `null` when the field is genuinely blank or not readable.
- Preserve Vietnamese diacritics.
- Preserve capitalization, numbers, punctuation and technical codes when visible.
- Do not normalize business meaning during transcription.
- Keep `member_id`, `document_id`, `page`, and `row_number` unchanged.
- `active` means the row contains report data and is therefore eligible for OCR.
- Ground Truth is human verified; this file is only a scaffold.

## Important separation

```text
Phase 2
    build + verify Ground Truth

Phase 7
    OCR prediction

Phase 9
    compare predictions with Ground Truth
    ↓
    Character Accuracy
    Field Accuracy
    Row Accuracy
    Page Accuracy
```

## Recommended sampling strategy

Do not label only one employee.

Use a representative subset across:

```text
multiple members
multiple weekly PDFs
multiple pages
different handwriting
technical codes / numbers
blank rows
filled rows
```
