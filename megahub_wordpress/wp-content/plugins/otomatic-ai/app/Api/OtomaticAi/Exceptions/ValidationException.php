<?php

namespace OtomaticAi\Api\OtomaticAi\Exceptions;

use Exception;

class ValidationException extends Exception
{
    /**
     * The validation exception errors
     *
     * @var array
     */
    private array $errors = [];

    public function __construct($message, $errors = [])
    {
        parent::__construct($message, 422);

        $this->errors = $errors;
    }

    /**
     * Return the validation exception errors
     *
     * @return array
     */
    public function getErrors(): array
    {
        return $this->errors;
    }
}
