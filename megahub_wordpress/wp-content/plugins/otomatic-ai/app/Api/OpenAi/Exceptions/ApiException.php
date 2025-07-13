<?php

namespace OtomaticAi\Api\OpenAi\Exceptions;

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
            $message = "OpenAi Error: " . $message;

            switch ($e->getCode()) {
                case 400:
                    return new BadRequestException($message, $e->getCode());
                case 401:
                    return new AuthentificationException($message, $e->getCode());
                case 403:
                    return new PermissionDeniedException($message, $e->getCode());
                case 404:
                    return new NotFoundException($message, $e->getCode());
                case 409:
                    return new ConflictException($message, $e->getCode());
                case 422:
                    return new UnprocessableEntityException($message, $e->getCode());
                case 429:
                    return new BadRequestException($message, $e->getCode());
            }
        }

        return $e;
    }
}
