<?php

namespace App\Controllers;

use App\Service\QuoteService;
use Naf\Form\Core\Validator;
use Psr\Http\Message\RequestInterface;
use Psr\Http\Message\ResponseInterface;
use function Naf\app;
use function Naf\View\render;
use function Naf\request;

class WebsiteController
{

    public function index(): ResponseInterface
    {
        /** @var QuoteService $quote */
        $quote = app()->container()->get('quote');
        return render('welcome', ['quote' => $quote->getRandomQuote()]);
    }

    public function contact(): ResponseInterface
    {
        /** @var RequestInterface $request */
        $request = app()->container()->get('request');

        if (request()->getMethod() === 'POST') {

            $validator = new Validator($request->getParsedBody(), [
                'email' => 'required|email',
                'password' => 'required|min:8',
            ]);

            if ($validator->fails()) {
                return render('contact', ['validator' => $validator]);
            }

        }

        return render('contact');
    }

}