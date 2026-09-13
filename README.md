# NAF App

A clean starting point for building applications with [NAF](https://github.com/nafphp/framework) — the minimal and flexible PHP microframework.

> **"As simple as possible, as flexible as necessary."**

---

## 🚀 Installation

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

---

## 🧰 Requirements

- PHP 8.3+
- Composer
- A webserver (e.g. Apache, nginx, or PHP’s built-in server)

---

## 🗂️ Project Structure

```
/app
  /Controllers
  /Models
  /views
  config.php
  routes.php
/public
  index.php
bootstrap.php
composer.json
```

- `app/` contains your application logic
- `public/` is the webroot
- `bootstrap.php` initializes the app
- `config.php` holds your app configuration
- `routes.php` contains all the routes

---

## 🛠️ First Steps

1. Define your first route in `app/routes.php`:

```php
route()->add('GET', '/', [App\Controllers\HomeController::class, 'index']);
```

2. Create a controller in `app/controllers/HomeController.php`:

```php
namespace App\Controllers;

use function Naf\render;

class HomeController
{
    public function index()
    {
        return render('home', ['name' => 'World']);
    }
}
```

3. Create a view in `app/views/home.phtml`:

```php
<?php use function Naf\s; ?>

<h1>Hello, <?= s($name) ?>!</h1>
```

---

## 📦 About NAF

This app skeleton is based on the [NAF microframework](https://github.com/nafphp/framework).  
It’s designed to give you a clean starting point — nothing more, nothing less.

To learn more about NAF and its philosophy, check out the [main documentation](https://nafphp.github.io/docs/).

---

## 🪪 License

MIT License.
See [LICENSE](LICENSE) for details.

---

Ready to build something awesome?  
Start hacking with **NAF**. 🚀