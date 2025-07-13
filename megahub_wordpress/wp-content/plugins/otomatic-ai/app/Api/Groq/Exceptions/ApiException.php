<?php

namespace OtomaticAi\Api\Groq\Exceptions;

use Exception;
use OtomaticAi\Vendors\Illuminate\Support\Arr;
use OtomaticAi\Vendors\GuzzleHttp\Exception\ClientException;

abstract class ApiException extends Exception
{
    /**
     * Create the correct ApiException based on Error Code
     *
     * @param Exception $e
     * @return Exception
     */
    static public function make(Exception $e)
    {
        if (get_class($e) === ClientException::class) {
            $response = $e->getResponse()->getBody()->getContents();
            $response = json_decode($response, true);
            $message = Arr::get($response, "error.message", $e->getMessage());
            $message = "Mistral Ai Error: " . $message;

            switch ($e->getCode()) {
                case 401:
                    return new AuthentificationException($message, $e->getCode());
            }
        }

        return $e;
    }
}
