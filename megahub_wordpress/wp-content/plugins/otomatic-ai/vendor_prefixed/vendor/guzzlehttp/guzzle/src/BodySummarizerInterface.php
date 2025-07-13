<?php

namespace OtomaticAi\Vendors\GuzzleHttp;

use OtomaticAi\Vendors\Psr\Http\Message\MessageInterface;
interface BodySummarizerInterface
{
    /**
     * Returns a summarized message body.
     */
    public function summarize(MessageInterface $message) : ?string;
}
