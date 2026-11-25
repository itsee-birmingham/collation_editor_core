"""CollateX collation engine: the CollateX Java microservice over HTTP (the default engine)."""

import json
import logging
import urllib.request

from collation.core.collation_engine import CollationEngine, CollationResult

logger = logging.getLogger(__name__)

# Seconds to wait for the CollateX microservice. Applies to connect AND to each
# socket read -- and since CollateX sends nothing at all until the collation is
# finished, in practice this is the whole budget for the run.
#
# Deliberately very generous. A verse-sized collation returns in milliseconds,
# but a large one -- e.g. John.11 against all available witnesses, approaching
# 1000 -- can legitimately grind for a long time, and timing out a real result
# after the editor has waited that long is far worse than waiting longer. The
# point of the bound is only to stop an UNBOUNDED process leak when the service
# is dead (see the note at the urlopen call), not to police slow collations.
# Override per project with the collatex_timeout algorithm setting.
DEFAULT_COLLATEX_TIMEOUT = 3600

_ACCEPT_HEADERS = {
    'json': 'application/json',
    'lcs': 'application/json',
    'tei': 'application/tei+xml',
    'graphml': 'application/graphml+xml',
    'dot': 'text/plain',
    'svg': 'image/svg+xml',
}


class CollatexEngine(CollationEngine):
    """Collation engine backed by the CollateX Java microservice."""

    _engine_meta = {
        'display_name': 'CollateX',
        'aligner_label': 'Algorithm',
        'aligner_key': 'collatex_algorithm',
    }

    _aligners = [
        {'id': 'dekker', 'name': 'Dekker', 'default': True},
        {'id': 'needleman-wunsch', 'name': 'Needleman-Wunsch'},
    ]

    def name(self):
        """Return the registry name of this engine."""
        return 'collatex'

    def collate(self, data, options, basetext_siglum):
        """POST the witnesses to CollateX and return its alignment table."""
        host = self.algorithm_settings.get('collatexHost', 'http://localhost:7369/collate')
        algorithm = self.algorithm_settings.get('collatex_algorithm') or options.get('algorithm', 'dekker')
        logger.info('collatex algorithm=%s host=%s witnesses=%d', algorithm, host, len(data.get('witnesses', [])))

        data['algorithm'] = algorithm
        if 'tokenComparator' in options:
            data['tokenComparator'] = options['tokenComparator']

        req = urllib.request.Request(host)
        req.add_header('content-type', 'application/json')
        req.add_header('Accept', _ACCEPT_HEADERS.get(options.get('outputFormat'), 'application/json'))

        # Without an explicit timeout urllib blocks in recv() indefinitely. On
        # 2026-08-20 a JVM upgrade left the CollateX service accepting connections
        # but never replying, and because this call could not time out, 28
        # collation processes accumulated over 16 hours -- one per request,
        # each pinning a socket and ~36 MB -- until the host ran short of memory.
        # A bounded wait turns a dead service into a prompt, visible error.
        try:
            timeout = float(self.algorithm_settings.get('collatex_timeout') or DEFAULT_COLLATEX_TIMEOUT)
        except (TypeError, ValueError):
            timeout = DEFAULT_COLLATEX_TIMEOUT

        try:
            response = urllib.request.urlopen(req, json.dumps(data).encode('utf-8'), timeout=timeout)
        except Exception:
            logger.error('CollateX service at %s unavailable after %ss', host, timeout)
            raise

        response_body = response.read()
        try:
            response_json = json.loads(response_body)
        except ValueError:
            # not JSON (another outputFormat was requested): hand it back untouched
            logger.info('CollateX returned a non-JSON response; passing it through')
            result = CollationResult()
            result._raw_response = response_body
            return result
        return CollationResult(witnesses=response_json.get('witnesses', []), table=response_json.get('table', []))
