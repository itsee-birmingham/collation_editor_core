import json
import sys
import types
from unittest import TestCase

from collation.core.collation_engine import (
    CollationEngine,
    CollationResult,
    get_engine,
    get_engine_registry,
    register_engine,
)
from collation.core.contrib.engines.collatex_python import CollatexPythonEngine
from collation.core.engines.collate_service import CollateServiceEngine
from collation.core.engines.collatex_microservice import CollatexEngine

WITNESSES = [
    {'id': 'A', 'tokens': [{'t': 'the', 'index': '2'}, {'t': 'big', 'index': '4'}, {'t': 'cat', 'index': '6'}]},
    {'id': 'B', 'tokens': [{'t': 'the', 'index': '2'}, {'t': 'cat', 'index': '4'}]},
]
OPTIONS = {'outputFormat': 'lcs', 'algorithm': 'dekker', 'tokenComparator': {'type': 'equality'}}


class _StaticEngine(CollationEngine):
    """Returns a fixed table; used to test the base class without any external service."""

    _engine_meta = {'display_name': 'Static', 'aligner_label': 'Flavour', 'aligner_key': 'static_flavour'}
    _aligners = [{'id': 'plain', 'name': 'Plain'}, {'id': 'fixed', 'name': 'Fixed', 'default': True}]

    def name(self):
        """Registry name."""
        return 'static'

    def collate(self, data, options, basetext_siglum):
        """One column holding each witness's first token."""
        return CollationResult(
            witnesses=[w['id'] for w in data['witnesses']], table=[[[w['tokens'][0]] for w in data['witnesses']]]
        )


class _Unavailable(_StaticEngine):
    """An engine whose optional dependency is missing."""

    @classmethod
    def available(cls):
        """Never runnable."""
        return False

    def name(self):
        """Registry name."""
        return 'unavailable'


class TestRegistry(TestCase):
    """Tests for the engine registry."""

    def test_core_registers_its_own_engines_only(self):
        """Core registers CollateX and the collation-service engine; contrib engines are registered by services."""
        self.assertIsInstance(get_engine('collatex', {}), CollatexEngine)
        self.assertIsInstance(get_engine('local', {}), CollateServiceEngine)
        self.assertNotIn('collatex-python', get_engine_registry()['engines'])
        register_engine('collatex-python', CollatexPythonEngine)
        self.assertIsInstance(get_engine('collatex-python', {}), CollatexPythonEngine)

    def test_unknown_name_falls_to_default(self):
        """An algorithm name with no engine of its own goes to the default engine."""
        self.assertIsInstance(get_engine('needleman-wunsch', {}), CollatexEngine)

    def test_registry_lists_only_available_engines_with_metadata(self):
        """Menus get only engines that can run here and describe themselves."""
        register_engine('static', _StaticEngine)
        register_engine('unavailable', _Unavailable)
        engines = get_engine_registry()['engines']
        self.assertIn('static', engines)
        self.assertNotIn('unavailable', engines)
        self.assertNotIn('local', engines)  # no metadata: never offered in menus
        self.assertEqual(engines['static']['aligner_label'], 'Flavour')
        self.assertEqual([a['id'] for a in engines['static']['aligners']], ['plain', 'fixed'])

    def test_aligner_helpers(self):
        """Aligner names and the default aligner come from the class list."""
        self.assertEqual(_StaticEngine.get_aligner_names(), {'plain': 'Plain', 'fixed': 'Fixed'})
        self.assertEqual(_StaticEngine.get_default_aligner(), 'fixed')
        self.assertEqual(CollatexEngine.get_default_aligner(), 'dekker')
        self.assertIsNone(CollateServiceEngine.get_default_aligner())


class TestRun(TestCase):
    """Tests for CollationEngine.run() and its hooks."""

    def test_run_returns_collatex_shaped_json(self):
        """run() serialises witnesses and table, nothing else."""
        out = json.loads(_StaticEngine({}).run({'witnesses': WITNESSES}, OPTIONS, 'A'))
        self.assertEqual(sorted(out.keys()), ['table', 'witnesses'])
        self.assertEqual(out['witnesses'], ['A', 'B'])
        self.assertEqual(out['table'][0][1], [{'t': 'the', 'index': '2'}])

    def test_obtain_result_wraps_collate(self):
        """obtain_result() can replace the collate() call."""

        class Cached(_StaticEngine):
            def obtain_result(self, data, options, basetext_siglum):
                return CollationResult(witnesses=['X'], table=[])

        self.assertEqual(json.loads(Cached({}).run({'witnesses': WITNESSES}, OPTIONS, 'A'))['witnesses'], ['X'])

    def test_add_extra_collation_data_default_is_identity(self):
        """The base engine adds nothing to the post-processed output."""
        output = {'apparatus': []}
        self.assertIs(_StaticEngine({}).add_extra_collation_data(output), output)

    def test_get_setting_ignores_empty_values(self):
        """An empty setting value falls through to the default."""
        engine = _StaticEngine({'a': '', 'b': 'x'})
        self.assertEqual(engine.get_setting('a', 'dflt'), 'dflt')
        self.assertEqual(engine.get_setting('b', 'dflt'), 'x')


