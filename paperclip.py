"""Deterministic CEO policy lab for Paperclip-style agent companies.

Not affiliated with paperclipai/paperclip (the agent-company control plane).
This is a tiny, tested resource-allocation loop: hire → research → produce.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass


@dataclass
class Company:
    cash: int = 100
    engineers: int = 1
    research: int = 0
    paperclips: int = 0
    day: int = 1


class CEO:
    """Run the company toward the single objective: making paperclips."""

    hire_cost = 50
    research_cost = 30
    production_cost = 5

    def __init__(self, company: Company | None = None) -> None:
        self.company = company or Company()

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
        if self.company.cash >= self.hire_cost and self.company.engineers < 2:
            self.hire_engineer()
        elif self.company.cash >= self.research_cost and self.company.research < 1:
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
        "--verbose",
        "-v",
        action="store_true",
        help="print a board brief after each day",
    )
    args = parser.parse_args()
    if args.days < 0:
        parser.error("--days must be non-negative")

    ceo = CEO()
    if args.verbose:
        print("=== Paperclip CEO lab (deterministic) ===")
        print(f"Start  | {ceo.board_brief()}")
    for _ in range(args.days):
        ceo.run_day()
        if args.verbose:
            # day has already advanced; show post-action state with completed day index
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
