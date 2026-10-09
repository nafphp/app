# NAF App

A clean starting point for building applications with [NAF](https://github.com/nafphp/framework).
Ordinary PHP, a small set of plugins, and room for your own application.

## Documentation

**[Your first application →](https://nafphp.github.io/docs/first-app/)**

Setup, examples and how to replace the starter demo live in the
[NAF documentation](https://nafphp.github.io/docs/). Choose optional packages with
[Which packages do I need?](https://nafphp.github.io/docs/choosing-packages/).

## Install

```bash
composer create-project naf/app my-app
cd my-app
APP_ENV=dev php -S 127.0.0.1:8000 -t public
```

Serve only `public/`. Keep the development server on localhost.

## Explore the demo

The welcome page includes interactive form and JSON examples. They use `fetch()` to show
validation errors, responses and HTTP status without a page reload. The contact example
validates only; it does not send or store messages. The forms retain their normal submissions
when JavaScript is unavailable. The form plugin checks CSRF for both examples.

`Start fresh` opens the cleanup steps with Copy buttons for the terminal commands. Replace
the demo routes first and save any changes you want to keep before running the removal command.
The installed framework and plugins remain your starting point.

## License

MIT. Part of [NAF](https://github.com/nafphp/framework).
