# -*- coding: utf-8 -*-
"""Abstract collation engine and plugin registry.

Provides the base class for collation engines and a registry mechanism
so that engines can be added without modifying core code.
"""
import json
import re
import sys
import time
from abc import ABC, abstractmethod


class CollationResult:
    """Container for collation engine output."""

    def __init__(self):
        self.table = []
        self.witnesses = []
        self.feedback = {
            'comments': '',
            'alignment_table': '',
            'processing_duration': None,
            'engine_usage': None,
        }

    def to_output_dict(self):
        """Return a dict suitable for use as the 'output' block."""
        d = {
            'witnesses': self.witnesses,
            'table': self.table,
        }
        # include only non-empty feedback entries
        feedback = {k: v for k, v in self.feedback.items()
                    if v is not None and v != ''}
        if feedback:
            d['collation_feedback'] = feedback
        return d


class CollationEngine(ABC):
    """Abstract base class for collation engines.

    Subclasses implement collate() to perform the actual collation.
    process_result() handles post-collation validation, HTML table
    building, and debug logging — inherited by all engines.
    """

    def __init__(self, algorithm_settings):
        self.algorithm_settings = algorithm_settings

    @abstractmethod
    def name(self):
        """Return the engine identifier string (e.g. 'collatex', 'claude')."""
        pass

    @abstractmethod
    def collate(self, data, options, basetext_siglum):
        """Perform collation and return a CollationResult.

        Args:
            data: dict with 'witnesses' list and 'algorithm' key
            options: dict with 'outputFormat', 'algorithm', 'tokenComparator'
            basetext_siglum: the siglum of the base text witness

        Returns:
            CollationResult with table and witnesses populated
        """
        pass

    def run(self, data, options, basetext_siglum):
        """Run collation with automatic timing, then post-process the result.

        Calls collate(), fills in processing_duration if the engine didn't set it,
        and populates engine_usage with the engine name and algorithm.
        """
        start_time = time.time()
        result = self.collate(data, options, basetext_siglum)

        elapsed = round(time.time() - start_time, 1)

        # fill in processing_duration if the engine didn't set it
        if result.feedback.get('processing_duration') is None:
            result.feedback['processing_duration'] = elapsed

        # ensure engine_usage has at least engine name and algorithm
        if result.feedback.get('engine_usage') is None:
            result.feedback['engine_usage'] = {}
        usage = result.feedback['engine_usage']
        if 'engine' not in usage:
            usage['engine'] = self.name()
        if 'algorithm' not in usage:
            usage['algorithm'] = options.get('algorithm', '')
        if 'duration_seconds' not in usage:
            usage['duration_seconds'] = elapsed
        if 'summary' not in usage:
            usage['summary'] = '{} | {}s'.format(self.name(), elapsed)

        return self.process_result(result, data)

    def process_result(self, result, data):
        """Post-process a CollationResult: validate tokens, build HTML table, write debug log.

        Args:
            result: CollationResult from collate()
            data: the original witness data (for building token indices)

        Returns:
            JSON string of the output dict
        """
        # raw response bypass (e.g. CollateX returning bytes directly)
        if hasattr(result, '_raw_response') and result._raw_response:
            return result._raw_response

        output = result.to_output_dict()

        _, input_token_indices = build_token_lookup(data['witnesses'])

        check_ai_verify_block(output, input_token_indices)

        if output.get('table') and output.get('witnesses'):
            validation_errors = validate_token_integrity(
                output['table'], output['witnesses'], input_token_indices)
            if validation_errors:
                print('======= alignment validation errors: {}'.format(
                    '; '.join(validation_errors)), file=sys.stderr)
                output['table'] = []
                output['witnesses'] = []
                feedback = output.get('collation_feedback', {})
                feedback['comments'] = (
                    'Error: The collation engine produced an alignment with token integrity errors '
                    'and the result has been rejected to protect data quality. '
                    'Please try again. Details: ' +
                    '; '.join(validation_errors))
                output['collation_feedback'] = feedback

        feedback = output.get('collation_feedback', {})
        if (not feedback.get('alignment_table')
                and output.get('table') and output.get('witnesses')):
            feedback['alignment_table'] = build_html_alignment_table(
                output['table'], output['witnesses'])
            output['collation_feedback'] = feedback

        log_dir = self.algorithm_settings.get('debug_log_dir')
        if log_dir:
            try:
                import os
                log_path = os.path.join(log_dir, 'post_collation.json')
                with open(log_path, 'w', encoding='utf-8') as f:
                    f.write(json.dumps({'output': output}, ensure_ascii=False, indent=4))
            except Exception as e:
                print('======= error writing log: ' + str(e), file=sys.stderr)

        return json.dumps(output, ensure_ascii=False, indent=4)


# ---------------------------------------------------------------------------
# Engine registry
# ---------------------------------------------------------------------------

