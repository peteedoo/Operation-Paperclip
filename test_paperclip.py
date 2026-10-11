import unittest

from paperclip import CEO, Company


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


if __name__ == "__main__":
    unittest.main()
