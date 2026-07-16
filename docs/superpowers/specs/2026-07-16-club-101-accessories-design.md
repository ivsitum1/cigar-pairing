# Club 101 + Accessories — design

## Goal

Add an educational **101** section inside Club with three tracks:

1. **Cigare 101** — vitola, strength vs body, humidor, cut, light
2. **Pića 101** — reading labels, age tiers, distillation/oak basics
3. **Pribor 101** — glasses, humidors, cutters, ashtrays, decanters

Optional **shop links** on accessory (and later any) cards for local/online retailers; partnerships can fill these later without schema changes.

## Non-goals (phase 1)

- Full accessories product catalog with prices/SKU
- New bottom-nav tab
- Affiliate tracking

## Data

New file `app/src/data/club101.json`:

```ts
{
  tracks: {
    cigars: GuideCard[],
    drinks: GuideCard[],
    accessories: GuideCard[]
  }
}

GuideCard = {
  id: string
  title: LocalizedText
  body: LocalizedText
  shopLinks?: { label: LocalizedText; url: string }[]  // optional
}
```

Facts/quiz stay in `club.json` (rotation + assessment). 101 is a structured curriculum.

## UI

On `ClubPage`, after “Did you know?” and before Quiz:

- `SectionTitle` → Club 101
- Short intro line
- `Chip` track switcher: Cigare | Pića | Pribor
- Stack of cedar cards (title + body); if `shopLinks` present, show outbound link chips

## i18n

Keys under `club.101*` and `club.track*`.

## Tests

`club101.test.ts`: each track has ≥4 cards; bilingual title/body; shop link URLs are http(s) when present.
