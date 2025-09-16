import importlib


class SettingsApplier(object):
    """Apply the collation settings to the data.

    This is run as a service and called from the services file when making standoff subreadings.
    """

    def __init__(self, options):
        self.settings = options['display_settings']
        self.display_settings_config = options['display_settings_config']
        self.display_settings_config['configs'].sort(key=lambda k: k['execution_pos'])

        module_name = self.display_settings_config['python_file']
        class_name = self.display_settings_config['class_name']
        MyClass = getattr(importlib.import_module(module_name), class_name)
        self.apply_settings_instance = MyClass()

    def apply_settings(self, token):
        """Apply the settings to the token (word).

        Args:
            token (dict): A dictionary representing a single token from the data.

        Returns:
            dict: The token dictionary with the settings applied.
        """
        # set up a base string for interface (this may change later with the settings)
        if 'n' in token:
            token['interface'] = token['n']
        elif 'original' in token:
            token['interface'] = token['original']
        else:
            token['interface'] = token['t']

        # display_settings_config is already in execution order
        for setting in self.display_settings_config['configs']:
            if (setting['id'] in self.settings and setting['apply_when'] is True
                    or setting['id'] not in self.settings and setting['apply_when'] is False):

                token = getattr(self.apply_settings_instance, setting['function'])(token)
        token['interface'] = token['interface'].replace('<', '&lt;').replace('>', '&gt;')
        return token

    def apply_settings_to_token_list(self, token_list):
        """Call apply_settings on each token in the list.

        Args:
            token_list (list): A list of tokens where each token is a dictionary.

        Returns:
            list: The provided list with the settings applied to each token.
        """
        settings_token_list = []
        for token in token_list:
            settings_token_list.append(self.apply_settings(token))
        return settings_token_list
