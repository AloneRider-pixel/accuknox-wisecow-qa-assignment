import contextlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import io
import json
from pathlib import Path
import socket
import subprocess
import sys
import threading
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import log_analyzer as logs
import http_health_checker as health


def entry(status=200, path='/', ip='192.0.2.1', extra=''):
    return f'{ip} - - [13/Nov/2026:10:00:00 +0000] "GET {path} HTTP/1.1" {status} 42{extra}\n'


class LogTests(unittest.TestCase):
    def test_fixture(self):
        with (ROOT / 'fixtures/access.log').open() as f:
            result = logs.analyze(f)
        self.assertEqual((result['total_lines'], result['valid_requests'], result['malformed_lines']), (6, 5, 1))
        self.assertEqual(result['errors_404'], 2)

    def test_empty(self):
        self.assertEqual(logs.analyze([])['valid_requests'], 0)

    def test_common(self):
        self.assertEqual(logs.analyze([entry()])['status_counts'], {'200': 1})

    def test_combined(self):
        self.assertEqual(logs.analyze([entry(extra=' "-" "Browser"')])['valid_requests'], 1)

    def test_invalid(self):
        self.assertEqual(logs.analyze(['bad\n', '\n'])['malformed_lines'], 2)

    def test_status_range(self):
        self.assertEqual(logs.analyze([entry(999)])['malformed_lines'], 1)

    def test_404_count(self):
        self.assertEqual(logs.analyze([entry(404), entry(500), entry(404)])['errors_404'], 2)

    def test_tie_order(self):
        self.assertEqual([p['value'] for p in logs.analyze([entry(path='/z'), entry(path='/a')])['top_pages']], ['/a', '/z'])

    def test_top_limit(self):
        self.assertEqual(len(logs.analyze([entry(path='/a'), entry(path='/b')], 1)['top_pages']), 1)

    def test_ipv6(self):
        self.assertEqual(logs.analyze([entry(ip='2001:db8::1')])['top_ips'][0]['value'], '2001:db8::1')

    def test_query_preserved(self):
        self.assertEqual(logs.analyze([entry(path='/a?q=1')])['top_pages'][0]['value'], '/a?q=1')

    def test_missing_file_cli(self):
        result = subprocess.run([sys.executable, 'scripts/log_analyzer.py', '/no-such-file'], cwd=ROOT, capture_output=True)
        self.assertEqual(result.returncode, 2)

    def test_bad_top_cli(self):
        result = subprocess.run([sys.executable, 'scripts/log_analyzer.py', 'fixtures/access.log', '--top', '0'], cwd=ROOT, capture_output=True)
        self.assertEqual(result.returncode, 2)

    def test_json_cli(self):
        result = subprocess.run([sys.executable, 'scripts/log_analyzer.py', 'fixtures/access.log'], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(json.loads(result.stdout)['errors_404'], 2)


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/slow':
            time.sleep(0.2)
        code = {'/ok': 200, '/created': 201, '/empty': 204, '/bad': 404, '/error': 500, '/redirect': 302}.get(self.path, 200)
        self.send_response(code)
        if code == 302:
            self.send_header('Location', '/ok')
        self.end_headers()
    def log_message(self, *_):
        pass


class HealthTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.url = f'http://127.0.0.1:{cls.server.server_port}'

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def test_200(self):
        self.assertTrue(health.check(self.url + '/ok')['up'])

    def test_201(self):
        self.assertTrue(health.check(self.url + '/created')['up'])

    def test_204(self):
        self.assertTrue(health.check(self.url + '/empty')['up'])

    def test_404(self):
        result = health.check(self.url + '/bad')
        self.assertFalse(result['up'])
        self.assertEqual(result['status_code'], 404)

    def test_500(self):
        self.assertFalse(health.check(self.url + '/error')['up'])

    def test_redirect_not_followed(self):
        result = health.check(self.url + '/redirect')
        self.assertEqual(result['status_code'], 302)
        self.assertFalse(result['up'])

    def test_timeout(self):
        result = health.check(self.url + '/slow', timeout=0.03)
        self.assertFalse(result['up'])
        self.assertIsNotNone(result['error'])

    def test_refused_connection(self):
        with socket.socket() as s:
            s.bind(('127.0.0.1', 0))
            port = s.getsockname()[1]
            result = health.check(f'http://127.0.0.1:{port}', timeout=0.1)
        self.assertFalse(result['up'])
        self.assertIsNotNone(result['error'])

    def test_invalid_scheme(self):
        with self.assertRaises(ValueError):
            health.check('file:///etc/passwd')

    def test_missing_host(self):
        with self.assertRaises(ValueError):
            health.check('https://')

    def test_credential_url(self):
        with self.assertRaises(ValueError):
            health.check('https://name:password@example.test')

    def test_response_timing(self):
        self.assertGreaterEqual(health.check(self.url + '/ok')['response_time_ms'], 0)

    def test_uptime_summary(self):
        with contextlib.redirect_stdout(io.StringIO()) as out:
            result = health.main([self.url + '/ok', '--checks', '2', '--interval', '0.01'])
        self.assertEqual(result, 0)
        self.assertEqual(json.loads(out.getvalue().splitlines()[-1])['summary']['observed_uptime_percent'], 100)

    def test_down_exit(self):
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(health.main([self.url + '/error']), 1)

    def test_nan_rejected(self):
        with self.assertRaises(Exception):
            health.positive_finite('nan')

    def test_negative_timeout_cli(self):
        result = subprocess.run([sys.executable, 'scripts/http_health_checker.py', self.url, '--timeout', '-1'], cwd=ROOT, capture_output=True)
        self.assertEqual(result.returncode, 2)

    def test_invalid_count_cli(self):
        result = subprocess.run([sys.executable, 'scripts/http_health_checker.py', self.url, '--checks', '0'], cwd=ROOT, capture_output=True)
        self.assertEqual(result.returncode, 2)


if __name__ == '__main__':
    unittest.main()
