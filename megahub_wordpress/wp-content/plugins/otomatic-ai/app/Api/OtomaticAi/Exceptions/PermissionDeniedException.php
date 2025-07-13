<?php

namespace OtomaticAi\Api\OtomaticAi\Exceptions;

use Exception;

class PermissionDeniedException extends Exception
{
    public function __construct()
    {
        parent::__construct("OtomaticAi Error: Permission Denied.", 403);
    }
}
