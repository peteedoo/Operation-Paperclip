# Operation Paperclip — CEO policy lab

**A tiny, deterministic CEO for [Paperclip](https://github.com/paperclipai/paperclip)-style agent companies:** allocate cash, hire once, fund research once, then maximize paperclip production under hard constraints.

[![CI](https://github.com/peteedoo/Operation-Paperclip/actions/workflows/ci.yml/badge.svg)](https://github.com/peteedoo/Operation-Paperclip/actions/workflows/ci.yml)

> **Not** [`paperclipai/paperclip`](https://github.com/paperclipai/paperclip) (the ~open-source control plane for autonomous AI-agent companies).  
> **Not** the historical U.S. program of the same name — this repo is a resource-allocation demo only.

---

## Why this exists

[Paperclip](https://github.com/paperclipai/paperclip) is the agent-company control plane (org charts, budgets, heartbeats, board governance). This lab is a **reference CEO policy**: a clear, tested hire → research → produce loop you can read in one sitting and map into a Paperclip company template.

**Job of the repo:** Paperclip ecosystem wedge, packaged as a hiring-grade ops artifact (constraints, acceptance tests, board metrics).

---

## 30-second demo

```bash
python paperclip.py --days 5 --verbose
```

```text
=== Paperclip CEO lab (deterministic) ===
Goal   | Maximize paperclips under cash and capacity constraints
Start  | Day 1: 0 paperclips | $100 cash | 1 engineers | 0 research
After  1 | 2 paperclips | $45 cash | 2 engineers | 0 research
After  2 | 6 paperclips | $10 cash | 2 engineers | 1 research
After  3 | 10 paperclips | $5 cash | 2 engineers | 1 research
After  4 | 14 paperclips | $0 cash | 2 engineers | 1 research
After  5 | 14 paperclips | $0 cash | 2 engineers | 1 research
Day 5: 14 paperclips, $0 cash, 2 engineers, 1 research
```

| Days | Paperclips | Cash left | Engineers | Research | What happened |
| --- | ---: | ---: | ---: | ---: | --- |
| 5 | 14 | $0 | 2 | 1 | Hire day 1 → research day 2 → produce until cash dies |
| 30 | 14 | $0 | 2 | 1 | Same ceiling — no revenue loop yet; cash exhaustion is the lesson |

**CEO policy (v0):** hire until `max_engineers` → fund research until `max_research` → spend remaining cash on production. Thresholds live in config (below). Output is fully deterministic for a given strategy file.

---

## Strategy config (file-driven)

Hire / research / produce costs and caps are loaded from [`config/ceo_strategy.json`](./config/ceo_strategy.json):

| Field | Meaning |
| --- | --- |
| `goal` | Company objective string |
| `costs.hire` / `research` / `produce` | Cash gates per action |
| `thresholds.max_engineers` / `max_research` | When to stop hiring / funding research |
| `starting.*` | Initial company state |
| `org_roles` | Role blurbs for the adapter sketch |

```bash
python paperclip.py --days 5 --config config/ceo_strategy.json
```

Override the JSON to explore alternate policies; keep the same schema so tests and the adapter stay valid.

---

## Paperclip wedge / heartbeat sketch

[`adapter/`](./adapter/) maps this CEO onto Paperclip-style **goal · budget · org roles · heartbeat** — a concrete sketch, not a fork of the control plane.

```bash
python -m adapter.heartbeat --days 5
python -m adapter.heartbeat --export-template   # JSON company surface
```

See [`adapter/README.md`](./adapter/README.md) for the concept map.

---

## Run & test

```bash
python paperclip.py --days 5          # final board line
python paperclip.py --days 5 -v       # day-by-day brief
python -m adapter.heartbeat --days 3  # wedge heartbeat sketch
python -m unittest -v                 # acceptance tests
```

Requires Python 3.11+.

---

## Ops brief

| Field | Value |
| --- | --- |
| Objective | Maximize paperclips under cash / capacity constraints |
| Loop | Hire → research → produce (priority order per day) |
| Costs | From strategy JSON (default: Hire $50 · Research $30 · Produce $5) |
| Yield | `engineers × (1 + research)` paperclips per production spend |
| Failure mode | Cash exhaustion — production returns `0`, headcount frozen |
| Acceptance | `unittest` covers hiring, scaling, growth priority, cash stop, config, adapter |

---

## Roadmap (stop early unless usage appears)

1. ✅ Deterministic CEO core + tests + CI  
2. ✅ Config file for hire / research / produce thresholds  
3. ✅ Paperclip adapter / heartbeat sketch mapping this policy to company goals & budgets  
4. Optional dashboard / CLI board metrics beyond `board_brief`  
5. Publish as a ClipMart-style company template if/when that marketplace matures  

---

## License

[MIT](./LICENSE)
