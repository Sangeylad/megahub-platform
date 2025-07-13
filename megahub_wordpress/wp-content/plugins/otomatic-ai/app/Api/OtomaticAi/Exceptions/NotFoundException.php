<?php

namespace OtomaticAi\Api\OtomaticAi\Exceptions;

use Exception;

class NotFoundException extends Exception
{
    public function __construct()
    {
        parent::__construct("OtomaticAi Error: Not Found.", 404);
    }
}
