<?php

namespace OtomaticAi\Controllers\Settings;

use Exception;
use OtomaticAi\Api\OpenAi\Client as OpenAiClient;
use OtomaticAi\Api\OpenAi\Exceptions\AuthentificationException as OpenAiAuthentificationException;
use OtomaticAi\Api\MistralAi\Client as MistralAiClient;
use OtomaticAi\Api\Groq\Client as GroqClient;
use OtomaticAi\Api\MistralAi\Exceptions\AuthentificationException as MistralAiAuthentificationException;
use OtomaticAi\Api\Groq\Exceptions\AuthentificationException as GroqAuthentificationException;
use OtomaticAi\Api\StabilityAi\Client as StabilityAiClient;
use OtomaticAi\Api\StabilityAi\Exceptions\AuthentificationException as StabilityAiAuthentificationException;
use OtomaticAi\Controllers\Controller;
use OtomaticAi\Utils\Settings;

class ApiController extends Controller
{
    /**
     * Get the api settings
     *
     * @return void
     */
    public function index()
    {
        $this->verifyNonce();

        $this->response(Settings::get('api'));
    }

    /**
     * Set the openai settings.
     * 
     * @return void
     */
    public function setOpenAI()
    {
        $this->verifyNonce();

        $this->validate([
            "api_key" => ["required", "string"],
            "organization" => ["nullable", "string"],
        ]);

        // validate openai api key
        if (!empty($this->input("api_key"))) {
            try {
                $api = new OpenAiClient($this->input("api_key"), $this->input("organization"));
                $models = $api->listModels();
            } catch (OpenAiAuthentificationException $e) {
                $this->response(["message" => $e->getMessage(), "errors" => ['api_key' => [$e->getMessage()]]], 422);
            } catch (Exception $e) {
                $this->response(["message" => "An error occurred", "error" => $e->getMessage()], 503);
            }
        }

        Settings::update($this->request, 'api.openai');
        Settings::save();

        $this->emptyResponse();
    }

    /**
     * Update the openai settings.
     * 
     * @return void
     */
    public function updateOpenAI()
    {
        $this->verifyNonce();

        $this->validate([
            "api_key" => ["nullable", "string"],
            "organization" => ["nullable", "string"],
        ]);

        // validate openai api key
        if (!empty($this->input("api_key"))) {
            try {
                $api = new OpenAiClient($this->input("api_key"), $this->input("organization"));
                $models = $api->listModels();
            } catch (OpenAiAuthentificationException $e) {
                $this->response(["message" => $e->getMessage(), "errors" => ['api_key' => [$e->getMessage()]]], 422);
            } catch (Exception $e) {
                $this->response(["message" => "An error occurred", "error" => $e->getMessage()], 503);
            }
        }

        Settings::update($this->request, 'api.openai');
        Settings::save();

        $this->emptyResponse();
    }

    /**
     * Update the mistral ai settings.
     * 
     * @return void
     */
    public function updateMistralAi()
    {
        $this->verifyNonce();

        $this->validate([
            "api_key" => ["nullable", "string"],
        ]);

        // validate mistral ai api key
        if (!empty($this->input("api_key"))) {
            try {
                $api = new MistralAiClient($this->input("api_key"));
                $models = $api->listModels();
            } catch (MistralAiAuthentificationException $e) {
                $this->response(["message" => "Incorrect API key provided", "errors" => ['api_key' => ["Incorrect API key provided"]]], 422);
            } catch (Exception $e) {
                $this->response(["message" => "An error occurred", "error" => $e->getMessage()], 503);
            }
        }

        Settings::update($this->request, 'api.mistral_ai');
        Settings::save();

        $this->emptyResponse();
    }

    /**
     * Update the groq settings.
     * 
     * @return void
     */
    public function updateGroq()
    {
        $this->verifyNonce();

        $this->validate([
            "api_key" => ["nullable", "string"],
        ]);

        // validate groq api key
        if (!empty($this->input("api_key"))) {
            try {
                $api = new GroqClient($this->input("api_key"));
                $models = $api->listModels();
            } catch (GroqAuthentificationException $e) {
                $this->response(["message" => "Incorrect API key provided", "errors" => ['api_key' => ["Incorrect API key provided"]]], 422);
            } catch (Exception $e) {
                $this->response(["message" => "An error occurred", "error" => $e->getMessage()], 503);
            }
        }

        Settings::update($this->request, 'api.groq');
        Settings::save();

        $this->emptyResponse();
    }

    /**
     * Update the stability ai settings.
     * 
     * @return void
     */
    public function updateStabilityAI()
    {
        $this->verifyNonce();

        $this->validate([
            "api_key" => ["nullable", "string"],
        ]);

        // validate stability ai api key
        if (!empty($this->input("api_key"))) {

            try {
                $api = new StabilityAiClient($this->input("api_key"));
                $api->account();
            } catch (StabilityAiAuthentificationException $e) {
                $this->response(["message" => $e->getMessage(), "errors" => ['api_key' => [$e->getMessage()]]], 422);
            } catch (Exception $e) {
                $this->response(["message" => "An error occurred", "error" => $e->getMessage()], 503);
            }
        }

        Settings::update($this->request, 'api.stability_ai');
        Settings::save();

        $this->emptyResponse();
    }

    /**
     * Update the unsplash settings.
     * 
     * @return void
     */
    public function updateUnsplash()
    {
        $this->verifyNonce();

        $this->validate([
            "api_key" => ["nullable", "string"],
        ]);

        Settings::update($this->request, 'api.unsplash');
        Settings::save();

        $this->emptyResponse();
    }

    /**
     * Update the pexels settings.
     * 
     * @return void
     */
    public function updatePexels()
    {
        $this->verifyNonce();

        $this->validate([
            "api_key" => ["nullable", "string"],
        ]);

        Settings::update($this->request, 'api.pexels');
        Settings::save();

        $this->emptyResponse();
    }

    /**
     * Update the pixabay settings.
     * 
     * @return void
     */
    public function updatePixabay()
    {
        $this->verifyNonce();

        $this->validate([
            "api_key" => ["nullable", "string"],
        ]);

        Settings::update($this->request, 'api.pixabay');
        Settings::save();

        $this->emptyResponse();
    }

    /**
     * Update the haloscan settings.
     * 
     * @return void
     */
    public function updateHaloscan()
    {
        $this->verifyNonce();

        $this->validate([
            "api_key" => ["nullable", "string"],
        ]);

        Settings::update($this->request, 'api.haloscan');
        Settings::save();

        $this->emptyResponse();
    }
}
