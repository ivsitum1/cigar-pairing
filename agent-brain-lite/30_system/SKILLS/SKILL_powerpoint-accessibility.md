---
name: powerpoint-accessibility
description: Scan and remediate PPTX for accessibility (contrast, reading order, alt text, titles). Use for accessible presentation, PPT audit, WCAG slides.
version: 1.0
last_updated: 2026-05-18
domain: tools
tokens: ~650
triggers:
  - powerpoint accessibility
  - accessible presentation
  - PPTX audit
  - slide accessibility
  - WCAG presentation
requires_packages: []
reference_files: []
conflicts_with:
  - figure-pipeline
disambiguation: Use for slide deck a11y; for publication figures use figure-pipeline.
pipeline_position: []
---

# Skill: PowerPoint accessibility

## When to use

- User provides `.pptx` for accessibility review or remediation guidance

## Procedure

1. **Structure:** unique slide titles; logical reading order.
2. **Contrast:** text/background meets WCAG AA where possible.
3. **Alt text:** every meaningful image; decorative marked decorative.
4. **Tables/charts:** summarize in speaker notes or alt text.
5. **Motion:** flag auto-advance and flashing content.
6. **Deliver:** prioritized fix list (high → low); no false claim of automated certification.

## Verification

- [ ] Issues tied to slide numbers
- [ ] Color-only encoding flagged

## Related

- `SKILL_presentation-speech.md`

## Related Hubs

- [[Presentation and slide skills]]
- [[Skills audit 2026-05]]
