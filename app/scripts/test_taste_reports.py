#!/usr/bin/env python3
"""Cuvar puta od prijave do kataloga.

Dvije stvari koje se lako slome, a tiho:
  * izvlacenje JSON bloka iz tijela prijave (app ga salje unutar markdowna),
  * prosjek kad istu cigaru ocijeni vise ljudi.

Pokreni iz app/:  python scripts/test_taste_reports.py
"""
import importlib.util
import json
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent


def _load(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


imp = _load("imp", "import-taste-report.py")
app = _load("app_", "apply-taste-reports.py")
fetch = _load("fetch_", "fetch-taste-reports.py")

BODY = """Dojmovi nakon pušenja — **Ivan**, 1 cigara.

| Cigara | Snaga | Tijelo |
| --- | --- | --- |
| Ashton Classic | 2 | 2 |

<details><summary>Podaci za uvoz</summary>

```json
{
  "kind": "cigar-pairing-taste-report",
  "v": 1,
  "by": "Ivan",
  "at": "2026-08-15T12:00:00.000Z",
  "reports": [
    {"cigarId": "cig-ashton-classic", "label": "Ashton Classic", "strength": 2, "body": 2,
     "at": "2026-08-15T11:00:00.000Z"}
  ]
}
```

</details>
"""


class TestExtract(unittest.TestCase):
    def test_reads_the_block_out_of_a_github_issue(self):
        payload = imp.extract_payload(BODY)
        self.assertEqual(payload["by"], "Ivan")
        self.assertEqual(len(payload["reports"]), 1)

    def test_reads_bare_json_too(self):
        payload = imp.extract_payload(
            '{"kind": "cigar-pairing-taste-report", "v": 1, "by": "Kolega", "reports": []}'
        )
        self.assertEqual(payload["by"], "Kolega")

    def test_refuses_text_without_a_report(self):
        for text in ("", "samo neki komentar", '```json\n{"kind": "nesto drugo"}\n```'):
            with self.assertRaises(SystemExit):
                imp.extract_payload(text)

    def test_clamps_instead_of_dropping(self):
        self.assertEqual(imp.clamp(9), 5)
        self.assertEqual(imp.clamp(0), 1)
        self.assertEqual(imp.clamp("3"), 3)
        self.assertIsNone(imp.clamp("jako"))
        self.assertIsNone(imp.clamp(None))


class TestAverage(unittest.TestCase):
    def test_single_taster_is_himself(self):
        self.assertEqual(app.average([4]), 4)

    def test_ties_go_up(self):
        # 3 i 4: tko je osjetio vise, osjetio je nesto sto drugi nije
        self.assertEqual(app.average([3, 4]), 4)
        self.assertEqual(app.average([2, 3]), 3)

    def test_plain_average_otherwise(self):
        self.assertEqual(app.average([2, 2, 5]), 3)
        self.assertEqual(app.average([5, 5, 5]), 5)
        self.assertEqual(app.average([1, 1]), 1)


class TestMergeAcrossPeople(unittest.TestCase):
    """Kljuc je (osoba, cigara) — dvoje ljudi ne prepisuje jedno drugo."""

    @staticmethod
    def _payload(by, strength, at="2026-08-15T12:00:00.000Z"):
        return {
            "kind": "cigar-pairing-taste-report",
            "by": by,
            "at": at,
            "reports": [{"cigarId": "cig-x", "strength": strength, "body": 3, "at": at}],
        }

    @staticmethod
    def _resolve(cid):
        return cid if cid == "cig-x" else None

    def test_two_people_stand_side_by_side(self):
        kept = {}
        imp.merge_payload(kept, self._payload("Ivan", 2), self._resolve)
        imp.merge_payload(kept, self._payload("Kolega", 4), self._resolve)
        self.assertEqual(len(kept), 2)
        self.assertEqual({r["strength"] for r in kept.values()}, {2, 4})

    def test_same_person_updates_in_place(self):
        kept = {}
        imp.merge_payload(kept, self._payload("Ivan", 2), self._resolve)
        _, added, updated, _ = imp.merge_payload(kept, self._payload("Ivan", 5), self._resolve)
        self.assertEqual((added, updated), (0, 1))
        self.assertEqual(len(kept), 1)
        self.assertEqual(next(iter(kept.values()))["strength"], 5)

    def test_repeating_the_same_report_changes_nothing(self):
        kept = {}
        imp.merge_payload(kept, self._payload("Ivan", 2), self._resolve, source="repo#1")
        before = json.loads(json.dumps(list(kept.values())))
        _, added, updated, _ = imp.merge_payload(
            kept, self._payload("Ivan", 2), self._resolve, source="repo#1"
        )
        self.assertEqual((added, updated), (0, 0))
        self.assertEqual(list(kept.values()), before)

    def test_unsigned_report_is_refused(self):
        with self.assertRaises(ValueError):
            imp.merge_payload({}, self._payload("  ", 3), self._resolve)

    def test_unknown_cigar_is_skipped_not_invented(self):
        payload = self._payload("Ivan", 3)
        payload["reports"][0]["cigarId"] = "cig-ne-postoji"
        kept = {}
        _, added, _, skipped = imp.merge_payload(kept, payload, self._resolve)
        self.assertEqual((added, skipped), (0, 1))
        self.assertEqual(kept, {})


class TestFetch(unittest.TestCase):
    def test_pull_requests_are_not_impressions(self):
        rows = [
            {"number": 1, "body": "x"},
            {"number": 2, "body": "y", "pull_request": {"url": "…"}},
        ]
        fetch._via_gh = lambda path: rows
        out = fetch.fetch_issues("owner/repo", "dojmovi", "all")
        self.assertEqual([r["number"] for r in out], [1])

    def test_reads_gh_paginated_output(self):
        # `gh api --paginate` zna nanizati vise JSON nizova jedan za drugim
        class FakeRun:
            stdout = '[{"number": 1}]\n[{"number": 2}]\n'

        fetch.shutil.which = lambda _: "/usr/bin/gh"
        fetch.subprocess.run = lambda *a, **k: FakeRun()
        rows = fetch._via_gh("/repos/x/y/issues?state=all")
        self.assertEqual([r["number"] for r in rows], [1, 2])


if __name__ == "__main__":
    unittest.main(verbosity=2)