from collation.core.engines.collatex import CollatexEngine

_engine_registry = {}
_default_engine = CollatexEngine


def register_engine(name, engine_class, default=False):
    """Register a collation engine class by algorithm name.

    If default=True, this engine handles any algorithm name not
    explicitly registered (e.g. CollateX handles dekker, needleman-wunsch, etc.).
    """
    _engine_registry[name] = engine_class
    if default:
        global _default_engine
        _default_engine = engine_class


def get_engine(name, algorithm_settings):
    """Look up and instantiate a registered engine, or fall back to the default."""
    cls = _engine_registry.get(name, _default_engine)
    if cls is not None:
        return cls(algorithm_settings)
    return None


def list_engines():
    """Return list of registered engine names."""
    return list(_engine_registry.keys())


# ---------------------------------------------------------------------------
# Shared utilities used by engines and the preprocessor
# ---------------------------------------------------------------------------

def build_token_lookup(witnesses):
    """Build lookup dicts from a list of witness objects.

    Returns:
        token_lookup: {witness_id: {index: token_dict}}
        input_token_indices: {witness_id: set(indices)}
    """
    token_lookup = {}
    input_token_indices = {}
    for witness in witnesses:
        wit_id = witness['id']
        token_lookup[wit_id] = {}
        input_token_indices[wit_id] = set()
        for token in witness['tokens']:
            token_lookup[wit_id][token['index']] = token
            input_token_indices[wit_id].add(token['index'])
    return token_lookup, input_token_indices


def validate_token_integrity(table, witnesses, input_token_indices):
    """Check for duplicate or missing tokens in an alignment table.

    Returns:
        list of error strings (empty if valid)
    """
    errors = []
    for i, wit_id in enumerate(witnesses):
        seen_indices = []
        for cg in table:
            if i < len(cg):
                for token in cg[i]:
                    idx = token.get('index')
                    if idx in seen_indices:
                        errors.append(
                            'Duplicate token index {} in witness {}'.format(idx, wit_id))
                    else:
                        seen_indices.append(idx)
        if wit_id in input_token_indices:
            missing = input_token_indices[wit_id] - set(seen_indices)
            if missing:
                errors.append(
                    'Missing token indices {} in witness {}'.format(
                        sorted(missing, key=lambda x: int(x)), wit_id))
    return errors


def check_ai_verify_block(output, input_token_indices):
    """Validate an AI engine's self-check verify block if present.

    Removes the verify block from output after checking.

    Returns:
        list of error strings (empty if valid or no verify block)
    """
    verify = output.get('verify', {})
    if not verify:
        return []
    errors = []
    for wit_id, verify_indices in verify.items():
        if wit_id in input_token_indices:
            expected = input_token_indices[wit_id]
            got = set(verify_indices)
            if len(verify_indices) != len(got):
                dupes = [idx for idx in verify_indices if verify_indices.count(idx) > 1]
                errors.append(
                    'AI self-check: duplicates {} in witness {}'.format(
                        list(set(dupes)), wit_id))
            missing_v = expected - got
            extra = got - expected
            if missing_v:
                errors.append(
                    'AI self-check: missing {} in witness {}'.format(
                        sorted(missing_v, key=lambda x: int(x)), wit_id))
            if extra:
                errors.append(
                    'AI self-check: unexpected {} in witness {}'.format(
                        sorted(extra, key=lambda x: int(x)), wit_id))
    if errors:
        print('======= AI verify block errors: {}'.format(
            '; '.join(errors)), file=sys.stderr)
    del output['verify']
    return errors


def build_html_alignment_table(table, witnesses):
    """Build an HTML alignment table from collation output.

    Returns:
        HTML string
    """
    html = '<table><thead><tr><th>Witness</th>'
    col_headers = []
    pbt_col_num = 0
    for cg in table:
        if len(cg) > 0:
            max_in_cg = max(len(w) for w in cg) if any(cg) else 1
            pbt_count = len(cg[0]) if len(cg) > 0 else 0
            for c in range(max_in_cg):
                if c < pbt_count:
                    pbt_col_num += 2
                    col_headers.append(str(pbt_col_num))
                else:
                    col_headers.append('')
    for hdr in col_headers:
        html += '<th>{}</th>'.format(hdr)
    html += '</tr></thead><tbody>'
    for wit_i, wit_id in enumerate(witnesses):
        html += '<tr><td>{}</td>'.format(wit_id)
        for cg in table:
            if wit_i < len(cg):
                for token in cg[wit_i]:
                    html += '<td>{}</td>'.format(token.get('original', ''))
                max_in_cg = max(len(w) for w in cg) if any(cg) else 0
                for _ in range(max_in_cg - len(cg[wit_i])):
                    html += '<td></td>'
            else:
                html += '<td></td>'
        html += '</tr>'
    html += '</tbody></table>'
    return html


