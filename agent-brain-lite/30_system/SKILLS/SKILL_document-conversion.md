---
name: document-conversion
description: Use for file format conversion between docx/xlsx/txt/md only Triggers include: document conversion, Word to txt, docx to md, Excel to markdown, convert document.
version: 1.1
last_updated: 2026-03-30
domain: tools
tokens: ~750
triggers:
  - document conversion
  - Word to txt
  - docx to md
  - Excel to markdown
  - convert document
requires_packages: [python-docx, openpyxl]
reference_files: []
pipeline_position: []
---

# Skill: Document conversion (Word, Excel ↔ txt, md)

Converts between Word (.docx), Excel (.xlsx), plain text (.txt), and Markdown (.md). Use when the user asks to convert documents, export to txt/md, create Word/Excel from text or markdown, "pretvori u txt", "u markdown", "iz Worda u tekst", "iz Excela u md", or similar.

## When to use

- User requests conversion between Word, Excel, txt, or md
- Keywords: "pretvori Word u txt", "excel u markdown", "docx u md", "txt u docx", "convert document", "export to text", "export to markdown", "iz .docx u .txt", "obrnuto"

## Prerequisites

- Python 3.8+
- Dependencies: `pip install -r 40_operations/scripts/document_conversion/requirements.txt` (python-docx, openpyxl)

## Step-by-step procedure

1. **Identify input and desired output format**
   - Input: path to .docx, .xlsx, .txt, or .md
   - Output: path (optional) and/or format (txt, md, docx, xlsx)

2. **Run the conversion script**
   ```bash
   # Output path optional; format inferred from extension or --to
   python 40_operations/scripts/document_conversion/convert_documents.py <input_path> [output_path]
   python 40_operations/scripts/document_conversion/convert_documents.py <input_path> --to txt|md|docx|xlsx
   ```

3. **Report result**
   - Script prints the output file path on success. Confirm to the user where the file was written.

## Supported conversions

| From   | To       |
|--------|----------|
| .docx  | .txt, .md |
| .xlsx  | .txt, .md |
| .txt   | .docx, .xlsx, .md |
| .md    | .docx, .xlsx, .txt |

Direct Word ↔ Excel is not supported (structure mismatch). Use txt or md as intermediate.

## Honesty and grounding checkpoints

- Tag outputs as `[EXTRACTED]`, `[VERIFIED]`, `[INFERRED]`, `[ASSUMPTION]`, or `[BLANK]`.
- Use `[VERIFIED]` only with evidence from code execution, user data, or authoritative documentation.
- If required inputs are missing, use `[BLANK]` and list what to supply next.
- Do not fabricate statistics, citations, guideline quotes, or tool outputs.

## Examples

**Input:** "Pretvori docx u markdown; zadrži tablice što je moguće."  
**Output:** "Koristim dogovoreni tok konverzije; struktura nakon konverzije `[VERIFIED]` usporedbom; format izvan podrške `[BLANK]` uz alternativu."

## Verification

- [ ] Input file exists and extension is supported
- [ ] Dependencies installed if first run
- [ ] Output path writable; if omitted, same directory with new extension is used

## Script location

- `40_operations/scripts/document_conversion/convert_documents.py`
- `40_operations/scripts/document_conversion/requirements.txt`
- `40_operations/scripts/document_conversion/README.md`

## Related Hubs

- [Skill registry](registry.json)
- [Skills index](../30_system/docs/indexes/SKILLS_INDEX.md)
- [Task optimization check](../30_system/docs/TASK_OPTIMIZATION_CHECK.md)
- [Workspace graph map](../30_system/docs/GRAPH_CONNECTIVITY_MAP.md)
- [Folder index hub](../docs/FOLDER_INDEX.md)
- [All notes index](../docs/ALL_NOTES_INDEX.md)
- [Graph connectivity map](../docs/GRAPH_CONNECTIVITY_MAP.md)
