from unittest import TestCase

from collation.core.regulariser import Regulariser


class RegulariserTests(TestCase):
    """Tests for the Regulariser."""

    default_conditions = {
        "python_file": "collation.core.default_implementations",
        "class_name": "RuleConditions",
        "configs": [
            {
                "id": "ignore_supplied",
                "label": "Ignore supplied markers",
                "function": "ignore_supplied",
                "apply_when": True,
                "check_by_default": False,
                "type": "string_application",
                "linked_to_settings": True,
                "setting_id": "view_supplied",
            },
            {
                "id": "ignore_unclear",
                "label": "Ignore unclear markers",
                "linked_to_settings": True,
                "setting_id": "view_unclear",
                "function": "ignore_unclear",
                "apply_when": True,
                "check_by_default": False,
                "type": "string_application"
            },
        ],
    }

    def test_regularise_token_two_rules_one_matches_word(self):
        """Test regularise token with multiple rules for the verse but only one matches because of word pos."""
        token = {'index': 2, 'rule_match': ['+', '&']}
        decisions = [
            {
                'id': '124',
                'created_time': '2023-10-19T11:08:08.552256Z',
                'context': {'word': 6},
                't': '+',
                'n': 'plus',
                'class': 'none',
                'scope': 'once',
            },
            {
                'id': '123',
                'created_time': '2023-10-18T11:08:08.552256Z',
                'context': {},
                't': '+',
                'n': 'and',
                'class': 'none',
                'scope': 'always',
            },
        ]
        regulariser = Regulariser(self.default_conditions, None)
        result = regulariser.regularise_token(token, decisions)
        expected = (True, 'and', [{'class': 'none', 'scope': 'always', 'id': '123', 't': '+', 'n': 'and'}])
        self.assertEqual(result, expected)

    def test_regularise_token_two_rules_one_could_match(self):
        """Test regularise token with multiple rules for the verse where one could match based on word string."""
        token = {'index': 2, 'rule_match': ['+']}
        decisions = [
            {
                'id': '124',
                'created_time': '2023-10-19T11:08:08.552256Z',
                'context': {},
                't': '+',
                'n': 'plus',
                'class': 'none',
                'scope': 'always',
            },
            {
                'id': '123',
                'created_time': '2023-10-18T11:08:08.552256Z',
                'context': {},
                't': '&',
                'n': 'and',
                'class': 'none',
                'scope': 'always',
            },
        ]
        regulariser = Regulariser(self.default_conditions, None)
        result = regulariser.regularise_token(token, decisions)
        expected = (True, 'plus', [{'class': 'none', 'scope': 'always', 'id': '124', 't': '+', 'n': 'plus'}])
        self.assertEqual(result, expected)

    def test_regularise_token_two_rules_both_match(self):
        """Test regularise token with multiple rules for the verse where both match and order is reversed."""
        token = {'index': 2, 'rule_match': ['+', '&']}
        decisions = [
            {
                'id': '124',
                'created_time': '2023-10-19T11:08:08.552256Z',
                'context': {},
                't': '+',
                'n': 'plus',
                'class': 'none',
                'scope': 'always',
            },
            {
                'id': '123',
                'created_time': '2023-10-18T11:08:08.552256Z',
                'context': {},
                't': '+',
                'n': 'and',
                'class': 'none',
                'scope': 'always',
            },
        ]
        regulariser = Regulariser(self.default_conditions, None)
        result = regulariser.regularise_token(token, decisions)
        expected = (
            True,
            'plus',
            [
                {'class': 'none', 'scope': 'always', 'id': '123', 't': '+', 'n': 'and'},
                {'class': 'none', 'scope': 'always', 'id': '124', 't': '+', 'n': 'plus'},
            ],
        )
        self.assertEqual(result, expected)

    def test_regularise_token_two_rules_both_could_match_different_rule_strings(self):
        """Test regularise token with multiple rules with different t values for the verse where both could match."""
        token = {'index': 2, 'rule_match': ['+', '&']}
        decisions = [
            {
                'id': '124',
                'created_time': '2023-10-19T11:08:08.552256Z',
                'context': {},
                't': '+',
                'n': 'plus',
                'class': 'none',
                'scope': 'always',
            },
            {
                'id': '123',
                'created_time': '2023-10-18T11:08:08.552256Z',
                'context': {},
                't': '&',
                'n': 'and',
                'class': 'none',
                'scope': 'always',
            },
        ]
        regulariser = Regulariser(self.default_conditions, None)
        result = regulariser.regularise_token(token, decisions)
        expected = (
            True,
            'plus',
            [
                {'class': 'none', 'scope': 'always', 'id': '123', 't': '&', 'n': 'and'},
                {'class': 'none', 'scope': 'always', 'id': '124', 't': '+', 'n': 'plus'},
            ],
        )
        self.assertEqual(result, expected)

    def test_regularise_token_two_rules_neither_match(self):
        """Test regularise token with multiple rules where none match."""
        token = {'index': 2, 'rule_match': ['none', 'fail']}
        decisions = [
            {
                'id': '124',
                'created_time': '2023-10-19T11:08:08.552256Z',
                'context': {},
                't': '+',
                'n': 'plus',
                'class': 'none',
                'scope': 'always',
            },
            {
                'id': '123',
                'created_time': '2023-10-18T11:08:08.552256Z',
                'context': {},
                't': '+',
                'n': 'and',
                'class': 'none',
                'scope': 'always',
            },
        ]
        regulariser = Regulariser(self.default_conditions, None)
        result = regulariser.regularise_token(token, decisions)
        expected = (False, None, None)
        self.assertEqual(result, expected)

    def test_regularise_token_two_rules_both_could_match_but_not_on_conditions(self):
        """Test regularise token with multiple rules for the verse where both could match but one not on conditions."""
        token = {'index': 2, 'rule_match': ['[+]', '&']}
        decisions = [
            {
                'id': '124',
                'created_time': '2023-10-19T11:08:08.552256Z',
                'context': {},
                'conditions': {'ignore_supplied': True},
                't': '+',
                'n': 'plus',
                'class': 'none',
                'scope': 'always',
            },
            {
                'id': '123',
                'created_time': '2023-10-18T11:08:08.552256Z',
                'context': {},
                't': '+',
                'n': 'and',
                'class': 'none',
                'scope': 'always',
            },
        ]
        regulariser = Regulariser(self.default_conditions, None)
        result = regulariser.regularise_token(token, decisions)
        expected = (
            True,
            'plus',
            [
                {'class': 'none', 'scope': 'always', 'id': '124', 't': '+', 'n': 'plus'},
            ],
        )
        self.assertEqual(result, expected)

    def test_regularise_token_two_rules_chained(self):
        """Test regularise token with chained rules."""
        token = {'index': 2, 'rule_match': ['+', '&']}
        decisions = [
            {
                'id': '124',
                'created_time': '2023-10-19T11:08:08.552256Z',
                'context': {},
                't': 'and',
                'n': 'plus',
                'class': 'none',
                'scope': 'always',
            },
            {
                'id': '123',
                'created_time': '2023-10-18T11:08:08.552256Z',
                'context': {},
                't': '+',
                'n': 'and',
                'class': 'none',
                'scope': 'always',
            },
        ]
        regulariser = Regulariser(self.default_conditions, None)
        result = regulariser.regularise_token(token, decisions)
        expected = (
            True,
            'plus',
            [
                {'class': 'none', 'scope': 'always', 'id': '123', 't': '+', 'n': 'and'},
                {'class': 'none', 'scope': 'always', 'id': '124', 't': 'and', 'n': 'plus'},
            ],
        )
        self.assertEqual(result, expected)
