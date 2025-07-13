<?php

namespace OtomaticAi\Api\Groq;

use Exception;
use OtomaticAi\Api\Groq\Exceptions\ApiException;
use OtomaticAi\Models\Usages\Usage;
use OtomaticAi\Utils\Settings;
use OtomaticAi\Vendors\Illuminate\Support\Arr;
use OtomaticAi\Vendors\GuzzleHttp\Client as HttpClient;
use OtomaticAi\Vendors\GuzzleHttp\Pool;
use OtomaticAi\Vendors\GuzzleHttp\Psr7\Request;
use OtomaticAi\Vendors\GuzzleHttp\Psr7\Response;

class PoolClient
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
     * Call the chat api from groq
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
                    "openai/v1/chat/completions",
                    [],
                    json_encode($payload)
                ),
                "after" => function ($complete) {

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
                }
            ];
        }

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
