"""Replace ## Examples blocks in SKILL_*.md with domain-tailored Input/Output."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "30_system/SKILLS"
json.loads((ROOT / "registry.json").read_text(encoding="utf-8"))  # validate registry exists

EXAMPLES: dict[str, tuple[str, str]] = {
    "ai-detection": (
        "Pokreni AI score na Discussion sekciji i reci što popraviti.",
        "Pokrećem `check_ai_score_fast` ili pipeline; score `[VERIFIED]` iz R outputa; prijedloge reformulacija `[INFERRED]` uz `writing-avoid-ai` reference.",
    ),
    "avoid-ai-formulations": (
        "Ova rečenica zvuči kao ChatGPT; zamijeni je akademski, bez šablonskih fraza.",
        "Zamjene predložim uz provjeru liste zabranjenih fraza `[EXTRACTED]`; ton discipline `[ASSUMPTION]` ako nema uzorka iz časopisa.",
    ),
    "case-report-series": (
        "Strukturiraj CARE case report za komplikaciju nakon regionalne anestezije.",
        "Outline slijedi CARE stavke `[EXTRACTED]`; identifikacija pacijenta i detalji slučaja samo ako ih korisnik da, inače `[BLANK]`.",
    ),
    "consort-checklist": (
        "Je li RCT manuskript kompletan za CONSORT prije slanja?",
        "Za svaku stavku: status i lokacija u MS `[EXTRACTED]`; ako tekst nije dostupan, stavke su `[BLANK]` uz popis što učitati.",
    ),
    "create-sop": (
        "Dokumentiraj ovaj višekorakni fix (npr. pre-commit) da ga tim može ponoviti.",
        "SOP: koraci, preduvjeti, rollback `[INFERRED]`; verzije alata i putanje `[EXTRACTED]` iz repozitorija; netestirani korak `[ASSUMPTION]`.",
    ),
    "document-conversion": (
        "Pretvori docx u markdown; zadrži tablice što je moguće.",
        "Koristim dogovoreni tok konverzije; struktura nakon konverzije `[VERIFIED]` usporedbom; format izvan podrške `[BLANK]` uz alternativu.",
    ),
    "eda-flexplot": (
        "Eksplorativno prikaži odnos doze i ishoda prije inferencije.",
        "Flexplot/EDA output `[VERIFIED]` ako se skripta izvrši; inferenciju ne radim u istom koraku; sljedeći skill predložim `[INFERRED]` (npr. test-selection).",
    ),
    "figure-pipeline": (
        "Trebam sve figure za rad u jednom prolazu (300 DPI, konzistentne oznake).",
        "Popis figura i redoslijed `[EXTRACTED]` iz uputa; export postavke `[VERIFIED]` nakon provjere datoteka; figura bez podataka `[BLANK]`.",
    ),
    "forest-plot": (
        "Jedan forest plot iz meta-analize za primarni ishod.",
        "Pooled estimate i CI `[VERIFIED]` iz model outputa; oznake studija `[EXTRACTED]` iz dataseta; stil ako nije specificiran `[ASSUMPTION]`.",
    ),
    "grade-assessment": (
        "GRADE za dva ishoda u istom sustavnom pregledu.",
        "Ocjena sigurnosti po ishodu s razlogom (bias, imprecision) `[INFERRED]` uz tablice `[EXTRACTED]`; brojke studija ne izmišljam.",
    ),
    "grill-me": (
        "Hoću feature X; nisam siguran oko auth-a, sheme i migracija.",
        "Design tree: grananje odluka; što je u kodu `[EXTRACTED]`; što korisnik mora potvrditi ostaje `[BLANK]` prije PRD-a.",
    ),
    "literature-synthesis": (
        "Napravi analysis grid i istraživačke praznine za literaturu o temi X.",
        "Grid i kategorije `[INFERRED]` iz pitanja; citati i godine `[EXTRACTED]` iz dostavljenih radova; bez liste studija `[BLANK]`.",
    ),
    "manuscript-structure": (
        "Nedostaje li Discussionu nešto tipično za IMRaD u ovom nacrtu?",
        "Checklist sekcija `[INFERRED]`; konkretne rupe samo iz dostavljenog teksta `[EXTRACTED]`; bez MS `[BLANK]`.",
    ),
    "observational-studies": (
        "Pišem case-control o riziku Y; treba STROBE usklađen nacrt.",
        "Odjeljci po STROBE-u `[EXTRACTED]`; matching i kontrole `[BLANK]` ako nisu definirani.",
    ),
    "prd-to-issues": (
        "Razbij PRD u vertical slice-ove za prvi sprint.",
        "Slice-ovi vezani uz `passes` u PRD-u `[EXTRACTED]`; ovisnosti `[INFERRED]`; nedostajući acceptance `[BLANK]`.",
    ),
    "prospective-cohort": (
        "Outline prospektivne kohorte za podnošenje časopisu.",
        "STROBE-usklađene sekcije `[EXTRACTED]`; definicija follow-upa `[BLANK]` ako korisnik nije dao timeline.",
    ),
    "publication-bias": (
        "k=14 studija; ima li asimetrije u funnel plotu za primarni ishod?",
        "Egger/Peters rezultati `[VERIFIED]` iz izračuna; klinička interpretacija `[INFERRED]`; za k<10 ne forsirati test `[EXTRACTED]` iz skill granica.",
    ),
    "ralph-loop": (
        "Ralph ON: issue #12 iz PRD-a, TDD.",
        "Log i testovi `[VERIFIED]` iz izvršenja; zeleni suite prije PROMISE COMPLETE; ako padaju testovi, završetak `[BLANK]`.",
    ),
    "rct-manuscript": (
        "RCT manuskript: randomizacija, ITT, CONSORT flow.",
        "Mapiranje na CONSORT sekcije `[INFERRED]`; brojevi iz protokola `[EXTRACTED]` ako su dati; flow brojevi bez podataka `[BLANK]`.",
    ),
    "research-grill-me": (
        "Radim meta-analizu X; nije mi jasan PICO i primarni ishod.",
        "PICO i ishod razjašnjavam pitanjima; kada korisnik potvrdi, zapisujem `[EXTRACTED]`; bez odgovora ostaje `[BLANK]`.",
    ),
    "research-spec-to-milestones": (
        "Od research-spec.json napravi redoslijed milestonea: analiza pa pisanje.",
        "Milestone-i vezani uz `passes` u specu `[EXTRACTED]`; trajanje `[ASSUMPTION]` ako nije u specu.",
    ),
    "retrospective-cohort": (
        "Retrospektivna kohorta iz registra; prvi draft glavnih sekcija.",
        "STROBE sekcije `[EXTRACTED]`; veličina uzorka i definicije `[EXTRACTED]` samo iz dostavljenog; nedostatak u registru `[BLANK]`.",
    ),
    "scholarly-iteration-loop": (
        "LOOP ON: iteracija 2 nakon recenzijskih komentara.",
        "Swiss Cheese prije zatvaranja iteracije `[VERIFIED]`; promjene u MS `[EXTRACTED]` iz diffa; neusklađen spec `[BLANK]`.",
    ),
    "sensitivity-analysis": (
        "Leave-one-out za primarni pooled effect u meta-analizi.",
        "LOO rezultati `[VERIFIED]` iz ponovnog fita; utjecaj studije `[INFERRED]`; bez pokrenutog modela `[BLANK]`.",
    ),
    "setup-project": (
        "Inicijaliziraj novi projekt s brain/agent-rules strukturom.",
        "Koristim `project_init` ili ekvivalent; struktura mapa `[VERIFIED]` nakon provjere; pogrešan workspace root `[BLANK]`.",
    ),
    "strobe-checklist": (
        "Je li kohortni manuskript pokrio STROBE stavke za cohort dizajn?",
        "Po stavci: status i lokacija u tekstu `[EXTRACTED]`; bez punog teksta stavke `[BLANK]`.",
    ),
    "target-trial-emulation": (
        "Definiraj target trial protokol za emulaciju u administrativnom kohortu.",
        "Eligibility i time-zero `[INFERRED]` uz podatke; varijable iz cohorta `[EXTRACTED]` ako su u kodu; bez sheme podataka `[BLANK]`.",
    ),
    "validate-setup": (
        "Je li ovaj workspace ispravno spojen na agent-rules i foldere projekta?",
        "Provjera mapa i skripti `[VERIFIED]` ako čitam FS; read-only pravilo za referencirani agent-rules `[EXTRACTED]`; drugačiji root `[ASSUMPTION]`.",
    ),
    "write-prd": (
        "Napiši PRD za bulk export s `passes` flagovima.",
        "Polja PRD-a i passes `[EXTRACTED]` iz dogovora; edge caseovi `[INFERRED]`; nepotvrđeni API ugovori `[BLANK]`.",
    ),
    "write-research-spec": (
        "Izgradi research-spec.json za meta-analizu HRQoL ishoda.",
        "`passes`, PICO, definicije ishoda `[EXTRACTED]` nakon usklađivanja; verzije paketa `[VERIFIED]` iz `renv.lock` ako postoji.",
    ),
}


def format_examples_block(skill_id: str) -> str:
    inp, out = EXAMPLES[skill_id]
    return (
        "## Examples\n\n"
        f'**Input:** "{inp}"  \n'
        f'**Output:** "{out}"\n\n'
    )


def replace_examples_section(text: str, new_section: str) -> str:
    marker = "## Examples\n\n"
    idx = text.find(marker)
    if idx == -1:
        return text
    after = text[idx + len(marker) :]
    next_h2 = after.find("\n## ")
    if next_h2 == -1:
        return text[:idx] + new_section.rstrip() + "\n"
    end = idx + len(marker) + next_h2
    return text[:idx] + new_section.rstrip() + "\n" + text[end:]


def main() -> None:
    updated: list[str] = []
    for path in sorted(ROOT.glob("SKILL_*.md")):
        skill_id = path.stem.replace("SKILL_", "")
        if skill_id not in EXAMPLES:
            continue
        text = path.read_text(encoding="utf-8")
        new_text = replace_examples_section(text, format_examples_block(skill_id))
        if new_text != text:
            path.write_text(new_text, encoding="utf-8")
            updated.append(path.name)

    print("UPDATED", len(updated))
    for u in updated:
        print(" ", u)


if __name__ == "__main__":
    main()
