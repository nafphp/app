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

## License

MIT. Part of [NAF](https://github.com/nafphp/framework).
