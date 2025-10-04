from unittest import TestCase
from unittest.mock import call, patch

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
                "id": "only_nomsac",
                "label": "Only apply to Nomina Sacra",
                "linked_to_settings": False,
                "function": "match_nomsac",
                "apply_when": True,
                "check_by_default": False,
                "type": "boolean"
            },
        ],
    }

    @patch('collation.core.regulariser.Regulariser._match_tokens')
    def test_regularise_token_two_rules_one_matches_word(self, mocked__match_token):
        """Test regularise token with multiple rules for the verse but only one matches based on word pos."""
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
        mocked__match_token.side_effect = [
            (True, decisions[1]['n'], decisions[1]['class'], decisions[1]['scope'], decisions[1]['id'], decisions[1]['t']),
        ]
        regulariser = Regulariser(self.default_conditions, None)
        result = regulariser.regularise_token(token, decisions)
        self.assertEqual(mocked__match_token.call_count, 1)
        mocked__match_token.assert_called_with(token, decisions[1])
        expected = (True, 'and', [{'class': 'none', 'scope': 'always', 'id': '123', 't': '+', 'n': 'and'}])
        self.assertEqual(result, expected)

    @patch('collation.core.regulariser.Regulariser._match_tokens')
    def test_regularise_token_two_rules_one_could_match(self, mocked__match_token):
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
        mocked__match_token.side_effect = [
            (False, None, None, None, None, None),
            (True, decisions[0]['n'], decisions[0]['class'], decisions[0]['scope'], decisions[0]['id'], decisions[0]['t']),
        ]
        regulariser = Regulariser(self.default_conditions, None)
        result = regulariser.regularise_token(token, decisions)
        self.assertEqual(mocked__match_token.call_count, 2)
        mocked__match_token.assert_has_calls([call(token, decisions[1]), call(token, decisions[0])])
        expected = (True, 'plus', [{'class': 'none', 'scope': 'always', 'id': '124', 't': '+', 'n': 'plus'}])
        self.assertEqual(result, expected)

    @patch('collation.core.regulariser.Regulariser._match_tokens')
    def test_regularise_token_two_rules_both_could_match(self, mocked__match_token):
        """Test regularise token with multiple rules for the verse where both could match and order is reversed."""
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
        mocked__match_token.side_effect = [
            (True, decisions[1]['n'], decisions[1]['class'], decisions[1]['scope'], decisions[1]['id'], decisions[1]['t']),
            (True, decisions[0]['n'], decisions[0]['class'], decisions[0]['scope'], decisions[0]['id'], decisions[0]['t']),
        ]
        regulariser = Regulariser(self.default_conditions, None)
        result = regulariser.regularise_token(token, decisions)
        self.assertEqual(mocked__match_token.call_count, 2)
        mocked__match_token.assert_has_calls([call(token, decisions[1]), call(token, decisions[0])])
        expected = (
            True,
            'plus',
            [
                {'class': 'none', 'scope': 'always', 'id': '123', 't': '+', 'n': 'and'},
                {'class': 'none', 'scope': 'always', 'id': '124', 't': '+', 'n': 'plus'},
            ],
        )
        self.assertEqual(result, expected)

    @patch('collation.core.regulariser.Regulariser._match_tokens')
    def test_regularise_token_two_rules_both_could_match_different_rule_strings(self, mocked__match_token):
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
        mocked__match_token.side_effect = [
            (True, decisions[1]['n'], decisions[1]['class'], decisions[1]['scope'], decisions[1]['id'], decisions[1]['t']),
            (True, decisions[0]['n'], decisions[0]['class'], decisions[0]['scope'], decisions[0]['id'], decisions[0]['t']),
        ]
        regulariser = Regulariser(self.default_conditions, None)
        result = regulariser.regularise_token(token, decisions)
        self.assertEqual(mocked__match_token.call_count, 2)
        mocked__match_token.assert_has_calls([call(token, decisions[1]), call(token, decisions[0])])
        expected = (
            True,
            'plus',
            [
                {'class': 'none', 'scope': 'always', 'id': '123', 't': '&', 'n': 'and'},
                {'class': 'none', 'scope': 'always', 'id': '124', 't': '+', 'n': 'plus'},
            ],
        )
        self.assertEqual(result, expected)

    @patch('collation.core.regulariser.Regulariser._match_tokens')
    def test_regularise_token_two_rules_neither_match(self, mocked__match_token):
        """Test regularise token with multiple rules for the verse where both could match and order is reversed."""
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
        mocked__match_token.side_effect = [
            (False, None, None, None, None, None, None),
            (False, None, None, None, None, None, None),
        ]
        regulariser = Regulariser(self.default_conditions, None)
        result = regulariser.regularise_token(token, decisions)
        self.assertEqual(mocked__match_token.call_count, 2)
        mocked__match_token.assert_has_calls([call(token, decisions[1]), call(token, decisions[0])])
        expected = (False, None, None)
        self.assertEqual(result, expected)

# unmocked tests

    def test_regularise_token_two_rules_one_matches_word_unmocked(self):
        """Test regularise token with multiple rules for the verse but only one matches based on word pos."""
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

    def test_regularise_token_two_rules_one_could_match_unmocked(self):
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

    def test_regularise_token_two_rules_both_could_match_unmocked(self):
        """Test regularise token with multiple rules for the verse where both could match and order is reversed."""
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

    def test_regularise_token_two_rules_both_could_match_different_rule_strings_unmocked(self):
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

    def test_regularise_token_two_rules_neither_match_unmocked(self):
        """Test regularise token with multiple rules for the verse where both could match and order is reversed."""
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

    def test_regularise_token_two_rules_both_could_match_but_not_on_conditions_unmocked(self):
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

    def test_regularise_token_two_rules_chained_unmocked(self):
        """Test regularise token with multiple rules for the verse where both could match and order is reversed."""
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
