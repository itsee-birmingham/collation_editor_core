# -*- coding: utf-8 -*-
"""CollateX collation engine — sends data to the CollateX Java microservice."""
import json
import sys
import urllib.request

from collation.core.collation_engine import CollationEngine, CollationResult


class CollatexEngine(CollationEngine):

    def name(self):
        return 'collatex'

    def collate(self, data, options, basetext_siglum):
        host = self.algorithm_settings.get('collatexHost', 'http://localhost:7369/collate')

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

        response = urllib.request.urlopen(req, json_witnesses.encode('utf-8'))
        response_body = response.read()

        result = CollationResult()
        try:
            response_json = json.loads(response_body)
            result.table = response_json.get('table', [])
            result.witnesses = response_json.get('witnesses', [])
        except Exception as e:
            print('======= error parsing CollateX result as json: ' + str(e), file=sys.stderr)
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
