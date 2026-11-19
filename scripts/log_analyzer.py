#!/usr/bin/env python3
"""Summarize Apache/Nginx common or combined access logs as JSON."""
import argparse
from collections import Counter
import json
from pathlib import Path
import re
import sys

# Use the first (remote-address) field, not X-Forwarded-For or an authenticated user.
LINE = re.compile(
    r'^(?P<ip>\S+) \S+ \S+ \[[^\]]+\] '
    r'"(?P<method>[^"\s]+) (?P<path>[^"\s]+) HTTP/\d(?:\.\d)?" '
    r'(?P<status>\d{3}) (?P<bytes>\d+|-)(?:\s.*)?$'
)


def analyze(lines, top=10):
    ips, pages, statuses = Counter(), Counter(), Counter()
    total = valid = malformed = 0
    for raw in lines:
        total += 1
        match = LINE.fullmatch(raw.rstrip('\r\n'))
        if not match or not 100 <= int(match['status']) <= 599:
            malformed += 1
            continue
        valid += 1
        ips[match['ip']] += 1
        pages[match['path']] += 1
        statuses[match['status']] += 1
    # Stable ordering makes reports reproducible even when counts tie.
    def ranked(counter):
        return [{'value': value, 'count': count}
                for value, count in sorted(counter.items(), key=lambda x: (-x[1], x[0]))[:top]]
    return {'total_lines': total, 'valid_requests': valid, 'malformed_lines': malformed,
            'errors_404': statuses['404'], 'status_counts': dict(sorted(statuses.items())),
            'top_pages': ranked(pages), 'top_ips': ranked(ips)}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('log', type=Path)
    parser.add_argument('--top', type=int, default=10)
    args = parser.parse_args(argv)
    if args.top < 1:
        parser.error('--top must be a positive integer')
    try:
        with args.log.open(encoding='utf-8', errors='replace') as source:
            report = analyze(source, args.top)
    except OSError as exc:
        print(f'Cannot read log: {exc}', file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
