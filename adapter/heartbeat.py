"""Paperclip-style heartbeat / company adapter sketch (v0).

Maps this repo's deterministic CEO policy onto Paperclip-adjacent concepts:
goal, budget, org roles, and a heartbeat tick. This is a documentation-grade
sketch — not a fork of paperclipai/paperclip and not a live control-plane client.

Usage:
    python -m adapter.heartbeat --days 3
    python -m adapter.heartbeat --export-template
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

# Allow `python -m adapter.heartbeat` from repo root without install.
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from paperclip import CEO, Company, Strategy, load_strategy  # noqa: E402


@dataclass(frozen=True)
class CompanyTemplate:
    """Sketch of a Paperclip-style company surface for this CEO policy."""

    name: str
    goal: str
    budget: dict[str, int]
    org_roles: dict[str, str]
    policy: dict[str, Any]
    heartbeat: dict[str, str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_company_template(strategy: Strategy | None = None) -> CompanyTemplate:
    """Export CEO strategy as a Paperclip-adjacent company template."""
    s = strategy or load_strategy()
    return CompanyTemplate(
        name="operation-paperclip-ceo-lab",
        goal=s.goal,
        budget={
            "starting_cash": s.starting_cash,
            "hire_cost": s.hire_cost,
            "research_cost": s.research_cost,
            "produce_cost": s.production_cost,
        },
        org_roles=dict(s.org_roles)
        or {
            "ceo": "Allocate cash: hire → research → produce",
            "engineer": "Multiply production yield with research",
        },
        policy={
            "priority": ["hire", "research", "produce"],
            "thresholds": {
                "max_engineers": s.max_engineers,
                "max_research": s.max_research,
            },
            "yield_formula": "engineers * (1 + research) per produce spend",
        },
        heartbeat={
            "tick": "run_day",
            "meaning": (
                "One heartbeat = one CEO day: optionally hire or research "
                "per thresholds, then attempt production."
            ),
            "board_metric": "board_brief()",
        },
    )


def heartbeat_tick(ceo: CEO) -> dict[str, Any]:
    """Apply one Paperclip-style heartbeat using the local CEO policy."""
    produced = ceo.run_day()
    c = ceo.company
    return {
        "produced": produced,
        "day": c.day - 1,
        "paperclips": c.paperclips,
        "cash": c.cash,
        "engineers": c.engineers,
        "research": c.research,
        "board_brief": ceo.board_brief(),
    }


def run_heartbeats(days: int, strategy: Strategy | None = None) -> list[dict[str, Any]]:
    """Run N heartbeat ticks; returns per-tick board snapshots."""
    s = strategy or load_strategy()
    ceo = CEO(company=Company.from_strategy(s), strategy=s)
    return [heartbeat_tick(ceo) for _ in range(days)]


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Paperclip wedge adapter sketch — map CEO policy to goal/budget/"
            "org roles and run heartbeat ticks."
        )
    )
    parser.add_argument("--days", type=int, default=5, help="heartbeat ticks to run")
    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help="CEO strategy JSON (default: config/ceo_strategy.json)",
    )
    parser.add_argument(
        "--export-template",
        action="store_true",
        help="print company template JSON and exit",
    )
    args = parser.parse_args()
    strategy = load_strategy(args.config)

    if args.export_template:
        print(json.dumps(build_company_template(strategy).to_dict(), indent=2))
        return

    if args.days < 0:
        parser.error("--days must be non-negative")

    template = build_company_template(strategy)
    print(f"Company | {template.name}")
    print(f"Goal    | {template.goal}")
    print(f"Budget  | starting_cash=${template.budget['starting_cash']}")
    print(f"Roles   | {', '.join(template.org_roles)}")
    print("--- heartbeats ---")
    for tick in run_heartbeats(args.days, strategy):
        print(
            f"tick {tick['day']:2d} | +{tick['produced']} clips | "
            f"{tick['paperclips']} total | ${tick['cash']} cash | "
            f"{tick['engineers']} eng | {tick['research']} research"
        )


if __name__ == "__main__":
    main()
