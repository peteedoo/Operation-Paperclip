# Paperclip wedge adapter (v0 sketch)

Maps this lab’s deterministic CEO policy onto **Paperclip-style company concepts** without forking [`paperclipai/paperclip`](https://github.com/paperclipai/paperclip).

| Local concept | Paperclip-adjacent concept |
| --- | --- |
| `Strategy.goal` | Company **goal** |
| `starting.cash` + costs | Company **budget** / spend gates |
| `org_roles` in strategy JSON | Org chart **roles** (CEO allocates; engineers produce) |
| `CEO.run_day()` | **Heartbeat** tick |
| `board_brief()` | Board / governance metric line |

## Run

```bash
python -m adapter.heartbeat --days 5
python -m adapter.heartbeat --export-template
```

`--export-template` prints a JSON company surface (goal, budget, roles, policy, heartbeat meaning) suitable for later ClipMart-style templates — still a sketch, not a live control-plane client.

## Intentional non-goals (v0)

- No clone of the Paperclip control plane, agents runtime, or MCP server
- No network calls to a Paperclip instance
- Thresholds stay file-driven in `config/ceo_strategy.json`
