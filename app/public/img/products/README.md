# Fotografije proizvoda

Ovdje zavrsavaju obradjene slike cigara i boca:

    public/img/products/cigars/<id cigare>.webp
    public/img/products/drinks/<id pica>.webp

Ne uredjuju se rucno. Nastaju u dva koraka, oba se pokrecu **lokalno** (prvi
trazi mrezu prema duckanima):

    python3 scripts/scrape-product-images.py --kind cigars
    python3 scripts/normalize-product-images.py

Prvi korak sprema originale u `scripts/output/product-images/raw/` (ne ide u
git — to su tudje fotografije u punoj velicini). Drugi im makne podlogu, izrezi
ih na proizvod, poravna svjetlinu i spremi WebP s prozirnoscu, a popis upise u
`src/data/productImages.json`.

Dok ove mape nema, aplikacija se crta bez slika i nista se ne lomi — kartica
jednostavno nema pojas s fotografijom.
