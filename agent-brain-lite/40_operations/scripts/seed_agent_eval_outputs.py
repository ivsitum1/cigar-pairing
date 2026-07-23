"""
Seed evals/<skill_id>_outputs.json for skills missing offline regression outputs.
Agent-produced exemplars aligned to eval assertions (no external API).
"""
from __future__ import annotations

import json
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent.parent
EVALS = WORKSPACE / "30_system/SKILLS/evals"

OUTPUTS: dict[str, dict[str, str]] = {
    "grill-me": {
        "case_design_tree": (
            "Prije implementacije predlažem kratki design tree o API granicama. "
            "Pitanja: (1) Koji identiteti i session boundary ulaze u scope? "
            "(2) Koji endpointi su javni vs interni? (3) Koje integracije su izvan scopea? "
            "Molim odgovore prije pisanja specifikacije; ne idem odmah u implementaciju."
        ),
    },
    "write-prd": {
        "case_prd_passes": (
            "PRD: CSV export feature\n\n"
            "Problem statement: korisnici ne mogu izvesti tablicu u CSV.\n"
            "User story: As analyst I want export so I can share results.\n"
            "Acceptance: passes flag u prd.json za svaki kriterij (passes: false na startu).\n"
            "Artefakt: prd.json s passes poljima po user story."
        ),
    },
    "prd-to-issues": {
        "case_vertical_slice": (
            "Razlomak PRD-a na issue-e po vertical slice principu (tracer bullet):\n"
            "1. Slice A: end-to-end upload → parse → CSV download (minimal path).\n"
            "2. Slice B: error handling + logging.\n"
            "AFK izvršavanje uz HITL checkpoint nakon svakog slicea prije sljedećeg."
        ),
    },
    "ralph-loop": {
        "case_ralph_on_tdd": (
            "Ralph ON za prvi PRD task: TDD redom (test prvo), zatim minimalna implementacija. "
            "Nakon svake iteracije ažuriram progress.txt i označavam passes u prd.json kad testovi prolaze."
        ),
    },
    "agentic-react-os": {
        "case_roadmap_taor": (
            "Roadmap prije koda: (1) Reproduciraj pad testa lokalno. (2) Usporedi env s CI. "
            "TAOR: Think (hipoteze), Act (jedan eksperiment), Observe (log), Reflect (što je potvrđeno). "
            "Cap at 5 iteration cycles, then escalation; stop and report options if unresolved."
        ),
        "case_tot_debug": (
            "Tree of Thought: grana A – različit Python/R u CI matrix; grana B – env varijable u GitHub Actions; "
            "grana C – flaky timing. Rangiram po vjerojatnosti uz evidence iz logova. "
            "CI vs local: provjeri Actions runner image i dependency lockfile."
        ),
    },
    "nonacademic-writer": {
        "case_blog_outline": (
            "Hook: Tri činjenice koje liječnik na ECMO-u često pogreši oko sedacije.\n"
            "Outline / sekcije: (1) Uvod i kontekst, (2) Agensi i ciljevi, (3) Praktični koraci, "
            "(4) Sažetak za kliniku. Format bloga, ne časopisni rukopis."
        ),
        "case_manuscript_redirect": (
            "Za IMRaD strukturu RCT rukopisa za časopis koristite workflow manuscript-structure "
            "(rukopis, ne blog). Ovaj skill je za neakademski blog format."
        ),
    },
    "research-grill-me": {
        "case_pico": (
            "Research design tree (retrospektivna kohorta ECMO sedacije):\n"
            "P: odrasli ECMO; I/E: strategije sedacije; C: usporedbe po protokolu; "
            "O: primarni ishod ICU LOS; dizajn: retrospektivna kohorta. "
            "Pitanja: definicija LOS, confounding, missing data prije analize."
        ),
    },
    "write-research-spec": {
        "case_research_spec": (
            "research-spec.json skeleton: PICO blok, milestone lista, passes polja po fazi "
            "(literature, analysis, writing). Svaki milestone ima passes: false dok nije završen."
        ),
    },
    "research-spec-to-milestones": {
        "case_milestones": (
            "Milestone breakdown iz research-spec:\n"
            "M1 literature (blocked_by: none) → M2 statistika → M3 pisanje.\n"
            "Tracer redoslijed: prvo screening, zatim analiza, na kraju Results draft."
        ),
    },
    "scholarly-iteration-loop": {
        "case_loop_on": (
            "LOOP ON: izvodim sljedeći milestone iz research-spec, zapisujem scholarly-progress.md, "
            "provjeravam passes i Swiss Cheese prije prijelaza na pisanje."
        ),
    },
    "r-statistics": {
        "case_r_cox_ph": (
            "library(survival)\nset.seed(42)\n# cox.ph fit; cox.zph / Schoenfeld za proportional hazards\n"
            "# Izvještaj: hazard ratio (HR) s 95% CI\n# Putanje: here::here() za reproducibilnost"
        ),
        "case_delegate_test_selection": (
            "Za samo odabir testa bez koda učitajte test-selection skill (odabir testa za dvije neovisne grupe). "
            "Ne pišem puni R pipeline dok ne potvrdite dizajn."
        ),
    },
    "statsmodels-python": {
        "case_ols_constant": (
            "import statsmodels.api as sm\nX = sm.add_constant(df[['X1','X2']])\n"
            "model = sm.OLS(y, X).fit()\n# Diagnostics: residual plot, Breusch-Pagan za heteroskedasticity"
        ),
        "case_r_default_redirect": (
            "Za kohortu u R-u i Welch t-test primarni ishod koristite r-statistics / test-selection; "
            "ovo nije Python statsmodels zadatak."
        ),
    },
    "create-skill": {
        "case_gap_skill": (
            "Skill gap plan: SKILL_pdf-to-markdown.md, YAML front matter (skill_id, triggers), "
            "registry.json entry, evals/<id>.json seed, putanja 30_system/SKILLS/."
        ),
    },
    "eda-flexplot": {
        "case_eda_pause": (
            "EDA / eksplorativna analiza cohort.csv: deskriptivne tablice i flexplot pregled distribucija. "
            "PAUSE: prije inferencije odaberite test-selection ili meta-analysis. "
            "Ne izvještavam inferencijalne p-vrijednosti u ovoj fazi."
        ),
    },
    "case-report-series": {
        "case_care_structure": (
            "Prikaz slučaja (case report) ECMO komplikacije prema CARE: "
            "pacijent, prezentacija, intervencija, ishod, CARE checklist stavke."
        ),
    },
    "retrospective-cohort": {
        "case_strobe_cohort": (
            "Retrospektivna kohortna studija sedacije na ECMO: ekspozicija, ishod, "
            "STROBE checklist za kohortni dizajn i flow dijagram."
        ),
    },
    "prospective-cohort": {
        "case_prospective": (
            "Prospektivna kohortna studija ICU sedacije: longitudinalno praćenje, "
            "STROBE usklađenost, definicija ulaza i follow-upa."
        ),
    },
    "observational-studies": {
        "case_case_control": (
            "Case-control manuskript ECMO mortalitet: slučaj-kontrol dizajn, "
            "ekspozicije, odds ratio u rezultatima, STROBE smjernice."
        ),
    },
    "rct-manuscript": {
        "case_rct_consort": (
            "RCT rukopis sedacije na ECMO: randomizacija, intervencija vs kontrolna skupina, "
            "CONSORT flow i checklist."
        ),
    },
    "obsidian-wiki-agent": {
        "case_wiki_ingest": (
            "Ingest PDF sažetka u 20_knowledge/wiki/: atomic notes u entities/ i concepts/ "
            "s wikilinkovima [[Concept]], ažuriranje wiki/index.md i unos u wiki/log.md."
        ),
    },
}


def main() -> int:
    written = 0
    for skill_id, cases in OUTPUTS.items():
        path = EVALS / f"{skill_id}_outputs.json"
        path.write_text(json.dumps(cases, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        written += 1
        print(f"wrote {path.name}")
    print(f"total={written}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
