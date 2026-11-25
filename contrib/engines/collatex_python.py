"""CollateX collation engine: the collatex Python package, run in-process (optional dependency)."""

import importlib
import importlib.util
import json
import logging

from collation.core.collation_engine import CollationEngine, CollationResult

logger = logging.getLogger(__name__)


class CollatexPythonEngine(CollationEngine):
    """Collation engine backed by the collatex Python package, run in-process.

    Not registered by the core: a services layer that wants it does
    ``register_engine('collatex-python', CollatexPythonEngine)``.
    Requires the optional ``collatex`` package (and its Levenshtein dependency);
    available() reports whether it is importable so the registry can leave the
    engine out of menus where it cannot run.

    The package's JSON differs from the Java microservice's: its table is
    witness-major (one row per witness) with ``null`` for gaps, and every token
    carries ``_sigil`` and ``_token_array_position``, whatever ``layout`` is
    asked for (checked on collatex 2.1.3, 2.2 and 2.3). The Java service is
    column-major with ``[]`` gaps and the tokens as sent, which is what the
    postprocessor expects, so collate() transposes and strips.
    """

    _engine_meta = {
        'display_name': 'CollateX (Python)',
        'aligner_label': 'Aligner',
        'aligner_key': 'collatex_python_aligner',
    }

    # The package has one alignment algorithm; astar is its experimental variant.
    _aligners = [
        {'id': 'dekker', 'name': 'Dekker', 'default': True},
        {'id': 'astar', 'name': 'Dekker (A*)'},
    ]

    _PRIVATE_TOKEN_KEYS = ('_sigil', '_token_array_position')

    @classmethod
    def available(cls):
        """True when the collatex package can be imported."""
        return importlib.util.find_spec('collatex') is not None

    def name(self):
        """Return the registry name of this engine."""
        return 'collatex-python'

    def collate(self, data, options, basetext_siglum):
        """Collate in-process with the collatex package and return the normalised table."""
        collatex = importlib.import_module('collatex')

        aligner = self.algorithm_settings.get('collatex_python_aligner') or self.get_default_aligner()
        comparator = options.get('tokenComparator') or {}
        near_match = comparator.get('type') == 'levenshtein'
        logger.info(
            'collatex (python) aligner=%s near_match=%s witnesses=%d',
            aligner,
            near_match,
            len(data.get('witnesses', [])),
        )

        collation = collatex.Collation()
        for witness in data.get('witnesses', []):
            collation.add_witness({'id': witness['id'], 'tokens': witness.get('tokens', [])})
        response = collatex.collate(
            collation, output='json', segmentation=False, near_match=near_match, astar=(aligner == 'astar')
        )
        parsed = json.loads(response) if isinstance(response, str) else response
        return CollationResult(
            witnesses=parsed.get('witnesses', []), table=self._to_column_major(parsed.get('table', []))
        )

    @classmethod
    def _to_column_major(cls, rows):
        """Transpose witness-major rows into column-major cells; None gaps become []; private keys go."""
        if not rows:
            return []
        columns = []
        for col in range(len(rows[0])):
            cell_per_witness = []
            for row in rows:
                cell = row[col] if col < len(row) else None
                if cell is None:
                    cell_per_witness.append([])
                else:
                    cell_per_witness.append(
                        [{k: v for k, v in token.items() if k not in cls._PRIVATE_TOKEN_KEYS} for token in cell]
                    )
            columns.append(cell_per_witness)
        return columns
