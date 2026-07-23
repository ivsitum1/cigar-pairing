# Agent Brain Lite

Lagani agentic mozak za uredske zadatke (medicina, znanost, izdavaštvo, bazalno pravo).

- [[index|Wiki indeks]]
- [[AGENTS]] (Cursor ulaz)
- [[docs/PROJECT_SETUP|Koloniranje u projekt]]

## Brzi start (ovaj repo kao master)

```powershell
copy .env.example .env
python scripts/link_parent.py
```

Otvori mapu u Cursoru. Za novi projekt:

```powershell
python scripts/project_init.py --root "PUTANJA_PROJEKTA" --no-symlink
```

Bez `link_parent.py` nema parent skills ni rules.
