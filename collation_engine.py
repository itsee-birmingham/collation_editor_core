"""Abstract collation engine and plugin registry.

Provides the base class for collation engines and a registry mechanism so
that engines can be added without modifying core code. A deployment layers
its own concerns (where settings come from, what to send back to its front
end) on through subclasses; see the hooks on CollationEngine.
"""

import json
from abc import ABC, abstractmethod


class CollationResult:
    """What an engine returns from collate(): the CollateX-shaped alignment."""

    def __init__(self, witnesses=None, table=None):
        self.witnesses = witnesses or []
        self.table = table or []

    def to_output_dict(self):
        """Return the dict the preprocessor hands to the postprocessor."""
        return {'witnesses': self.witnesses, 'table': self.table}


class CollationEngine(ABC):
    """Abstract base class for collation engines.

    Subclasses implement name() and collate(). An engine may offer a choice
    of aligners (CollateX: Dekker or Needleman-Wunsch; an AI engine: its
    models); it lists them in _aligners and says what to call that choice in
    _engine_meta so a front end can label the menu correctly.

    Hooks for subclasses:
      obtain_result()             around collate(); e.g. to reuse a cached result
      add_extra_collation_data()  after post-processing, to add keys of the
                                  engine's own to what goes back to the front end
    """

    # Subclasses should define these to describe themselves to front ends.
    _engine_meta = {
        'display_name': 'My Collation Engine',
        'aligner_label': 'Aligner',  # what the front end calls the choice below
        'aligner_key': 'my_engine_aligner',  # algorithm_settings key that selects one
    }
    _aligners = [
        # {'id': 'dekker', 'name': 'Dekker', 'default': True},
        # {'id': 'needleman-wunsch', 'name': 'Needleman-Wunsch'},
    ]

    def __init__(self, algorithm_settings, display_settings=None):
        self.algorithm_settings = algorithm_settings or {}
        self.display_settings = display_settings or {}

    @classmethod
    def available(cls):
        """Whether this engine can run here (e.g. its optional dependency is installed)."""
        return True

    @classmethod
    def get_aligner_names(cls):
        """Return {aligner_id: display_name}."""
        return {a['id']: a['name'] for a in cls._aligners}

    @classmethod
    def get_default_aligner(cls):
        """Return the default aligner id, or the first aligner if none is marked, or None."""
        for aligner in cls._aligners:
            if aligner.get('default'):
                return aligner['id']
        return cls._aligners[0]['id'] if cls._aligners else None

    @classmethod
    def get_engine_registry(cls):
        """Return this engine's metadata and aligners in registry format."""
        meta = dict(cls._engine_meta)
        meta['aligners'] = cls._aligners
        return meta

    def get_setting(self, key, default=None):
        """Return algorithm_settings[key] unless absent or empty, else default.

        Deployments that keep settings elsewhere override this.
        """
        val = self.algorithm_settings.get(key)
        return val if val not in (None, '') else default

    @abstractmethod
    def name(self):
        """Return the engine identifier string (e.g. 'collatex')."""

    @abstractmethod
    def collate(self, data, options, basetext_siglum):
        """Perform collation and return a CollationResult.

        Args:
            data: dict with a 'witnesses' list in the CollateX input format
            options: dict with 'outputFormat', 'algorithm', 'tokenComparator'
            basetext_siglum: the siglum of the base text witness

        Returns:
            CollationResult with table and witnesses populated
        """

    def obtain_result(self, data, options, basetext_siglum):
        """Hook around collate(); override to reuse a previous result, retry, etc."""
        return self.collate(data, options, basetext_siglum)

    def run(self, data, options, basetext_siglum):
        """Collate and return the CollateX-shaped JSON the postprocessor consumes.

        Returns the engine's raw response untouched when it supplied one
        (see CollateServiceEngine), else a JSON string.
        """
        result = self.obtain_result(data, options, basetext_siglum)
        if getattr(result, '_raw_response', None):
            return result._raw_response
        return json.dumps(result.to_output_dict(), ensure_ascii=False)

    def add_extra_collation_data(self, output):
        """Hook on the post-processed output before it goes back to the front end.

        Return it unchanged (the default) or add keys of the engine's own. The
        core display ignores keys it does not know, so whoever adds a key is
        responsible for displaying it.
        """
        return output


# ---------------------------------------------------------------------------
# Engine registry
# ---------------------------------------------------------------------------

# Imported here rather than at the top: the engines subclass CollationEngine,
# so top-level imports would be circular.
from collation.core.engines.collate_service import CollateServiceEngine  # noqa: E402
from collation.core.engines.collatex_microservice import CollatexEngine  # noqa: E402

_engine_registry = {}
_default_engine = CollatexEngine


def register_engine(name, engine_class, default=False):
    """Register a collation engine class by name.

    If default=True, this engine handles any name not explicitly registered
    (the CollateX microservice does, so 'dekker' and 'needleman-wunsch' as
    algorithm names reach it).
    """
    _engine_registry[name] = engine_class
    if default:
        global _default_engine
        _default_engine = engine_class


def get_engine(name, algorithm_settings, display_settings=None):
    """Look up and instantiate a registered engine, or fall back to the default."""
    cls = _engine_registry.get(name, _default_engine)
    if cls is not None:
        return cls(algorithm_settings, display_settings=display_settings)
    return None


def list_engines():
    """Return list of registered engine names."""
    return list(_engine_registry.keys())


def get_engine_registry():
    """Return metadata from every registered engine that is available and describes itself."""
    engines = {}
    for name, cls in _engine_registry.items():
        if getattr(cls, '_engine_meta', None) and cls.available():
            engines[name] = cls.get_engine_registry()
    return {'engines': engines}


# The engines the core ships: the CollateX microservice (the default) and the
# collation-service engine behind the localCollationFunction services variable.
# Further engines (including those in contrib/engines/) are registered by the
# services layer.
register_engine('collatex', CollatexEngine)
register_engine('local', CollateServiceEngine)
