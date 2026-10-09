<?php

declare(strict_types=1);

use App\Controllers\WebsiteController;

use function Naf\route;

route()->add('GET', '/', [WebsiteController::class, 'index'], 'home');
route()->add('POST', '/api', [WebsiteController::class, 'api'], 'api');

route()->add('GET', '/contact', [WebsiteController::class, 'contact'], 'contact');
route()->add('POST', '/contact', [WebsiteController::class, 'contact'], 'contact.submit');
