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


if __name__ == "__main__":
    unittest.main()