class TestCollateServiceEngine(TestCase):
    """Tests for a project-supplied collation service wrapped as an engine."""

    def setUp(self):
        """Install a fake project module exposing a collation class."""
        module = types.ModuleType('fake_local_collation')

        class Local(object):
            def collate(self, data, options):
                return json.dumps({'witnesses': ['A', 'B'], 'table': [[[{'t': 'the'}], [{'t': 'the'}]]]})

            def broken(self, data, options):
                return b'not json'

        module.Local = Local
        sys.modules['fake_local_collation'] = module

    def tearDown(self):
        """Remove the fake project module."""
        del sys.modules['fake_local_collation']

    def _engine(self, function):
        config = {'python_file': 'fake_local_collation', 'class_name': 'Local', 'function': function}
        return CollateServiceEngine({'local_collation_function': config})

    def test_parses_collatex_json(self):
        """CollateX-shaped JSON from the service becomes a normal result."""
        out = json.loads(self._engine('collate').run({'witnesses': WITNESSES}, OPTIONS, 'A'))
        self.assertEqual(out['witnesses'], ['A', 'B'])
        self.assertEqual(out['table'][0][1][0]['t'], 'the')

    def test_unparseable_result_is_passed_through_raw(self):
        """Anything else is handed back untouched, as the services variable always allowed."""
        self.assertEqual(self._engine('broken').run({'witnesses': WITNESSES}, OPTIONS, 'A'), b'not json')


class TestCollatexPythonEngine(TestCase):
    """Tests for the in-process collatex engine (with a stubbed collatex module)."""

    def test_normalises_witness_major_json(self):
        """Rows become columns, None gaps become [], private keys go."""
        rows = [
            [[{'t': 'the', '_sigil': 'A', '_token_array_position': 0}], [{'t': 'big', '_sigil': 'A'}], [{'t': 'cat'}]],
            [[{'t': 'the', '_sigil': 'B'}], None, [{'t': 'cat', '_sigil': 'B'}]],
        ]
        table = CollatexPythonEngine._to_column_major(rows)
        self.assertEqual(len(table), 3)
        self.assertEqual(table[1], [[{'t': 'big'}], []])
        self.assertEqual(table[0][0], [{'t': 'the'}])

    def test_collate_uses_a_stub_collatex_module(self):
        """collate() drives the package with the right options and normalises its output."""
        seen = {}
        stub = types.ModuleType('collatex')

        class Collation(object):
            def __init__(self):
                self.witnesses = []

            def add_witness(self, witness):
                self.witnesses.append(witness)

        def collate(collation, **kwargs):
            seen.update(kwargs)
            return json.dumps(
                {
                    'witnesses': [w['id'] for w in collation.witnesses],
                    'table': [[[t] for t in w['tokens']] for w in collation.witnesses],
                }
            )

        stub.Collation = Collation
        stub.collate = collate
        saved = sys.modules.get('collatex')
        sys.modules['collatex'] = stub
        try:
            two = [{'id': 'A', 'tokens': [{'t': 'x'}, {'t': 'y'}]}, {'id': 'B', 'tokens': [{'t': 'x'}, {'t': 'z'}]}]
            fuzzy = dict(OPTIONS, tokenComparator={'type': 'levenshtein', 'distance': 2})
            out = json.loads(
                CollatexPythonEngine({'collatex_python_aligner': 'astar'}).run({'witnesses': two}, fuzzy, 'A')
            )
        finally:
            if saved is not None:
                sys.modules['collatex'] = saved
            else:
                del sys.modules['collatex']
        self.assertEqual(seen['output'], 'json')
        self.assertFalse(seen['segmentation'])
        self.assertTrue(seen['near_match'])
        self.assertTrue(seen['astar'])
        self.assertEqual(out['witnesses'], ['A', 'B'])
        self.assertEqual(out['table'][1], [[{'t': 'y'}], [{'t': 'z'}]])
