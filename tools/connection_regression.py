#!/usr/bin/env python3
"""Test only a uniquely named local container. Never changes Kubernetes or pushes."""
import concurrent.futures
import json
import socket
import subprocess
import sys
import time
import uuid


def docker(*args):
    return subprocess.check_output(['docker', *args], text=True, timeout=90).strip()


def main():
    image = sys.argv[1] if len(sys.argv) > 1 else 'wisecow:concurrent-v2'
    name = 'wisecow-concurrent-' + uuid.uuid4().hex[:12]
    started = False
    try:
        docker('run', '-d', '--pull', 'never', '--name', name, '--read-only', '--cap-drop', 'ALL',
               '--security-opt', 'no-new-privileges:true', '--memory', '128m',
               '--cpus', '0.25', '-p', '127.0.0.1::4499', image)
        started = True
        port = int(docker('port', name, '4499/tcp').rsplit(':', 1)[1])

        def get(_=None):
            with socket.create_connection(('127.0.0.1', port), timeout=3) as sock:
                sock.settimeout(6)
                sock.sendall(b'GET / HTTP/1.1\r\nHost: localhost\r\nConnection: keep-alive\r\n\r\n')
                raw = b''
                while True:
                    part = sock.recv(65536)
                    if not part:
                        break
                    raw += part
                    if len(raw) > 200000:
                        raise RuntimeError('Response too large')
            headers, body = raw.split(b'\r\n\r\n', 1)
            lines = headers.split(b'\r\n')
            fields = dict(line.split(b': ', 1) for line in lines[1:])
            if not lines[0].startswith(b'HTTP/1.1 200 ') or b'<pre>' not in body or b'^__^' not in body:
                raise RuntimeError('Missing HTTP 200 or real cow output')
            if int(fields[b'Content-Length']) != len(body) or fields[b'Connection'] != b'close':
                raise RuntimeError('Incorrect HTTP framing')
            return True

        for attempt in range(20):
            try:
                get()
                break
            except Exception:
                if attempt == 19:
                    raise
                time.sleep(.5)
        print('PASS: real cow, HTTP 200, exact framing and clean connection close', flush=True)
        time.sleep(.2)
        with socket.create_connection(('127.0.0.1', port), timeout=2) as idle:
            idle.settimeout(6)
            with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
                if not all(pool.map(get, range(8))):
                    raise RuntimeError('Parallel request failed')
            print('PASS: eight concurrent GETs while another peer is idle', flush=True)
            if idle.recv(1) != b'':
                raise RuntimeError('Idle peer did not close cleanly')
        print('PASS: idle peer closed cleanly', flush=True)
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            if not all(pool.map(get, range(24))):
                raise RuntimeError('Repeated parallel requests failed')
        print('PASS: twenty-four further requests with eight workers', flush=True)
        for _ in range(30):
            with socket.create_connection(('127.0.0.1', port), timeout=2):
                pass
            time.sleep(.03)
        get()
        state = json.loads(docker('inspect', '--format', '{{json .State}}', name))
        user = docker('inspect', '--format', '{{.Config.User}}', name)
        if not state.get('Running') or state.get('OOMKilled') or user != '10001:10001':
            raise RuntimeError('Container state or configured non-root user check failed')
        print('PASS: probe-like connects, later GET, running container, non-root user', flush=True)
        print('Docker resource snapshot:', flush=True)
        subprocess.run(['docker', 'stats', '--no-stream', '--format', '{{.MemUsage}} {{.CPUPerc}} {{.PIDs}}', name], check=False)
        print('This is local-container evidence only. kind, port-forward, Chrome and stability still require checks.', flush=True)
        return 0
    except Exception as exc:
        print('FAIL: %s: %s' % (type(exc).__name__, exc), flush=True)
        return 1
    finally:
        if started:
            subprocess.run(['docker', 'logs', '--tail', '30', name], check=False)
            subprocess.run(['docker', 'rm', '-f', name], check=False)


if __name__ == '__main__':
    raise SystemExit(main())
