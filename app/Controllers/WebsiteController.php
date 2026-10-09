<?php

declare(strict_types=1);

namespace App\Controllers;

use App\Service\QuoteService;
use Psr\Http\Message\ResponseInterface;

use function Naf\abort;
use function Naf\Form\is_post;
use function Naf\Form\validator;
use function Naf\json;
use function Naf\param;
use function Naf\redirect;
use function Naf\request;
use function Naf\route;
use function Naf\View\render;

class WebsiteController
{
    public function __construct(private readonly QuoteService $quotes)
    {
    }

    public function index(): ResponseInterface
    {
        return render('welcome', [
            'title' => 'Welcome to your new App!',
            'quote' => $this->quotes->getRandomQuote(),
        ]);
    }

    public function api(): ResponseInterface
    {
        $name = param()->get('name', '');
        if (!is_string($name)) {
            return json([
                'error'  => 'Invalid request.',
                'fields' => ['name' => ['Use a text value.']],
            ], 422);
        }

        $check = validator()->validate(['name' => $name], [
            'name' => 'required|max:80',
        ]);

        if (!$check->isValid()) {
            return json(['error' => 'Invalid request.', 'fields' => $check->getErrorMessages()], 422);
        }

        return json(['data' => ['hello' => $name]]);
    }

    public function contact(): ResponseInterface
    {
        $values = [];
        $check  = validator();
        $asJson = request()->getHeaderLine('Accept') === 'application/json';

        if (is_post()) {
            foreach (['firstname', 'lastname', 'message'] as $field) {
                $value = param()->get($field, '');
                if (!is_string($value)) {
                    if ($asJson) {
                        return json([
                            'error'  => 'Invalid request.',
                            'fields' => [$field => ['Use a text value.']],
                        ], 422);
                    }

                    abort(400, 'Form fields must be text.');
                }
                $values[$field] = $value;
            }

            $check->validate($values, [
                'firstname' => 'required|max:80',
                'lastname'  => 'required|max:80',
                'message'   => 'required|min:10',
            ]);

            if ($check->isValid()) {
                // This demo validates only. Add your application service here.
                if ($asJson) {
                    return json(['data' => ['message' => 'Your form passed validation. Nothing was sent or stored.']]);
                }

                return redirect(route('contact'));
            }

            if ($asJson) {
                return json(['error' => 'Invalid request.', 'fields' => $check->getErrorMessages()], 422);
            }
        }

        return render('contact', [
            'title'  => 'Form demo · NAF',
            'check'  => $check,
            'values' => $values,
        ]);
    }
}
