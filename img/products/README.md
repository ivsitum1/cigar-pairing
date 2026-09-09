# Fotografije proizvoda

Ovdje završavaju obrađene slike cigara i boca:

    public/img/products/cigars/<id cigare>.webp
    public/img/products/drinks/<id pića>.webp

Ne uređuju se ručno. Nastaju u tri koraka, sva se pokreću **lokalno**
(prvi dva traže mrežu prema dućanima):

    python scripts/attach-product-images.py   # adrese → src/data/productImages.json
    python scripts/fetch-product-images.py    # preuzimanje → scripts/output/product-images/
    python scripts/normalize-product-images.py  # cutout → ovdje + productImagesLocal.json

`attach` puni popis dućanskih URL-ova (`productImages.json`). `fetch` sprema
originale u `scripts/output/product-images/` (ne ide u git — tuđe fotografije
u punoj veličini). `normalize` im makne podlogu, izreže proizvod, poravna
svjetlinu i spremi WebP s prozirnošću, a popis upiše u
`src/data/productImagesLocal.json`.

Dok lokalnog manifesta nema (prazni `cigars`/`drinks`), aplikacija koristi
dućanske URL-ove iz `productImages.json` — kartica i dalje ima sliku.
