#!/usr/bin/env python3
"""Cuvar puta od prijave do kataloga.

Dvije stvari koje se lako slome, a tiho:
  * izvlacenje JSON bloka iz tijela prijave (app ga salje unutar markdowna),
  * prosjek kad istu cigaru ocijeni vise ljudi.

Pokreni iz app/:  python scripts/test_taste_reports.py
"""
import importlib.util
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


if __name__ == "__main__":
    unittest.main(verbosity=2)
