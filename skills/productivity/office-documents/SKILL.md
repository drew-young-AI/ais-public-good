---
name: office-documents
type: skill
description: "Read and summarize Microsoft Office files: Word .docx, Excel .xlsx/.xls, PowerPoint .pptx, and PDFs."
version: 1.0.0
author: local
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Office, DOCX, XLSX, XLS, PPTX, PDF, Documents, Tables]
    related_skills: [powerpoint, ocr-and-documents]
---

# Office Documents

Use this skill whenever the user provides or references common Microsoft Office files:

- Word: `.docx`
- Excel: `.xlsx`, `.xls`
- PowerPoint: `.pptx`
- PDF: `.pdf`

## Default Extraction

Use `markitdown` first because it gives readable Markdown across Office formats:

```bash
python -m markitdown file.docx
python -m markitdown file.xlsx
python -m markitdown file.pptx
python -m markitdown file.pdf
```

## Format-Specific Checks

### Word

Use `python-docx` when paragraph/table structure matters:

```python
from docx import Document
doc = Document("file.docx")
for p in doc.paragraphs:
    print(p.text)
for table in doc.tables:
    for row in table.rows:
        print([cell.text for cell in row.cells])
```

### Excel

Use `openpyxl` for `.xlsx` and `xlrd` for legacy `.xls`.

```python
from openpyxl import load_workbook
wb = load_workbook("file.xlsx", data_only=True)
for ws in wb.worksheets:
    print("SHEET", ws.title)
    for row in ws.iter_rows(values_only=True):
        print(row)
```

### PowerPoint

Use the `powerpoint` skill for full slide work. For quick text extraction:

```bash
python -m markitdown file.pptx
```

## Rules

- Prefer structured parsers over OCR for Office files.
- Use OCR only for scanned PDFs or image-only documents.
- For spreadsheets, preserve sheet names, row/column context, formulas versus displayed values when relevant.
- For PowerPoint, include speaker notes when available and mention if visual layout may affect meaning.
- Do not claim a document is empty until checking for tables, notes, hidden sheets, and embedded text.
