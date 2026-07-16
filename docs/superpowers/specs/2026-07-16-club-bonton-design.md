# Pušački bonton — design

## Goal

Add a **separate Club view** — a short etiquette “book” for cigar & drink evenings — inspired by the *form* of classic British manners guides (short precepts, chaptered), without copying any specific work.

## Placement

- Teaser card on Club (sibling to 101), opens full-page view
- Back to Club; chapter list → chapter detail (reuse `LessonBody` layout)

## Non-goals

- Not a 101 track (different tone: manners vs technique)
- No shop links
- No quiz gating

## Data

`app/src/data/bonton.json`:

```ts
{
  title: LocalizedText
  epigraph: LocalizedText
  chapters: { id, title, body }[]  // body uses same \n\n + • catalogue format as club101
}
```

## Tone

- Courtesy, hospitality, measure
- Inclusive (“domaćin / gost”, not gendered exam)
- Positive teaching; short catalogues
