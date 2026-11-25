"""Collation engine for a project-supplied collation service (the localCollationFunction services variable)."""

import importlib
import json
import logging

from collation.core.collation_engine import CollationEngine, CollationResult

logger = logging.getLogger(__name__)


class CollateServiceEngine(CollationEngine):
    """A project's own collation function, wrapped as an engine.

    algorithm_settings['local_collation_function'] holds the project's
    ``python_file`` / ``class_name`` / ``function``; the method is called with
    (data, options) and must return CollateX-shaped JSON (bytes, str or dict),
    as documented for the ``localCollationFunction`` services variable. The
    engine is not listed in menus: the preprocessor selects it whenever that
    variable is configured.
    """

    _engine_meta = {}

    def name(self):
        """Return the registry name of this engine."""
        return 'local'

    def collate(self, data, options, basetext_siglum):
        """Call the configured project function and wrap whatever it returns."""
        config = self.algorithm_settings.get('local_collation_function') or {}
        module = importlib.import_module(config['python_file'])
        instance = getattr(module, config['class_name'])()
        logger.info('collation service %s.%s.%s', config['python_file'], config['class_name'], config['function'])
        response = getattr(instance, config['function'])(data, options)

        payload = response
        try:
            if isinstance(payload, bytes):
                payload = payload.decode('utf-8')
            if isinstance(payload, str):
                payload = json.loads(payload)
            return CollationResult(witnesses=payload.get('witnesses', []), table=payload.get('table', []))
        except Exception:
            # not CollateX JSON: hand it back untouched, as the hook always allowed
            logger.info('collation service result is not CollateX JSON; passing it through')
            result = CollationResult()
            result._raw_response = response
            return result
