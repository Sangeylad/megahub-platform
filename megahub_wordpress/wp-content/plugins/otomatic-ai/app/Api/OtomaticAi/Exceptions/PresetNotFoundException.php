<?php

namespace OtomaticAi\Api\OtomaticAi\Exceptions;

use Exception;

class PresetNotFoundException extends Exception
{
    public function __construct($role)
    {
        parent::__construct("OtomaticAi Error: Preset `" . $role . "` not found.", 404);
    }
}
