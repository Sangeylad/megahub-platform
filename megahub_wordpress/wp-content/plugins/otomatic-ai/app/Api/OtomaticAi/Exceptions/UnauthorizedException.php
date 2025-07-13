<?php

namespace OtomaticAi\Api\OtomaticAi\Exceptions;

use Exception;

class UnauthorizedException extends Exception
{
    public function __construct()
    {
        parent::__construct("OtomaticAi Error: Unauthenticated.", 401);
    }
}
