<?php

namespace OtomaticAi\Controllers;

use Exception;
use OtomaticAi\Api\OtomaticAi\Client;
use OtomaticAi\Api\OtomaticAi\Exceptions\UnauthorizedException;
use OtomaticAi\Api\OtomaticAi\Exceptions\ValidationException;
use OtomaticAi\Utils\Auth;
use OtomaticAi\Utils\Settings;

class AuthController extends Controller
{
    /**
     * Login the user
     *
     * @return void
     */
    public function login()
    {
        $this->verifyNonce();

        $this->validate([
            "email" => ["required", "email"],
            "password" => ["required", "string"],
        ]);

        try {
            Auth::login($this->input("email"), $this->input("password"));
            $this->emptyResponse();
        } catch (ValidationException $e) {
            $this->response(["message" => $e->getMessage(), "errors" => $e->getErrors()], 422);
        } catch (Exception $e) {
            $this->response(["message" => "An error occurred", "error" => $e->getMessage()], 503);
        }
    }

    /**
     * Logout the user
     *
     * @return void
     */
    public function logout()
    {
        $this->verifyNonce();

        try {
            Auth::logout();
            $this->emptyResponse();
        } catch (Exception $e) {
            $this->response(["message" => "An error occurred", "error" => $e->getMessage()], 503);
        }
    }

    /**
     * Get the authenticated domain
     *
     * @return void
     */
    public function domain()
    {
        $this->verifyNonce();

        try {
            $this->response(Auth::domain());
        } catch (UnauthorizedException $e) {
            $this->emptyResponse();
        } catch (Exception $e) {
            $this->response(["message" => "An error occurred", "error" => $e->getMessage()], 503);
        }
    }

    /**
     * Get the required settings statuses
     *
     * @return void
     */
    public function requiredSettings()
    {
        $this->verifyNonce();

        $this->response([
            "openai" => !empty(Settings::get('api.openai.api_key')),
        ]);
    }

    /**
     * Set the domain to premium
     *
     * @return void
     */
    public function enablePremium()
    {
        $this->verifyNonce();

        try {
            $api = new Client;
            $response = $api->enablePremium();
            Auth::refreshDomain();
            $this->response($response);
        } catch (UnauthorizedException $e) {
            $this->emptyResponse();
        } catch (Exception $e) {
            $this->response(["message" => "An error occurred", "error" => $e->getMessage()], 503);
        }
    }

    /**
     * Set the domain to free
     *
     * @return void
     */
    public function disablePremium()
    {
        $this->verifyNonce();

        try {
            $api = new Client;
            $response = $api->disablePremium();
            Auth::refreshDomain();
            $this->response($response);
        } catch (UnauthorizedException $e) {
            $this->emptyResponse();
        } catch (Exception $e) {
            $this->response(["message" => "An error occurred", "error" => $e->getMessage()], 503);
        }
    }
}
