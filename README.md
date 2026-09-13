# NAF App

A clean starting point for building applications with [NAF](https://github.com/nafphp/framework) — the minimal and flexible PHP microframework.

> **"As simple as possible, as flexible as necessary."**

---

```bash
composer create-project naf/app my-app
```

Alternatively, clone the repo manually:

```bash
git clone https://github.com/nafphp/app my-app
cd my-app
composer install
```

Make sure your webserver points to the `/public` directory as document root.

## Documentation

**[Your first application →](https://nafphp.github.io/docs/first-app/)**

Everything about this package — what it does, how it is configured and what it needs — lives
in the [NAF documentation](https://nafphp.github.io/docs/). Not sure which packages you need?
[Start here](https://nafphp.github.io/docs/choosing-packages/).

## Working on the starter

Read [AGENTS.md](AGENTS.md) for the starter layout, current dependency compatibility steps,
extension examples and HTTP verification. Create a new project with the command above;
`naf/app` is an application skeleton, not a library to require inside another application.

## License

MIT. Part of [NAF](https://github.com/nafphp/framework).
