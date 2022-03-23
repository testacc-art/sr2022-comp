#!/usr/bin/env python3

import unittest

import yaml

# Path hackery
import pathlib
import sys
ROOT = pathlib.Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from score import Scorer, InvalidScoresheetException


class ScorerTests(unittest.TestCase):
    longMessage = True

    def construct_scorer(self, zone_contents):
        return Scorer(self.teams_data, zone_contents)

    def assertScores(self, expected_scores, zone_contents):
        scorer = self.construct_scorer(zone_contents)
        scorer.validate(None)
        actual_scores = scorer.calculate_scores()

        self.assertEqual(expected_scores, actual_scores, "Wrong scores")

    def setUp(self):
        self.teams_data = {
            'ABC': {'zone': 0, 'present': True, 'left_scoring_zone': False},
            'DEF': {'zone': 1, 'present': True, 'left_scoring_zone': False},
        }

    def test_template(self):
        template_path = ROOT / 'template.yaml'
        with template_path.open() as f:
            data = yaml.load(f)

        teams_data = data['teams']
        arena_data = data.get('arena_zones')
        extra_data = data.get('other')

        scorer = Scorer(teams_data, arena_data)
        scores = scorer.calculate_scores()

        scorer.validate(extra_data)

        self.assertEqual(
            teams_data.keys(),
            scores.keys(),
            "Should return score values for every team",
        )

    def test_no_cans(self):
        self.assertScores(
            {'ABC': 0, 'DEF': 0},
            {0: {'tokens': ""}, 1: {'tokens': ""}},
        )

    def test_cans(self):
        self.assertScores(
            {'ABC': 0, 'DEF': 4},
            {0: {'tokens': "S"}, 1: {'tokens': "TBS"}},
        )

    def test_cans_and_left_scoring_zone(self):
        self.teams_data['ABC']['left_scoring_zone'] = True
        self.assertScores(
            {'ABC': 1, 'DEF': 4},
            {0: {'tokens': "S"}, 1: {'tokens': "TBS"}},
        )

    def test_invalid_can_characters(self):
        scorer = self.construct_scorer(
            {0: {'tokens': "X"}, 1: {'tokens': "TBS"}},
        )
        with self.assertRaises(InvalidScoresheetException):
            scorer.validate(None)

    def test_invalid_can_characters_in_zone_without_robot(self):
        self.teams_data = {
            'ABC': {'zone': 0, 'present': True, 'left_scoring_zone': False},
        }
        scorer = self.construct_scorer(
            {0: {'tokens': "S"}, 1: {'tokens': "X"}},
        )
        with self.assertRaises(InvalidScoresheetException):
            scorer.validate(None)

    def test_lower_case_can_characters(self):
        scorer = self.construct_scorer(
            {0: {'tokens': "s"}, 1: {'tokens': "tbs"}},
        )
        with self.assertRaises(InvalidScoresheetException):
            scorer.validate(None)

    def test_lower_case_can_characters_in_zone_without_robot(self):
        self.teams_data = {
            'ABC': {'zone': 0, 'present': True, 'left_scoring_zone': False},
        }
        scorer = self.construct_scorer(
            {0: {'tokens': "S"}, 1: {'tokens': "s"}},
        )
        with self.assertRaises(InvalidScoresheetException):
            scorer.validate(None)

    def test_more_than_28_cans_seen(self):
        scorer = self.construct_scorer(
            {0: {'tokens': "S" * 28}, 1: {'tokens': "TB"}},
        )
        with self.assertRaises(InvalidScoresheetException):
            scorer.validate(None)

    def test_more_than_28_cans_seen_in_zone_without_robot(self):
        self.teams_data = {
            'ABC': {'zone': 0, 'present': True, 'left_scoring_zone': False},
        }
        scorer = self.construct_scorer(
            {0: {'tokens': ""}, 1: {'tokens': "S" * 29}},
        )
        with self.assertRaises(InvalidScoresheetException):
            scorer.validate(None)

    def test_space_in_cans(self):
        self.assertScores(
            {'ABC': 0, 'DEF': 4},
            {0: {'tokens': "S "}, 1: {'tokens': "TB S"}},
        )

    def test_left_scoring_zone_not_specified(self):
        self.teams_data = {
            'ABC': {'zone': 0, 'present': True},
            'DEF': {'zone': 1, 'present': True},
        }
        self.assertScores(
            {'ABC': 0, 'DEF': 4},
            {0: {'tokens': "S"}, 1: {'tokens': "TBS"}},
        )

    def test_left_scoring_zone_but_absent(self):
        self.teams_data = {
            'ABC': {'zone': 0, 'present': False, 'left_scoring_zone': True},
            'DEF': {'zone': 1, 'present': True, 'left_scoring_zone': False},
        }
        scorer = self.construct_scorer(
            {0: {'tokens': "S"}, 1: {'tokens': "TBS"}},
        )
        with self.assertRaises(InvalidScoresheetException):
            scorer.validate(None)


if __name__ == '__main__':
    unittest.main()
