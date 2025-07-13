<?php

namespace OtomaticAi\Api\OpenAi;

use Exception;
use OtomaticAi\Api\OpenAi\Exceptions\ApiException;
use OtomaticAi\Models\Usages\Usage;
use OtomaticAi\Utils\Settings;
use OtomaticAi\Vendors\Illuminate\Support\Arr;
use OtomaticAi\Vendors\Illuminate\Support\Str;
use OtomaticAi\Vendors\GuzzleHttp\Client as HttpClient;
use OtomaticAi\Vendors\GuzzleHttp\Exception\ClientException;

class Client
{
    /**
     * The openai api endpoint
     *
     * @var string
     */
    private string $endpoint = "https://api.openai.com/v1";

    /**
     * The GuzzleHttp client
     *
     * @var HttpClient
     */
    private HttpClient $client;

    /**
     * Create a new OpenAi Api client
     *
     * @param string|null $key
     * @param string|null $organization
     * @throws Exception
     */
    public function __construct(string $key = null, string $organization = null)
    {
        // get the key
        if (empty($key)) {
            $key = Settings::get("api.openai.api_key");
        }
        if (empty($key)) {
            throw new Exception("No OpenAI Api Key provided.");
        }

        // get the organizaion
        if (empty($organization)) {
            $organization = Settings::get("api.openai.organization");
        }

        // create the http client
        $settings = [
            "base_uri" => rtrim($this->endpoint, "/") . '/',
            "headers" => [
                "Authorization" => "Bearer " . $key,
                "Content-Type" => "application/json",
            ],
            "timeout" => 600
        ];

        if (!empty($organization)) {
            $settings["headers"]["OpenAI-Organization"] = $organization;
        }

        $this->client = new HttpClient($settings);
    }

    /**
     * Call the list models api from openai
     *
     * @return array
     * @throws Exception
     */
    public function listModels(): array
    {
        return $this->request("GET", "models");
    }

    /**
     * Call the chat api from openai
     *
     * @param array $payload
     * @return array
     * @throws Exception
     */
    public function chat(array $payload): array
    {
        // call the chat api
        $complete = $this->request("POST", "chat/completions", [
            "json" => $payload
        ]);

        // store the usage
        $usage = Arr::get($complete, "usage", []);
        if (Arr::get($usage, 'prompt_tokens', 0) + Arr::get($usage, 'completion_tokens', 0) > 0) {
            Usage::create([
                "provider" => "openai_chat",
                "payload" => [
                    "model" => Arr::get($complete, 'model'),
                    "prompt_tokens" => Arr::get($usage, 'prompt_tokens', 0),
                    "completion_tokens" => Arr::get($usage, 'completion_tokens', 0),
                ]
            ]);
        }

        return $complete;
    }

    /**
     * Call the dall-e api from openai
     *
     * @param string $prompt
     * @param array $settings
     * @return array
     * @throws Exception
     */
    public function image(string $prompt, array $settings = [])
    {
        // make the payload
        $payload = array_merge([
            "model" => "dall-e-2",
            "n" => 1,
            "size" => "1024x1024",
            "response_format" => "b64_json",
            "quality" => "standard",
        ], $settings);
        $payload["prompt"] = $prompt;

        // force standard quality on dall-e-2 model
        if (Str::lower($payload["model"]) === "dall-e-2") {
            $payload["quality"] = "standard";
        }

        // call the dall-e api
        $complete = $this->request("POST", "images/generations", [
            "json" => $payload
        ]);

        // store the usage
        Usage::create([
            "provider" => "openai_image",
            "payload" => [
                "model" => Str::lower($payload["model"]),
                "size" => Str::lower($payload["size"]),
                "n" => $payload["n"],
                "quality" => Str::lower($payload["quality"], "standard"),
            ]
        ]);

        return $complete;
    }

    /**
     * Perform an api request
     *
     * @param string $method
     * @param stirng $uri
     * @param array $options
     * @return array
     * @throws Exception
     */
    private function request(string $method, string $uri, array $options = [])
    {
        try {
            $response = $this->client->request($method, $uri, $options);
            $response = $response->getBody()->getContents();
            $response = json_decode($response, true);

            return $response;
        } catch (ClientException $e) {
            $e = ApiException::make($e);

            throw $e;
        }
    }
}
