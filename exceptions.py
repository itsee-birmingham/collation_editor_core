class DataInputException(Exception):
    """Raised by the collation process if an error is encoutered that is likely due to the input data."""

    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


class MissingSuffixesException(Exception):
    """Raised by some exporters if a collation unit reading is missing the suffixes key.

    If this exception is raised then often reapproving the verse will in the collation editor will fix it.
    """

    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)
