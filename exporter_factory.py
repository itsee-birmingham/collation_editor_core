import importlib


class ExporterFactory(object):
    """Determine the correct exporter based on the settings.

    Attributes:
        exporter_settings (dict, optional): The details of the exporter class/function to use for the export. Defaults
            to None.
        options (dict, optional): Options to use when instatiating the exporter class. Defaults to {}.
    """

    def __init__(self, exporter_settings=None, options={}):
        if exporter_settings and 'python_file' in exporter_settings:
            module_name = exporter_settings['python_file']
            class_name = exporter_settings['class_name']
            self.exporter_function = exporter_settings['function']
        else:
            module_name = 'collation.core.exporter'
            class_name = 'Exporter'
            self.exporter_function = 'export_data'

        MyClass = getattr(importlib.import_module(module_name), class_name)
        self.exporter = MyClass(**options)

    def export_data(self, data):
        """Start the export by calling the exporter function from the exporter class specified.

        Args:
            data (list): A list of JSON objects each representing a collation unit of the data to be exported.

        Returns:
            unknown: The return value of the function called.
        """
        return getattr(self.exporter, self.exporter_function)(data)
