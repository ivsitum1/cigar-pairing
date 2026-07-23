---
title: Neural Map
category: meta
tags: [neural-network, routing]
---

# Graf čvorova (agentic neural network)

```
                    ┌─────────────────┐
                    │  00 Orchestrator │
                    │  (ulazni čvor)   │
                    └────────┬────────┘
         ┌──────────┬───────┼───────┬──────────┐
         ▼          ▼       ▼       ▼          ▼
    ┌────────┐ ┌────────┐ ┌────┐ ┌──────────┐ ┌──────────┐
    │ 01     │ │ 02     │ │ 03 │ │ 04       │ │ Parent   │
    │ Admin  │ │ Writer │ │Auto│ │ Research │ │ (agent   │
    └────────┘ └────────┘ └────┘ └──────────┘ │  rules)  │
         │          │       │       │         └──────────┘
         └──────────┴───────┴───────┘              ▲
                    handoff (.agent/task/)          │
                    eskalacija (docs/PARENT_BRAIN) ─┘
```

Težine routinga u `harness/routing.json`. RAG-lite: `skills/wiki-query` pretražuje `knowledge/` i YAML frontmatter.

- [[harness/LAYERS|Harness slojevi]]
- `harness/routing.json`
