<?php

namespace App\Jobs;

use Naf\Cli\Core\Output;
use Naf\Queue\Core\QueueJobInterface;
use function Naf\log;

class SendMailJob implements QueueJobInterface
{
    private string $email;

    public function __construct(array $payload)
    {
        $this->email = $payload['email'];
    }

    public function handle(Output $output): void
    {
        log()->info('Send Mail Job');
        $output->writeLine('Sending mail to ' . $this->email);
    }

}