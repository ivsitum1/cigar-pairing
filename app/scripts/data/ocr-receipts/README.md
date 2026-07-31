# OCR receipt fixtures (HR shops)

Photos + transcribed text for training / regression of `receiptParse`.

| File | Shop | Notes |
|------|------|-------|
| `camelot-havana-2026-07-10.png` | Camelot d.o.o. / Havana, Frankopanska 22 | Table with `/24` box counts, `1,00 Kom` |
| `tobacco-shop-5-2023-07-29.png` | Tobacco shop 5 / PJ7 Branimirova | Mixed cigars + candy; SKUs `CR…` |
| `tobacco-shop-5-2024-07-30.png` | Tobacco shop 5 | Bundle qty `10 KOM`, La Estrella |

Transcriptions (ideal OCR) live in `*.ocr.txt` next to each photo. Unit tests use those texts against `cigars.json`.
