<?php

namespace OtomaticAi\Api\Haloscan\Exceptions;

use Exception;
use OtomaticAi\Vendors\Illuminate\Support\Arr;
use OtomaticAi\Vendors\GuzzleHttp\Exception\ClientException;

abstract class ApiException extends Exception
{
    /**
     * Create the correct ApiException based on Error Code
     *
     * @param ClientException $e
     * @return ApiException|ClientException
     */
    static public function make(ClientException $e)
    {
        $response = $e->getResponse()->getBody()->getContents();
        $response = json_decode($response, true);
        $message = Arr::get($response, "message", $e->getMessage());
        $message = "Haloscan Error: " . $message;

        switch ($e->getCode()) {
            case 403:
                return new PermissionDeniedException($message, $e->getCode());
        }

        return $e;
    }
}
