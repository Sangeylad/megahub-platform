<?php

namespace OtomaticAi\Api\StabilityAi\Exceptions;

class NoSuccessfulGenerationException extends ApiException
{
    public function __construct()
    {
        parent::__construct("StabilityAi Error: No successful generation.");
    }
}
