"""The interface settings that match these default functions are set in static/js/default_settings.js."""


class RuleConditions(object):
    """The default rule conditions to use if services file or project do not supply any."""

    def ignore_unclear(self, decision_word, token_words):
        """Ignore unclear text by replacing underdots with empty strings.

        Args:
            decision_word (str): The string representing the decision word
            token_words (list): A list of strings where each string is an acceptable form of the token for applying the
                rule.

        Returns:
            tuple (str, list): The input words with underdots removed.
        """
        print(decision_word)
        print(token_words)
        decision_word = decision_word.replace('̣', '')
        token_words = [w.replace('̣', '') for w in token_words]
        return (decision_word, token_words)

    def ignore_supplied(self, decision_word, token_words):
        """Ignore supplied text by replacing square brackets with empty strings.

        Args:
            decision_word (str): The string representing the decision word
            token_words (list): A list of strings where each string is an acceptable form of the token for applying the
                rule.

        Returns:
            tuple (str, list): The input words with square brackets removed.
        """
        decision_word = decision_word.replace('[', '').replace(']', '')
        token_words = [w.replace('[', '').replace(']', '') for w in token_words]
        return (decision_word, token_words)


class ApplySettings(object):
    """Functions for the default settings, used if services file or project do not supply any."""

    def lower_case(self, token):
        """Apply the lower case setting to the token.

        Args:
            token (dict): A dictionary representing a token (word).

        Returns:
            dict: The token dictionary with the interface key changed according to the setting.
        """
        token['interface'] = token['interface'].lower()
        return token

    def hide_supplied_text(self, token):
        """Remove [ and ] from the token (they indicate supplied text).

        Args:
            token (dict): A dictionary representing a token (word).

        Returns:
            dict: The token dictionary with the interface key changed according to the setting.
        """
        token['interface'] = token['interface'].replace('[', '').replace(']', '')
        return token

    def hide_unclear_text(self, token):
        """Remove underdots from the token (they inidcate unclear text).

        Args:
            token (dict): A dictionary representing a token (word).

        Returns:
            dict: The token dictionary with the interface key changed according to the setting.
        """
        token['interface'] = token['interface'].replace('̣', '')
        return token
