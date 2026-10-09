<?php

declare(strict_types=1);

use function Naf\app;

const BASE_PATH = __DIR__;

require_once __DIR__ . '/vendor/autoload.php';

// Register application services here, before run() handles the request.
app()->run();
