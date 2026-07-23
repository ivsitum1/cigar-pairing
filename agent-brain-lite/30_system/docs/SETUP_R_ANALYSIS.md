# Postavljanje R okruženja za analizu (R, Quarto, paketi)

Koristi ovaj dokument kad **prvi put** postavljaš **agent rules** na novom radnom okruženju. Redoslijed: prvo R, zatim paketi, na kraju Quarto ako trebaš `.qmd` dokumente.

---

## 1. Preduvjeti

- **R** (najnovija stabilna): [https://cran.r-project.org/](https://cran.r-project.org/)
- **RStudio** (preporučeno): [https://posit.co/download/rstudio-desktop/](https://posit.co/download/rstudio-desktop/)
- **Radni direktorij** u R-u mora biti **korijen repozitorija** (folder u kojem leže `setup_duckdb.R`, `40_operations/scripts/`, `30_system/docs/`).

U RStudio-u: *File → Open Project* ili *Session → Set Working Directory → To Source File Location* nakon što otvoriš skriptu iz korijena.

---

## 2. Instalacija R paketa (obavezno za analizu u ovom repou)

U R konzoli, **iz korijena projekta**:

```r
source("40_operations/scripts/utils/install_packages.R")
```

Skripta je **idempotentna**: ponovno pokretanje samo instalira ono što nedostaje.

**Što instalira (sažetak):**

| Skup | Paketi |
|------|--------|
| Jezgra | `duckdb`, `DBI`, `tidyverse`, `here`, `readr`, `readxl` |
| Meta / Bayes / tablice | `meta`, `metafor`, `brms`, `bayesplot`, `robvis`, `writexl`, `openxlsx`, `gtsummary`, `flextable` |
| Vizualizacija (statistički testovi) | `ggstatsplot`, `patchwork`, `ggpubr` |
| Modeliranje / MI / inference | `MASS`, `lme4`, `glmmTMB`, `mgcv`, `car`, `emmeans`, `marginaleffects`, `performance`, `broom`, `mice`, `naniar`, `janitor`, `boot` |
| Survival | `survival`, `survminer`, `flexsurv` |
| Causal (lite) | `MatchIt`, `WeightIt`, `cobalt`, `EValue` |

Prošireni katalog (on-demand): `30_system/SKILLS/reference/r_statistics_packages.md` · skill: `@r-statistics`

### Windows: `brms` i kompilacija

Paketi poput **`brms`** (Stan) na Windowsu često zahtijevaju **RTools**. Ako instalacija padne:

1. Instaliraj odgovarajući **RTools** za tvoju verziju R-a: [https://cran.r-project.org/bin/windows/Rtools/](https://cran.r-project.org/bin/windows/Rtools/)
2. Ponovno pokreni `source("40_operations/scripts/utils/install_packages.R")`.

---

## 3. Provjera DuckDB (opcionalno, preporučeno)

```r
source("setup_duckdb.R")
```

Očekuj poruku tipa `DuckDB OK`. Ako vidiš grešku o nedostajućem paketu, ponovi korak 2.

---

## 4. Quarto (samo ako koristiš Quarto dokumente)

**Quarto nije R paket** — to je zaseban program.

1. Preuzmi instalaciju: [https://quarto.org/docs/get-started/](https://quarto.org/docs/get-started/)
2. Instaliraj i **zatvori pa ponovno otvori** RStudio.
3. `quarto check` u terminalu.

Bez Quarto-a možeš raditi u **`.R`** ili **`.Rmd`**; predložak: `30_system/docs/analysis_template.qmd`.

---

## 5. renv (opcionalno)

```r
install.packages("renv")
renv::init()
source("40_operations/scripts/utils/install_packages.R")
```

---

## Brzi kontrolni popis

- [ ] R instaliran, radni direktorij = korijen agent rules
- [ ] `source("40_operations/scripts/utils/install_packages.R")` bez kritičnih grešaka
- [ ] (Opcionalno) `source("setup_duckdb.R")` OK
- [ ] (Ako treba `.qmd`) Quarto instaliran, `quarto check` OK

---

## Ažuriranje

Nakon `git pull` novih promjena u skriptama, ponovno pokreni `install_packages.R` ako su dodani novi paketi.

**Last updated:** 2026-06-28
