<?php

namespace App\Controllers;

use App\Service\QuoteService;
use Psr\Http\Message\ResponseInterface;
use function Naf\Form\is_post;
use function Naf\Form\validator;
use function Naf\app;
use function Naf\View\render;
use function Naf\json;
use function Naf\param;
use function Naf\redirect;
use function Naf\route;

class WebsiteController
{

    public function index(): ResponseInterface
    {
        /** @var QuoteService $quote */
        $quote = app()->container()->get('quote');
        return render('welcome', ['quote' => $quote->getRandomQuote()]);
    }

    public function api(): ResponseInterface
    {
        $check = validator()->validate(param()->all(), [
            'name' => 'required|max:80',
        ]);

        if (!$check->isValid()) {
            return json(['error' => 'Invalid request.', 'fields' => $check->getErrorMessages()], 422);
        }

        return json(['data' => ['hello' => param()->get('name')]]);
    }

    public function contact(): ResponseInterface
    {
        if (!is_post()) {
            return render('contact', ['check' => validator()]);
        }

        $check = validator()->validate(param()->all(), [
            'firstname' => 'required|max:80',
            'lastname'  => 'required|max:80',
            'message'   => 'required|min:10',
        ]);

        if (!$check->isValid()) {
            // Back to the form; memory() still finds what was typed.
            return render('contact', ['check' => $check]);
        }

        // Do something with it here - send a mail, store it, queue it.

        return redirect(route('contact'));
    }

}