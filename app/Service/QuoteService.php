<?php

declare(strict_types=1);

namespace App\Service;

class QuoteService
{
    /** @var list<array{0: string, 1: string}> */
    protected array $quotes = [
        ['Will Rogers', 'Don’t let yesterday take up too much of today.'],
        ['Audrey Hepburn', 'Nothing is impossible. The word itself says "I\'m possible!"'],
        ['Wayne Dyer', 'If you change the way you look at things, the things you look at change.'],
        ['Malala Yousafzai', 'Let us make our future now, and let us make our dreams tomorrow’s reality.'],
        ['Leonard I. Sweet', 'The future is not something we enter. The future is something we create.'],
        ['Nikki Giovanni', 'Mistakes are a fact of life. It is the response to the error that counts.'],
        ['Gloria Steinem', 'Dreaming, after all, is a form of planning.'],
        ['Margaret Fuller', 'If you have knowledge, let others light their candles in it.'],
        ['Albert Einstein', 'A person who never made a mistake never tried anything new.'],
        ['Drew Houston', 'Don’t worry about failure, you only have to be right once.'],
        ['Theodore Roosevelt', 'Believe you can and you\'re halfway there.'],
        ['Nelson Mandela', 'It always seems impossible until it\'s done.'],
        ['Amanda Gorman', 'There is no better compass than compassion.'],
        ['Suzy Kassem', 'Doubt kills more dreams than failure ever will.'],
        ['Walt Disney', 'The best way to get started is to quit talking and begin doing.'],
    ];

    /** @return array{0: string, 1: string} */
    public function getRandomQuote(): array
    {
        return $this->quotes[array_rand($this->quotes)];
    }
}
