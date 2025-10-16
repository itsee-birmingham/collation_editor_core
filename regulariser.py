import importlib
import sys


class Regulariser(object):
    """Apply regularisation rules.

    Attributes:
        rule_conditions_config (dict): The dictionary for the rule conditions configuration.
        local_python_functions (_type_): _description_

    """

    def __init__(self, rule_conditions_config, local_python_functions):
        self.rule_conditions_config = rule_conditions_config
        module_name = rule_conditions_config['python_file']
        class_name = rule_conditions_config['class_name']
        MyClass = getattr(importlib.import_module(module_name), class_name)
        self.instance = MyClass()
        if local_python_functions:
            self.local_python_functions = local_python_functions
        else:
            self.local_python_functions = None

    def _match_token(self, token, decision):
        """Check the decision still matches after any rule conditions have been applied."""
        if '_id' in decision:
            print('deprecated - use \'id\' for rules not \'_id\'', file=sys.stderr)
            decision['id'] = decision['_id']
        decision_word = decision['t']
        token_matches = token['rule_match']
        for condition in self.rule_conditions_config['configs']:
            if 'conditions' in decision and decision['conditions'] is not None:
                if (
                    condition['id'] in decision['conditions'].keys()
                    and decision['conditions'][condition['id']] is True
                    and condition['apply_when'] is True
                ) or (
                    (
                        condition['id'] not in decision['conditions'].keys()
                        or (
                            condition['id'] in decision['conditions'].keys()
                            and decision['conditions'][condition['id']] is False
                        )
                    )
                    and condition['apply_when'] is False
                ):
                    if condition['type'] == 'boolean':
                        result = getattr(self.instance, condition['function'])(token, decision)
                        if result is False:
                            # if any of these don't match then we know the rule is
                            # irrelevant so we can return false already
                            return (False, None)
                    if condition['type'] == 'string_application':
                        decision_word, token_matches = getattr(self.instance, condition['function'])(
                            decision_word, token_matches
                        )
        for word in token_matches:
            if word == decision_word:
                return (True, decision)
        return (False, None)

    def regularise_token(self, token, decisions):
        """Check the token against the rules.

        Args:
            token (dict): The token to be regualised.
            decisions (list): The relevant rules for this collation unit retrieved from the database. Each rule in the
                list is a dictionary.

        Returns:
            tuple (boolean, string|None, list|None): Details of any matching rules in application order. The boolean
                says whether at least one rule matched the token. The string is the n value of the last rule in the
                chain. The list gives simplified details of all rules that were applied.

        """
        decision_matches = []
        # filter the rules so based on applicability to this token (including word number and witness is appropriate)
        for decision in decisions:
            if '_id' in decision:
                print('deprecated - use \'id\' for rules not \'_id\'', file=sys.stderr)
                decision['id'] = decision['_id']

            if (
                decision['scope'] == 'always'
                or decision['scope'] == 'verse'
                or (decision['scope'] == 'manuscript' and token['reading'] == decision['context']['witness'])
                or (
                    decision['scope'] == 'once'
                    and (
                        token['index'] == str(decision['context']['word'])
                        and token['reading'] == decision['context']['witness']
                    )
                )
            ):
                decision_matches.append(decision)
        # order by time last modified or created for newer data
        # TODO: perhaps always better to do created time otherwise adding exception
        # to a global rule will change the order for all verses
        if len(decision_matches) > 1:
            decision_matches.sort(
                key=lambda x: x['_meta']['_last_modified_time'] if '_meta' in x else x['created_time']
            )

        classes = []
        last_match = None
        matched = False
        for i, match_d in enumerate(decision_matches):
            if last_match and last_match[0] is True:
                # append the last matched n to the list of match word
                # if its not in there in the token to allow chaining
                if last_match[1]['n'] not in token['rule_match']:
                    token['rule_match'].append(last_match[1]['n'])
            match = self._match_token(token, match_d)
            if match[0] is True:
                last_match = match
                matched = True
                classes.append(
                    {
                        'class': match[1]['class'],
                        'scope': match[1]['scope'],
                        'id': match[1]['id'],
                        't': match[1]['t'],
                        'n': match[1]['n'],
                    }
                )
            if i + 1 == len(decision_matches):
                if matched is True:
                    return (True, last_match[1]['n'], classes)
        return (False, None, None)
