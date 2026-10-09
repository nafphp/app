#!/usr/bin/env python3
"""Test the installed starter through PHP's HTTP server (Python 3.9+, standard library)."""
import http.cookiejar
import json
import os
from pathlib import Path
import re
import shlex
import shutil
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

    def request(path, data=None, binary=False, headers=None):
        body = urllib.parse.urlencode(data).encode() if data is not None else None
        req = urllib.request.Request(f'http://127.0.0.1:{port}{path}', data=body, headers=headers or {})
        try:
            result = opener.open(req, timeout=5)
        except urllib.error.HTTPError as error:
            result = error
        with result:
            body = result.read()
            return result.status, result.headers, body if binary else body.decode()

    def token(path='/contact'):
        status, _, body = request(path)
        match = re.search(r'name="_csrf" value="([^"]+)"', body)
        expect(status == 200 and match is not None, f'{path} renders a CSRF token')
        return match[1]

    with tempfile.TemporaryDirectory(prefix='naf-app-smoke-') as tmp:
        # Exercise a disposable host, including the documented removal of demo files.
        host = Path(tmp) / 'app'
        host.mkdir()
        for name in ('app', 'public', 'vendor'):
            shutil.copytree(ROOT / name, host / name)
        for name in ('bootstrap.php', 'composer.json', 'composer.lock'):
            shutil.copy2(ROOT / name, host / name)
        with tempfile.TemporaryFile(mode='w+') as log:
            process = subprocess.Popen(
                # These fixtures edit PHP between requests; bypass opcode revalidation delays.
                [*PHP, '-d', 'opcache.enable=0', '-d', f'session.save_path={tmp}',
                 '-S', f'127.0.0.1:{port}', '-t', str(host / 'public')],
                cwd=tmp, env={**os.environ, 'APP_ENV': 'dev'}, stdout=log, stderr=log)
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
                expect('<blockquote>' in body and '<figcaption>' in body, 'Starter keeps its quotes and authors')
                expect('/images/naf-mark.png' in body and 'width="48" height="48"' in body,
                       'Header uses the square logo without a wordmark')
                expect('name="viewport"' in body and 'class="skip-link"' in body, 'Layout supports mobile screens and keyboard navigation')
                expect('Keep the framework. Lose the demo.' in body and 'composer create-project naf/app my-next-app' in body,
                       'Welcome explains removing the demos and starting a fresh project')
                expect('action="/api"' in body and 'name="_csrf"' in body, 'Welcome exposes the CSRF-protected JSON demo')
                expect('data-demo="contact"' in body and 'data-demo="api"' in body,
                       'Both interactive examples are available on the welcome page')
                tokens = re.findall(r'name="_csrf" value="([^"]+)"', body)
                expect(len(tokens) == 2 and len(set(tokens)) == 1, 'Welcome forms share one generated CSRF token')
                configuration = host / 'app/config.php'
                original_configuration = configuration.read_text()
                configuration.write_text("<?php return ['showQuote' => false];\n")
                expect('<blockquote>' not in request('/')[2], 'Quote can be hidden through application configuration')
                configuration.write_text(original_configuration)
                status, headers, image = request('/images/naf-mark.png', binary=True)
                expect(status == 200 and 'image/png' in headers.get('Content-Type', '') and image.startswith(b'\x89PNG'),
                       'Public logo asset is served')
                status, headers, body = request('/css/naf.css')
                expect(status == 200 and 'text/css' in headers.get('Content-Type', '') and body,
                       'Public CSS is served')
                status, headers, body = request('/js/demo.js')
                expect(status == 200 and 'javascript' in headers.get('Content-Type', '') and body,
                       'Interactive demo JavaScript is served')
                expect(request('/contact', {'firstname': 'Ada'})[0] == 400,
                       'Contact rejects missing CSRF token')
                expect(request('/api', {'name': 'Ada'})[0] == 400, 'API rejects missing CSRF token')
                status, _, body = request('/contact')
                expect(status == 200 and '/images/naf-mark.png' in body and 'Nothing is sent or stored.' in body,
                       'Contact shares the layout and explains the demo limits')
                status, _, body = request('/contact', {
                    '_csrf': token(), 'firstname': 'Ada', 'lastname': 'Lovelace', 'message': 'short'})
                expect(status == 200 and 'At least 10' in body and 'value="Ada"' in body,
                       'Invalid contact shows validation errors and retains input')
                status, _, body = request('/contact', {
                    '_csrf': token(), 'firstname': '<script>alert(1)</script>', 'lastname': 'Lovelace',
                    'message': '<b>x</b>'})
                expect(status == 200 and '&lt;script&gt;alert(1)&lt;/script&gt;' in body
                       and '&lt;b&gt;x&lt;/b&gt;' in body and '<script>alert(1)</script>' not in body,
                       'Invalid contact escapes input fields and textarea values')
                expect('aria-invalid="true"' in body and 'id="message-error"' in body,
                       'Validation errors are associated with their fields')
                expect(request('/contact', {'_csrf': token(), 'firstname[]': 'Ada', 'lastname': 'Lovelace',
                                            'message': 'A valid length message.'})[0] == 400,
                       'Contact rejects array input before validation or rendering')
                status, headers, _ = request('/contact', {
                    '_csrf': token(), 'firstname': 'Ada', 'lastname': 'Lovelace',
                    'message': 'Hello from the starter smoke test.'})
                expect(status == 302 and headers.get('Location') == '/contact',
                       'Valid contact returns a usable HTTP redirect')
                status, headers, body = request('/api', {'_csrf': token(), 'name': ''})
                expect(status == 422 and 'name' in json.loads(body)['fields'],
                       'Invalid API input returns field errors')
                status, _, body = request('/api', {'_csrf': token('/'), 'name[]': 'Ada'})
                expect(status == 422 and 'name' in json.loads(body)['fields'], 'API rejects array input as JSON field errors')
                status, headers, body = request('/api', {'_csrf': token('/'), 'name': 'Ada'})
                expect(status == 200 and json.loads(body) == {'data': {'hello': 'Ada'}}
                       and 'application/json' in headers.get('Content-Type', ''),
                       'Valid API input returns the expected JSON response')
                accepts_json = {'Accept': 'application/json'}
                expect(request('/contact', {'firstname': 'Ada'}, headers=accepts_json)[0] == 400,
                       'Interactive contact still rejects missing CSRF tokens')
                shared_token = token('/')
                status, headers, body = request('/contact', {
                    '_csrf': shared_token, 'firstname': '', 'lastname': '', 'message': 'short'}, headers=accepts_json)
                expect(status == 422 and set(json.loads(body)['fields']) == {'firstname', 'lastname', 'message'}
                       and 'application/json' in headers.get('Content-Type', ''),
                       'Interactive contact returns JSON field errors with HTTP 422')
                status, _, body = request('/contact', {
                    '_csrf': shared_token, 'firstname[]': 'Ada', 'lastname': 'Lovelace',
                    'message': 'A valid length message.'}, headers=accepts_json)
                expect(status == 422 and 'firstname' in json.loads(body)['fields'],
                       'Interactive contact rejects arrays as JSON field errors')
                for attempt in range(2):
                    status, headers, body = request('/contact', {
                        '_csrf': shared_token, 'firstname': 'Ada', 'lastname': 'Lovelace',
                        'message': 'Hello from the interactive starter.'}, headers=accepts_json)
                    expect(status == 200 and 'Location' not in headers
                           and json.loads(body)['data']['message'] == 'Your form passed validation. Nothing was sent or stored.',
                           f'Interactive contact succeeds without redirect or token rotation (attempt {attempt + 1})')
                status, _, body = request('/api', {'_csrf': shared_token, 'name': 'Grace'}, headers=accepts_json)
                expect(status == 200 and json.loads(body) == {'data': {'hello': 'Grace'}},
                       'API remains usable after contact submissions with the shared page token')
                # Replace the routes before removing their controller, as the welcome page explains.
                (host / 'app/routes.php').write_text("""<?php
use App\\Controllers\\HomeController;
use function Naf\\route;
route()->add('GET', '/', [HomeController::class, 'index'], 'home');
""")
                (host / 'app/Controllers/HomeController.php').write_text("""<?php
namespace App\\Controllers;
use Psr\\Http\\Message\\ResponseInterface;
use function Naf\\View\\render;
final class HomeController
{
    public function index(): ResponseInterface
    {
        return render('home');
    }
}
""")
                (host / 'app/views/home.phtml').write_text('<!doctype html><h1>My own application</h1>\n')
                for name in ('app/Controllers/WebsiteController.php', 'app/Service/QuoteService.php',
                             'app/views/welcome.phtml', 'app/views/contact.phtml',
                             'app/views/partials/contact-form.phtml', 'app/Jobs/SendMailJob.php'):
                    (host / name).unlink()
                configuration.write_text('<?php return [];\n')
                status, _, body = request('/')
                expect(status == 200 and 'My own application' in body, 'Application works after replacing routes and removing all demo PHP')
                expect(request('/contact')[0] == 404, 'Removed contact demo has no remaining route')
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
