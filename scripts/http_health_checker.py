#!/usr/bin/env python3
"""Check HTTP status, response time and observed uptime without third-party packages."""
import argparse
from datetime import datetime, timezone
import json
import math
import socket
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def positive_finite(value):
    number = float(value)
    if not math.isfinite(number) or number <= 0:
        raise argparse.ArgumentTypeError('must be finite and greater than zero')
    return number


def check(url, timeout=5.0):
    parsed = urlparse(url)
    if parsed.scheme not in {'http', 'https'} or not parsed.hostname:
        raise ValueError('Use an absolute http:// or https:// URL')
    if parsed.username is not None or parsed.password is not None:
        raise ValueError('Do not put credentials in the URL')
    start = time.monotonic()
    status, error = None, None
    try:
        request = Request(url, headers={'User-Agent': 'QA-Health-Check/1.0'}, method='GET')
        # Deliberately do not follow redirects: a login redirect is not app health.
        with build_opener(NoRedirect).open(request, timeout=timeout) as response:
            status = response.status
    except HTTPError as exc:
        status = exc.code
        exc.close()
    except (URLError, TimeoutError, socket.timeout, OSError) as exc:
        error = str(exc)
    return {'timestamp_utc': datetime.now(timezone.utc).isoformat(), 'url': url,
            'up': status is not None and 200 <= status < 300,
            'status_code': status, 'error': error,
            'response_time_ms': round((time.monotonic() - start) * 1000, 3)}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('url')
    parser.add_argument('--timeout', type=positive_finite, default=5.0)
    parser.add_argument('--checks', type=int, default=1)
    parser.add_argument('--interval', type=positive_finite, default=60.0,
                        help='seconds between completed checks (default: 60)')
    args = parser.parse_args(argv)
    if args.checks < 1:
        parser.error('--checks must be positive')
    results = []
    try:
        for i in range(args.checks):
            if i:
                time.sleep(args.interval)
            result = check(args.url, args.timeout)
            results.append(result)
            print(json.dumps(result), flush=True)
    except ValueError as exc:
        parser.error(str(exc))
    except KeyboardInterrupt:
        return 130
    up_count = sum(result['up'] for result in results)
    print(json.dumps({'summary': {'checks': len(results), 'up_checks': up_count,
                                 'observed_uptime_percent': round(100 * up_count / len(results), 2)}}))
    return 0 if up_count == len(results) else 1


if __name__ == '__main__':
    raise SystemExit(main())
