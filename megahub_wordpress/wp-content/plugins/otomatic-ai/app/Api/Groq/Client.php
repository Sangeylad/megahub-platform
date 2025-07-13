<?php

namespace OtomaticAi\Api\Groq;

use Exception;
use OtomaticAi\Api\Groq\Exceptions\ApiException;
use OtomaticAi\Models\Usages\Usage;
use OtomaticAi\Utils\Settings;
use OtomaticAi\Vendors\Illuminate\Support\Arr;
use OtomaticAi\Vendors\GuzzleHttp\Client as HttpClient;
use OtomaticAi\Vendors\GuzzleHttp\Exception\ClientException;

class Client
{
    /**
     * The groq api endpoint
     *
     * @var string
     */
    private string $endpoint = "https://api.groq.com";

    /**
     * The GuzzleHttp client
     *
     * @var HttpClient
     */
    private HttpClient $client;

    /**
     * Create a new Groq Api client
     *
     * @param string|null $key
     * @throws Exception
     */
    public function __construct(string $key = null)
    {
        // get the key
        if (empty($key)) {
            $key = Settings::get("api.groq.api_key");
        }
        if (empty($key)) {
            throw new Exception("No Groq Api Key provided.");
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

        $this->client = new HttpClient($settings);
    }

    /**
     * Call the list models api from groq
     *
     * @return array
     * @throws Exception
     */
    public function listModels(): array
    {
        return $this->request("GET", "openai/v1/models");
    }

    /**
     * Call the chat api from groq
     *
     * @param array $payload
     * @return array
     * @throws Exception
     */
    public function chat(array $payload): array
    {
        // call the chat api
        $complete = $this->request("POST", "openai/v1/chat/completions", [
            "json" => $payload
        ]);

        // store the usage
        $usage = Arr::get($complete, "usage", []);
        if (Arr::get($usage, 'prompt_tokens', 0) + Arr::get($usage, 'completion_tokens', 0) > 0) {
            Usage::create([
                "provider" => "groq_chat",
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
