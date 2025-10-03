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
                "function": "ignore_unclear",
                "apply_when": True,
                "check_by_default": False,
                "type": "string_application",
                "linked_to_settings": True,
                "setting_id": "view_unclear",
            },
        ],
    }

    def test_match_tokens(self):
        """"""
        token = {'rule_match': ['+', '&']}
        decision = {'id': '123', 't': '+', 'n': 'and', 'class': 'none', 'scope': 'once'}
        regulariser = Regulariser(self.default_conditions, None)
        result = regulariser.match_tokens(token, decision)
        expected = (True, 'and', 'none', 'once', '123', '+')
        self.assertEqual(result, expected)

    def test_regularise_token_one_verse_rule(self):
        """Test regularise token with one rule only for the verse."""
        token = {'index': 2, 'rule_match': ['+', '&']}
        decisions = [
            {
                'id': '123',
                'created_time': '2023-10-18T11:08:08.552256Z',
                'context': {},
                't': '+',
                'n': 'and',
                'class': 'none',
                'scope': 'always',
            }
        ]
        regulariser = Regulariser(self.default_conditions, None)
        result = regulariser.regularise_token(token, decisions)
        expected = (True, 'and', [{'class': 'none', 'scope': 'always', 'id': '123', 't': '+', 'n': 'and'}])
        self.assertEqual(result, expected)

    def test_regularise_token_two_rules_one_match(self):
        """Test regularise token with multiple rules for the verse but only one match."""
        token = {'index': 2, 'rule_match': ['+', '&']}
        decisions = [
            {
                'id': '123',
                'created_time': '2023-10-19T11:08:08.552256Z',
                'context': {'word': 2},
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

    def test_regularise_token_two_rules_both_could_match(self):
        """Test regularise token with multiple rules for the verse where both could match and order is reversed."""
        token = {'index': 2, 'rule_match': ['+', '&']}
        decisions = [
            {
                'id': '123',
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
        expected = (True, 'and', [{'class': 'none', 'scope': 'always', 'id': '123', 't': '+', 'n': 'and'}])
        self.assertEqual(result, expected)
