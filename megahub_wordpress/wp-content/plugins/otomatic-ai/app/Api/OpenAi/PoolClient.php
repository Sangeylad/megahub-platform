<?php

namespace OtomaticAi\Api\OpenAi;

use Exception;
use OtomaticAi\Api\OpenAi\Exceptions\ApiException;
use OtomaticAi\Models\Usages\Usage;
use OtomaticAi\Utils\Settings;
use OtomaticAi\Vendors\Illuminate\Support\Arr;
use OtomaticAi\Vendors\Illuminate\Support\Str;
use OtomaticAi\Vendors\GuzzleHttp\Client as HttpClient;
use OtomaticAi\Vendors\GuzzleHttp\Pool;
use OtomaticAi\Vendors\GuzzleHttp\Psr7\Request;
use OtomaticAi\Vendors\GuzzleHttp\Psr7\Response;

class PoolClient
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
     * Call the chat api from openai
     *
     * @param array $payloads
     * @return array
     * @throws Exception
     */
    public function chat(array $payloads): array
    {
        // call the chat api
        $requests = [];
        foreach ($payloads as $payload) {
            $requests[] = [
                "request" => new Request(
                    'POST',
                    "chat/completions",
                    [],
                    json_encode($payload)
                ),
                "after" => function ($complete) {

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
                }
            ];
        }

        $completes = $this->run($requests);

        return $completes;
    }

    /**
     * Call the dall-e api from openai
     *
     * @param array $prompts
     * @param array $settings
     * @return array
     * @throws Exception
     */
    public function image(array $prompts, array $settings = [])
    {
        if (count($prompts) !== count($settings)) {
            throw new Exception("`prompts` and `settings` parameters do not have the same number of items.");
        }

        $requests = [];
        foreach ($prompts as $index => $prompt) {
            // make the payload
            $payload = array_merge([
                "model" => "dall-e-2",
                "n" => 1,
                "size" => "1024x1024",
                "response_format" => "b64_json",
                "quality" => "standard",
            ], $settings[$index]);
            $payload["prompt"] = $prompt;

            // force standard quality on dall-e-2 model
            if (Str::lower($payload["model"]) === "dall-e-2") {
                $payload["quality"] = "standard";
            }

            // make the request
            $requests[] = [
                "request" => new Request(
                    'POST',
                    "images/generations",
                    [],
                    json_encode($payload)
                ),
                "after" => function ($complete) use ($payload) {

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
                }
            ];
        }

        // call the dall-e api
        $completes = $this->run($requests);

        return $completes;
    }

    /**
     * Perform an api request
     *
     * @param array $requests
     * @param stirng $uri
     * @param array $options
     * @return array
     * @throws Exception
     */
    private function run(array $requests)
    {
        $output = [];

        // get the http requests
        $httpRequests = Arr::pluck($requests, "request");

        // create the pool
        $pool = new Pool($this->client, $httpRequests, [
            'concurrency' => 10,
            'fulfilled' => function (Response $response, $index) use (&$output, $requests) {
                $response = $response->getBody()->getContents();
                $response = json_decode($response, true);
                $output[$index] = $response;

                // call after callback
                if (!empty($requests[$index]["after"]) && is_callable($requests[$index]["after"])) {
                    $requests[$index]["after"]($response);
                }
            },
            'rejected' => function (Exception $reason, $index) {
                $e = ApiException::make($reason);
                throw $e;
            },
        ]);

        // call the pool
        $promise = $pool->promise();
        $promise->wait();

        return $output;
    }
}
