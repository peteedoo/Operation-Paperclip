"""Deterministic CEO policy lab for Paperclip-style agent companies.

Not affiliated with paperclipai/paperclip (the agent-company control plane).
This is a tiny, tested resource-allocation loop: hire → research → produce.

Thresholds and costs are file-driven via config/ceo_strategy.json (override
with --config). Defaults match the v0 policy so behavior stays deterministic.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent / "config" / "ceo_strategy.json"


@dataclass(frozen=True)
class Strategy:
    """File-driven hire / research / produce policy."""

    goal: str
    hire_cost: int
    research_cost: int
    production_cost: int
    max_engineers: int
    max_research: int
    starting_cash: int
    starting_engineers: int
    starting_research: int
    starting_paperclips: int
    starting_day: int
    org_roles: dict[str, str]
    version: int = 1

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Strategy:
        costs = data["costs"]
        thresholds = data["thresholds"]
        starting = data.get("starting", {})
        return cls(
            version=int(data.get("version", 1)),
            goal=str(data["goal"]),
            hire_cost=int(costs["hire"]),
            research_cost=int(costs["research"]),
            production_cost=int(costs["produce"]),
            max_engineers=int(thresholds["max_engineers"]),
            max_research=int(thresholds["max_research"]),
            starting_cash=int(starting.get("cash", 100)),
            starting_engineers=int(starting.get("engineers", 1)),
            starting_research=int(starting.get("research", 0)),
            starting_paperclips=int(starting.get("paperclips", 0)),
            starting_day=int(starting.get("day", 1)),
            org_roles={str(k): str(v) for k, v in data.get("org_roles", {}).items()},
        )


def load_strategy(path: Path | str | None = None) -> Strategy:
    """Load CEO strategy from JSON. Defaults to config/ceo_strategy.json."""
    config_path = Path(path) if path else DEFAULT_CONFIG_PATH
    with config_path.open(encoding="utf-8") as fh:
        data = json.load(fh)
    return Strategy.from_dict(data)


@dataclass
class Company:
    cash: int = 100
    engineers: int = 1
    research: int = 0
    paperclips: int = 0
    day: int = 1

    @classmethod
    def from_strategy(cls, strategy: Strategy) -> Company:
        return cls(
            cash=strategy.starting_cash,
            engineers=strategy.starting_engineers,
            research=strategy.starting_research,
            paperclips=strategy.starting_paperclips,
            day=strategy.starting_day,
        )


class CEO:
    """Run the company toward the configured objective (default: paperclips)."""

    def __init__(
        self,
        company: Company | None = None,
        strategy: Strategy | None = None,
    ) -> None:
        self.strategy = strategy or load_strategy()
        self.company = company or Company.from_strategy(self.strategy)

    @property
    def hire_cost(self) -> int:
        return self.strategy.hire_cost

    @property
    def research_cost(self) -> int:
        return self.strategy.research_cost

    @property
    def production_cost(self) -> int:
        return self.strategy.production_cost

    def hire_engineer(self) -> None:
        if self.company.cash < self.hire_cost:
            raise ValueError("not enough cash to hire an engineer")
        self.company.cash -= self.hire_cost
        self.company.engineers += 1

    def fund_research(self) -> None:
        if self.company.cash < self.research_cost:
            raise ValueError("not enough cash to fund research")
        self.company.cash -= self.research_cost
        self.company.research += 1

    def produce(self) -> int:
        if self.company.cash < self.production_cost:
            return 0
        self.company.cash -= self.production_cost
        produced = self.company.engineers * (1 + self.company.research)
        self.company.paperclips += produced
        return produced

    def run_day(self) -> int:
        s = self.strategy
        if (
            self.company.cash >= self.hire_cost
            and self.company.engineers < s.max_engineers
        ):
            self.hire_engineer()
        elif (
            self.company.cash >= self.research_cost
            and self.company.research < s.max_research
        ):
            self.fund_research()
        produced = self.produce()
        self.company.day += 1
        return produced

    def board_brief(self) -> str:
        c = self.company
        return (
            f"Day {c.day}: {c.paperclips} paperclips | "
            f"${c.cash} cash | {c.engineers} engineers | "
            f"{c.research} research"
        )


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Run the Paperclip CEO lab — a deterministic hire/research/produce "
            "policy for agent-company resource loops."
        )
    )
    parser.add_argument("--days", type=int, default=5, help="number of days to run")
    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help="path to CEO strategy JSON (default: config/ceo_strategy.json)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="print a board brief after each day",
    )
    args = parser.parse_args()
    if args.days < 0:
        parser.error("--days must be non-negative")

    strategy = load_strategy(args.config)
    ceo = CEO(strategy=strategy)
    if args.verbose:
        print("=== Paperclip CEO lab (deterministic) ===")
        print(f"Goal   | {strategy.goal}")
        print(f"Start  | {ceo.board_brief()}")
    for _ in range(args.days):
        ceo.run_day()
        if args.verbose:
            c = ceo.company
            print(
                f"After {c.day - 1:2d} | {c.paperclips} paperclips | "
                f"${c.cash} cash | {c.engineers} engineers | "
                f"{c.research} research"
            )

    company = ceo.company
    print(
        f"Day {company.day - 1}: {company.paperclips} paperclips, "
        f"${company.cash} cash, {company.engineers} engineers, "
        f"{company.research} research"
    )


if __name__ == "__main__":
    main()
