#!/usr/bin/env python3
"""Test the installed starter through PHP's HTTP server (Python 3.9+, standard library)."""
import http.cookiejar
import json
import os
from pathlib import Path
import re
import shlex
import socket
import subprocess
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parent.parent
PHP = shlex.split(os.environ.get('PHP_COMMAND', 'php'))


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def main():
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        port = sock.getsockname()[1]
    opener = urllib.request.build_opener(
        NoRedirect(), urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
    checks = 0

    def expect(condition, message):
        nonlocal checks
        if not condition:
            raise AssertionError(message)
        checks += 1
        print('PASS', message, flush=True)

    def request(path, data=None):
        body = urllib.parse.urlencode(data).encode() if data is not None else None
        req = urllib.request.Request(f'http://127.0.0.1:{port}{path}', data=body)
        try:
            result = opener.open(req, timeout=5)
        except urllib.error.HTTPError as error:
            result = error
        with result:
            return result.status, result.headers, result.read().decode()

    def token():
        status, _, body = request('/contact')
        match = re.search(r'name="_csrf" value="([^"]+)"', body)
        expect(status == 200 and match is not None, 'Contact page renders a CSRF token')
        return match[1]

    with tempfile.TemporaryDirectory(prefix='naf-app-smoke-') as tmp:
        with tempfile.TemporaryFile(mode='w+') as log:
            process = subprocess.Popen(
                [*PHP, '-d', f'session.save_path={tmp}', '-S', f'127.0.0.1:{port}', '-t', 'public'],
                cwd=ROOT, env={**os.environ, 'APP_ENV': 'dev'}, stdout=log, stderr=log)
            try:
                for _ in range(100):
                    if process.poll() is not None:
                        raise RuntimeError('PHP server stopped before becoming ready')
                    try:
                        with socket.create_connection(('127.0.0.1', port), timeout=.2):
                            break
                    except OSError:
                        time.sleep(.05)
                else:
                    raise RuntimeError('PHP server readiness timed out')

                status, _, body = request('/')
                expect(status == 200 and 'Welcome to your new App!' in body, 'Welcome page renders')
                status, headers, body = request('/css/naf.css')
                expect(status == 200 and 'text/css' in headers.get('Content-Type', '') and body,
                       'Public CSS is served')
                expect(request('/contact', {'firstname': 'Ada'})[0] == 400,
                       'Contact rejects missing CSRF token')
                expect(request('/api', {'name': 'Ada'})[0] == 400, 'API rejects missing CSRF token')
                status, _, body = request('/contact', {
                    '_csrf': token(), 'firstname': 'Ada', 'lastname': 'Lovelace', 'message': 'short'})
                expect(status == 200 and 'At least 10' in body and 'value="Ada"' in body,
                       'Invalid contact shows validation errors and retains input')
                status, headers, _ = request('/contact', {
                    '_csrf': token(), 'firstname': 'Ada', 'lastname': 'Lovelace',
                    'message': 'Hello from the starter smoke test.'})
                expect(status == 302 and headers.get('Location') == '/contact',
                       'Valid contact returns a usable HTTP redirect')
                status, headers, body = request('/api', {'_csrf': token(), 'name': ''})
                expect(status == 422 and 'name' in json.loads(body)['fields'],
                       'Invalid API input returns field errors')
                status, headers, body = request('/api', {'_csrf': token(), 'name': 'Ada'})
                expect(status == 200 and json.loads(body) == {'data': {'hello': 'Ada'}}
                       and 'application/json' in headers.get('Content-Type', ''),
                       'Valid API input returns the expected JSON response')
            except Exception:
                log.seek(0)
                print(log.read()[-6000:])
                raise
            finally:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
    print(f'PASS {checks} HTTP checks')


if __name__ == '__main__':
    main()
