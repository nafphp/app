# Working with naf/app

NAF is a small PHP framework with optional Composer plugins. The core provides boot,
configuration, a service container, routing, events and PSR-7 responses. This repository is
the `naf/app` **project starter**, not a plugin or a library to install inside another app.
It supplies the host's entry point, application classes, routes and templates.

This file is also copied into projects created from the starter. Check the Git remote and
the actual `composer.json` before acting: when maintaining `nafphp/app`, follow the
[NAF contribution workflow](https://github.com/nafphp/docs/blob/main/AGENT_WORKFLOW.md) and
[release procedure](https://github.com/nafphp/docs/blob/main/RELEASING.md). NAF source fixes
use an RC branch and the maintainer merges them; verified NAF documentation-only changes
may be merged by the agent. Those publication permissions do **not** transfer to a user's
generated application. Follow that application's maintainer instructions instead.
Preserve existing changes and review documentation with every behavior change.

## Start and verify an installation

Read [composer.json](composer.json), [composer.lock](composer.lock),
[bootstrap.php](bootstrap.php) and [public/index.php](public/index.php). The starter requires
PHP 8.3+ and installs `naf/framework`, `naf/form` and `naf/view`; `naf/session` is a transitive
dependency. Check Composer for their extension requirements. A sibling workspace directory
does not install a package.

Use an unused test directory outside the source checkout. For a new application:

```sh
composer create-project naf/app nafphp-agent-demo
cd nafphp-agent-demo
APP_ENV=dev php -S 127.0.0.1:8080 -t public
```

The starter requires at least framework 0.2.2 and form 0.2.3: framework 0.2.2 fixes
development-server redirects, form 0.2.3 checks CSRF for every state-changing method and adds
`csrf()->token()`. New installations work without a separate dependency update. In
applications created from older starters, run
`composer require 'naf/framework:^0.2.2' 'naf/form:^0.2.3' --with-all-dependencies` to adopt
these minimums. To test changes to the starter itself, copy the changed tree into a disposable
host and run `composer install` followed by `composer test`; `create-project` alone only tests
the published starter. Release dependencies before updating the starter's lock file, and
verify the locked, latest compatible and minimum supported dependency sets before release.
The starter also excludes `nyholm/psr7` below 1.8.2: its implicit-nullability deprecations
on PHP 8.4+ become HTTP errors through NAF's error handler. Keep this transitive compatibility
constraint until the required framework versions enforce an equivalent minimum themselves.

Run the development server from the application root and serve only `public/`. The
bootstrap and front controller resolve includes relative to their own files. Use paths
based on `__DIR__`, define `BASE_PATH` before the first `app()` call, and register services
before `app()->run()`.
Configure production servers to route application requests through `public/index.php`.
Keep local environment files and secrets out of commits; the starter's ignore list does not
exclude `.env`. When present, `.env.local` replaces `.env`; NAF environment names are
`dev`, `test` and `prod`.

## Where application changes belong

- [app/routes.php](app/routes.php) registers routes with unique names. Keep it declarative: the first
  `app()` call boots plugins and loads routes before later bootstrap service bindings exist.
- [app/Controllers](app/Controllers/) contains ordinary PHP controllers; Composer maps
  `App\` to `app/`. Preserve filename/namespace case. Keep business rules in application
  services, such as [app/Service](app/Service/), rather than growing controllers.
- [app/config.php](app/config.php) returns configuration; `Naf\config()` reads it and uses
  colon-separated nested keys. It is not a configuration setter.
- [app/views](app/views/) contains `naf/view` templates, layouts and blocks;
  [public](public/) contains public assets. Use `render()` for a response, `view()` for a
  string, `asset()` for assets, and `s()` to escape HTML text and quoted attributes.

Prefer existing NAF functions, dependency injection, validation rules, events and plugin
interfaces. Fix reusable framework/plugin defects in their owning package instead of copying
internals into this starter or changing installed vendor files. Add optional packages only
for features the application needs; inspect their own `AGENTS.md` and user guides.

## Examples to adapt

Create `app/Controllers/GreetingController.php`:

```php
<?php

declare(strict_types=1);

namespace App\Controllers;

use App\Service\QuoteService;
use Psr\Http\Message\ResponseInterface;

use function Naf\json;

final class GreetingController
{
    public function __construct(private readonly QuoteService $quotes)
    {
    }

    public function show(string $name): ResponseInterface
    {
        return json(['hello' => $name, 'quote' => $this->quotes->getRandomQuote()]);
    }
}
```

Add this registration to the existing `app/routes.php`, reusing its `route` import:

```php
<?php
use App\Controllers\GreetingController;
use function Naf\route;

route()->add('GET', '/greet/{name}', [GreetingController::class, 'show'], 'greeting');
```

The default dispatcher autowires concrete constructor dependencies; the action receives
the route's named `$name` parameter, not method injection. `WebsiteController` receives
`QuoteService` through the same constructor injection; no string service binding is needed.
If consumers need the same configured instance, register it under its class name. `get()` retrieves
registered services; `make()` constructs classes. Bind interfaces and scalar configuration
explicitly. See the [DI guide](https://nafphp.github.io/docs/dependency-injection/).

For a form template, wrap sticky user input with escaping:

```php
<?php
use function Naf\Form\memory;
use function Naf\View\s;
?>
<input name="firstname" value="<?= s(memory('firstname')) ?>">
```

`memory()` reads the current request; it does not escape HTML or survive a redirect. The
starter controller checks input types and passes explicit values to its form; the template
escapes those values with `s()`. Validate input types and fields with
`validator()->validate(...)`, inspect `isValid()`, and retain CSRF protection.
Generate a token once per rendered page and reuse it. A Bearer header alone is not authentication.
Return `json()`, `render()` or `redirect()` responses from handlers and let NAF emit them.

## Know the demonstration's limits

The [contact action](app/Controllers/WebsiteController.php) validates and redirects; it does
not send or persist a message. With `Accept: application/json`, it returns JSON field errors
with status 422 or a success response with status 200. The welcome and contact pages share
[the form template](app/views/partials/contact-form.phtml); generate their CSRF token once in
the parent page. [public/js/demo.js](public/js/demo.js) progressively enhances both examples
with `fetch()`, keeping the CSRF token and same-origin session cookies. Do not generate a new
token for each JSON response: both forms on the welcome page share the original token.
[SendMailJob](app/Jobs/SendMailJob.php) is an unused example
requiring `naf/queue`/`naf/cli`, which the starter does not install; it only logs and prints.
Neither is a ready mail integration. For delivery, install `naf/mail` and use its mailer;
for tests, explicitly bind the [documented dummy or file transport](https://nafphp.github.io/docs/mail/).

Run `composer validate --strict` and `composer test` (Python 3.9+ is needed only for the test
runner). The HTTP smoke test starts and stops its own PHP server on a free loopback port;
set `PHP_COMMAND='php -n'` only when needed for a broken local INI configuration and all
required extensions are built in. CI runs the test on PHP 8.3 and 8.5 with locked, latest and
lowest dependencies. It checks welcome/assets, contact rendering, CSRF rejection, validation,
redirect status/Location, input escaping/types, API JSON and the documented demo removal.
It also checks JSON contact responses and repeated requests with a shared CSRF token. Verify
browser feedback, reset, Copy buttons and mobile layout when changing the demo JavaScript.
It uses disposable copies and exercises bootstrap from a different working directory.
There is no PHPUnit suite or analyse script. Lint changed PHP and test added routes such as
`/greet/Ada` too. Keep tests of redirects from
following them automatically, and use session cookies and fresh CSRF tokens for submissions.

When changing setup or examples, also check the public
[installation guide](https://nafphp.github.io/docs/install/),
[first application](https://nafphp.github.io/docs/first-app/) and affected recipes.
The sibling `docs/` checkout, when available, has an executable example runner documented in
its README. Do not claim nonexistent starter tests or unrun checks passed.

Follow the shared [PHP code style](https://github.com/nafphp/docs/blob/main/CODE_STYLE.md):
explicit imports, readable logical groups and escaped template values. The starter ships
the same logo mark and charcoal/teal palette as the documentation. `showQuote` in
`app/config.php` controls the quote panel; the quotes remain in `QuoteService`.
The welcome page explains replacing routes before deleting their demo files. Keep those
instructions and the removal smoke test consistent when changing the starter layout.
`Start fresh` opens the instructions and copies commands; it does not expose a web endpoint
that deletes project files. Remove the unused form partial and JavaScript when cleaning up.
