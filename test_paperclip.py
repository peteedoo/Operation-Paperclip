import json
import tempfile
import unittest
from pathlib import Path

from adapter.heartbeat import build_company_template, run_heartbeats
from paperclip import CEO, Company, Strategy, load_strategy


class CEOTests(unittest.TestCase):
    def test_hiring_uses_cash_and_increases_capacity(self):
        company = Company(cash=50)
        CEO(company).hire_engineer()
        self.assertEqual(company.cash, 0)
        self.assertEqual(company.engineers, 2)

    def test_production_scales_with_engineers_and_research(self):
        company = Company(cash=5, engineers=2, research=1)
        produced = CEO(company).produce()
        self.assertEqual(produced, 4)
        self.assertEqual(company.paperclips, 4)
        self.assertEqual(company.cash, 0)

    def test_run_day_prioritizes_growth_then_production(self):
        company = Company()
        ceo = CEO(company)
        produced = ceo.run_day()
        self.assertEqual(produced, 2)
        self.assertEqual(company.engineers, 2)
        self.assertEqual(company.paperclips, 2)
        self.assertEqual(company.day, 2)

    def test_production_stops_when_cash_is_exhausted(self):
        company = Company(cash=4)
        self.assertEqual(CEO(company).produce(), 0)
        self.assertEqual(company.paperclips, 0)

    def test_board_brief_is_shareable(self):
        company = Company(cash=100, engineers=1, research=0, paperclips=0, day=1)
        brief = CEO(company).board_brief()
        self.assertIn("Day 1:", brief)
        self.assertIn("$100 cash", brief)


class StrategyConfigTests(unittest.TestCase):
    def test_default_strategy_matches_v0_thresholds(self):
        strategy = load_strategy()
        self.assertEqual(strategy.hire_cost, 50)
        self.assertEqual(strategy.research_cost, 30)
        self.assertEqual(strategy.production_cost, 5)
        self.assertEqual(strategy.max_engineers, 2)
        self.assertEqual(strategy.max_research, 1)
        self.assertEqual(strategy.starting_cash, 100)

    def test_custom_strategy_file_drives_thresholds(self):
        payload = {
            "version": 1,
            "goal": "Ship more clips with a bigger team",
            "costs": {"hire": 40, "research": 20, "produce": 5},
            "thresholds": {"max_engineers": 3, "max_research": 2},
            "starting": {
                "cash": 120,
                "engineers": 1,
                "research": 0,
                "paperclips": 0,
                "day": 1,
            },
            "org_roles": {"ceo": "Allocate", "engineer": "Produce"},
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "strategy.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            strategy = load_strategy(path)

        company = Company.from_strategy(strategy)
        ceo = CEO(company=company, strategy=strategy)
        # Day 1: hire (cash 120 → 80), then produce (80 → 75) → 2 clips
        self.assertEqual(ceo.run_day(), 2)
        self.assertEqual(company.engineers, 2)
        # Day 2: hire again toward max_engineers=3
        self.assertEqual(ceo.run_day(), 3)
        self.assertEqual(company.engineers, 3)

    def test_strategy_from_dict_is_immutable_policy(self):
        strategy = Strategy.from_dict(
            {
                "goal": "g",
                "costs": {"hire": 1, "research": 2, "produce": 3},
                "thresholds": {"max_engineers": 1, "max_research": 0},
            }
        )
        self.assertEqual(strategy.production_cost, 3)
        with self.assertRaises(Exception):
            strategy.hire_cost = 99  # type: ignore[misc]


class AdapterHeartbeatTests(unittest.TestCase):
    def test_company_template_maps_goal_budget_roles(self):
        template = build_company_template()
        self.assertEqual(template.goal, load_strategy().goal)
        self.assertIn("starting_cash", template.budget)
        self.assertIn("ceo", template.org_roles)
        self.assertEqual(template.heartbeat["tick"], "run_day")

    def test_heartbeats_match_deterministic_ceo_loop(self):
        ticks = run_heartbeats(5)
        self.assertEqual(len(ticks), 5)
        self.assertEqual(ticks[-1]["paperclips"], 14)
        self.assertEqual(ticks[-1]["cash"], 0)
        self.assertEqual(ticks[-1]["engineers"], 2)
        self.assertEqual(ticks[-1]["research"], 1)


if __name__ == "__main__":
    unittest.main()
