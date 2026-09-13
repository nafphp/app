<?php

require_once 'vendor/autoload.php';

use App\Service\QuoteService;
use function Naf\app;

const BASE_PATH = __DIR__;

app()->container()->set('quote', function() {
    return new QuoteService();
});

app()->run();