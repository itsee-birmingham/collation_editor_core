# -*- coding: utf-8 -*-
"""CollateX collation engine — sends data to the CollateX Java microservice."""
import json
import sys
import urllib.request

from collation.core.collation_engine import CollationEngine, CollationResult


class CollatexEngine(CollationEngine):

    _engine_meta = {
        'display_name': 'CollateX',
        'model_override_key': 'collatex_algorithm',
    }

    _models = [
        {'id': 'dekker', 'name': 'Dekker', 'max_tokens': 0, 'default': True},
        {'id': 'needleman-wunsch', 'name': 'Needleman-Wunsch', 'max_tokens': 0},
    ]

    def name(self):
        return 'collatex'

    def collate(self, data, options, basetext_siglum):
        host = self.algorithm_settings.get('collatexHost', 'http://localhost:7369/collate')
        algorithm = self.algorithm_settings.get('collatex_algorithm') or options.get('algorithm', 'dekker')

        witnesses = data.get('witnesses', [])
        word_counts = [len(w.get('tokens', [])) for w in witnesses]
        self._write_conversation_log(
            'algorithm={} host={}\n{} witnesses, {} to {} words each'.format(
                algorithm, host, len(witnesses), min(word_counts), max(word_counts)))

        if 'algorithm' in options:
            data['algorithm'] = options['algorithm']
        if 'tokenComparator' in options:
            data['tokenComparator'] = options['tokenComparator']

        json_witnesses = json.dumps(data)
        if 'outputFormat' in options:
            accept_header = self._convert_header(options['outputFormat'])
        else:
            accept_header = 'application/json'

        req = urllib.request.Request(host)
        req.add_header('content-type', 'application/json')
        req.add_header('Accept', accept_header)

        try:
            response = urllib.request.urlopen(req, json_witnesses.encode('utf-8'))
        except Exception as e:
            self._write_conversation_log('+++ ERROR: CollateX service unavailable: {} +++'.format(e))
            raise

        response_body = response.read()

        algorithm_name = self.get_model_names().get(algorithm, algorithm)
        fuzzy = 'with' if self.algorithm_settings.get('fuzzy_match') else 'without'

        result = CollationResult()
        try:
            response_json = json.loads(response_body)
            result.table = response_json.get('table', [])
            result.witnesses = response_json.get('witnesses', [])
            self._write_conversation_log('+++ SUCCESS: {} CGs, {} witnesses +++'.format(
                len(result.table), len(result.witnesses)))
            result.feedback['comments'] = (
                'CollateX {} {} fuzzy match: {} column groups, {} witnesses with between {} and {} words each'.format(
                    algorithm_name, fuzzy, len(result.table), len(result.witnesses),
                    min(word_counts), max(word_counts)))
            result.feedback['engine_usage'] = {
                'engine': 'collatex',
                'model': algorithm,
                'model_name': algorithm_name,
                'summary': 'CollateX {}'.format(algorithm_name),
            }
        except Exception as e:
            print('======= error parsing CollateX result as json: ' + str(e), file=sys.stderr)
            self._write_conversation_log('+++ JSON PARSE ERROR: {} +++'.format(e))
            result.feedback['comments'] = 'Error parsing CollateX response: {}'.format(e)
            # return raw response as-is for backward compatibility
            result._raw_response = response_body
        return result

    @staticmethod
    def _convert_header(accept):
        if accept == 'json' or accept == 'lcs':
            return 'application/json'
        elif accept == 'tei':
            return 'application/tei+xml'
        elif accept == 'graphml':
            return 'application/graphml+xml'
        elif accept == 'dot':
            return 'text/plain'
        elif accept == 'svg':
            return 'image/svg+xml'
        return 'application/json'