def parse_ai_json_response(text):
    """Parse JSON from an AI response that may include markdown fences or preamble.

    Returns:
        parsed dict, or raises an exception
    """
    text = text.strip()
    # strip markdown code fences if present
    if text.startswith('```'):
        first_newline = text.find('\n')
        if first_newline != -1:
            text = text[first_newline + 1:]
        if text.endswith('```'):
            text = text[:-3].strip()
    # fix trailing commas which are invalid JSON but sometimes produced by LLMs
    text = re.sub(r',\s*([}\]])', r'\1', text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # model may have included preamble text before the JSON;
        # try to find valid JSON by scanning for { and parsing from there
        for idx in range(len(text)):
            if text[idx] == '{':
                try:
                    candidate = re.sub(r',\s*([}\]])', r'\1', text[idx:])
                    return json.loads(candidate)
                except json.JSONDecodeError:
                    decoder = json.JSONDecoder()
                    try:
                        result, _ = decoder.raw_decode(candidate)
                        return result
                    except json.JSONDecodeError:
                        continue
        raise


def expand_compact_table(table, witnesses, token_lookup):
    """Expand a compact index-format table into full WordToken objects.

    In compact format, table cells contain string indices instead of
    full token objects. This reconstructs the full objects from the lookup.

    Returns:
        expanded table (list of column groups)
    """
    print('reconstructing WordTokens from compact index format', file=sys.stderr)
    expanded_table = []
    for cg in table:
        expanded_cg = []
        for i, indices in enumerate(cg):
            wit_id = witnesses[i] if i < len(witnesses) else None
            tokens = []
            for idx in indices:
                if wit_id and wit_id in token_lookup and idx in token_lookup[wit_id]:
                    tokens.append(token_lookup[wit_id][idx])
                else:
                    print('WARNING: token index {} not found for witness {}'.format(
                        idx, wit_id), file=sys.stderr)
            expanded_cg.append(tokens)
        expanded_table.append(expanded_cg)
    return expanded_table


def is_compact_format(table):
    """Check if a table uses compact index format (arrays of strings)
    vs full WordToken format (arrays of objects)."""
    return (len(table) > 0 and len(table[0]) > 0
            and any(len(cg_wit) > 0 for cg_wit in table[0])
            and isinstance(next(
                (item for cg_wit in table[0] for item in cg_wit), None
            ), str))


def compress_ai_request(data, basetext_siglum):
    """Build a compressed AI request from witness data.

    Compression rules (no data is lost):
    - 'verse' is hoisted to top level (same for all tokens)
    - 'reading' is omitted when it equals the witness id
    - 'siglum' is omitted when it equals the witness id
    - 't' is omitted when it equals 'original'
    - 'n' is omitted when absent or equals 't'
    - 'rule_match' is omitted when it equals [original]
    - 'decision_details' and 'decision_class' are omitted when absent
    - Uses compact JSON separators

    Returns:
        dict ready for json.dumps()
    """
    # extract verse from first token (same for all)
    verse = None
    for w in data['witnesses']:
        if w['tokens']:
            verse = w['tokens'][0].get('verse')
            break

    compressed_witnesses = []
    for w in data['witnesses']:
        wit_id = w['id']
        compressed_tokens = []
        for token in w['tokens']:
            ct = {
                'index': token['index'],
                'original': token['original'],
            }
            # only include fields that differ from defaults
            if token.get('t') and token['t'] != token['original']:
                ct['t'] = token['t']
            n_val = token.get('n')
            t_val = token.get('t', token['original'])
            if n_val and n_val != t_val:
                ct['n'] = n_val
            if token.get('siglum') and token['siglum'] != wit_id:
                ct['siglum'] = token['siglum']
            if token.get('reading') and token['reading'] != wit_id:
                ct['reading'] = token['reading']
            rule_match = token.get('rule_match')
            if rule_match and rule_match != [token['original']]:
                ct['rule_match'] = rule_match
            if 'decision_details' in token:
                ct['decision_details'] = token['decision_details']
            if 'decision_class' in token:
                ct['decision_class'] = token['decision_class']
            # preserve any other keys we don't know about
            for k in token:
                if k not in ('index', 'original', 't', 'n', 'siglum',
                             'reading', 'verse', 'rule_match',
                             'decision_details', 'decision_class'):
                    ct[k] = token[k]
            compressed_tokens.append(ct)
        compressed_witnesses.append({'id': wit_id, 'tokens': compressed_tokens})

    result = {
        'input': {'witnesses': compressed_witnesses},
        'basetext_siglum': basetext_siglum,
        'verse': verse,
        'output': {
            'ai_comments': '',
            'ai_alignment_table': '',
            'witnesses': [basetext_siglum],
            'table': []
        }
    }
    return result
