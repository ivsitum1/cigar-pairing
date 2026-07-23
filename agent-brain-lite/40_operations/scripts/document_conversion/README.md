# Document conversion (Word, Excel ↔ txt, md)

Script: `convert_documents.py`

## Install

```bash
pip install -r requirements.txt
```

## Usage

```bash
# Infer output from path or default extension
python convert_documents.py report.docx
# -> report.txt

python convert_documents.py data.xlsx output.md
# -> output.md

# Force format with --to
python convert_documents.py notes.txt --to docx
# -> notes.docx

python convert_documents.py draft.md --to docx saved.docx
# -> saved.docx
```

## Supported conversions

| From   | To    |
|--------|--------|
| .docx  | .txt, .md |
| .xlsx  | .txt, .md |
| .txt   | .docx, .xlsx, .md |
| .md    | .docx, .xlsx, .txt |

Word/Excel are not converted directly to each other (structure differs).

## Related Hubs

- [Folder index hub](../../../30_system/docs/FOLDER_INDEX.md)
- [All notes index](../../../30_system/docs/ALL_NOTES_INDEX.md)
- [Graph connectivity map](../../../30_system/docs/GRAPH_CONNECTIVITY_MAP.md)
