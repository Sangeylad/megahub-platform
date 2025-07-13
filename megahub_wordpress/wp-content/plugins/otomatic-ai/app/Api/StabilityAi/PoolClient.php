<?php

namespace OtomaticAi\Api\StabilityAi;

use Exception;
use OtomaticAi\Api\StabilityAi\Exceptions\ApiException;
use OtomaticAi\Api\StabilityAi\Exceptions\NoSuccessfulGenerationException;
use OtomaticAi\Vendors\GuzzleHttp\Exception\ClientException;
use OtomaticAi\Models\Usages\Usage;
use OtomaticAi\Utils\Settings;
use OtomaticAi\Vendors\GuzzleHttp\Client as HttpClient;
use OtomaticAi\Vendors\Illuminate\Support\Arr;
use OtomaticAi\Vendors\Illuminate\Support\Str;
use OtomaticAi\Vendors\GuzzleHttp\Pool;
use OtomaticAi\Vendors\GuzzleHttp\Psr7\MultipartStream;
use OtomaticAi\Vendors\GuzzleHttp\Psr7\Request;
use OtomaticAi\Vendors\GuzzleHttp\Psr7\Response;

class PoolClient
{
    /**
     * The stability ai api endpoint
     *
     * @var string
     */
    private string $endpoint = "https://api.stability.ai";

    /**
     * The GuzzleHttp client
     *
     * @var HttpClient
     */
    private HttpClient $client;

    /**
     * The auth key
     *
     * @var HttpClient
     */
    private string $key;

    /**
     * Create a new StabilityAi Api client
     *
     * @param string|null $key
     * @throws Exception
     */
    function __construct(string $key = null)
    {
        // get the key
        if (empty($key)) {
            $key = Settings::get("api.stability_ai.api_key");
        }
        if (empty($key)) {
            throw new Exception("No StabilityAI Api Key provided.");
        }

        $this->key = $key;

        // create the http client
        $this->client = new HttpClient(
            [
                "base_uri" => rtrim($this->endpoint, "/") . '/',
                "headers" => [
                    "Content-Type" => "application/json",
                ],
                "timeout" => 600
            ]
        );
    }

    /**
     * Call the text to image api endpoint
     *
     * @param array $settings
     * @return array
     * @throws Exception
     */
    public function textToImage(array $settings = []): array
    {
        $requests = [];
        foreach ($settings as $payload) {

            // make the payload
            $payload = array_merge([
                "samples" => 1,
                "steps" => 30,
                "width" => 1344,
                "height" => 768,
                "cfg_scale" => 7,
                "text_prompts" => []
            ], $payload);

            // fix the prompt limit
            Arr::set($payload, "text_prompts.0.text", Str::limit(Arr::get($payload, "text_prompts.0.text"), 1900, ''));

            // make the request
            $requests[] = [
                "request" => new Request(
                    'POST',
                    "v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image",
                    [
                        "Authorization" => "Bearer " . $this->key,
                        "Accept" => "application/json",
                    ],
                    json_encode($payload)
                ),
                "after" => function ($item) use ($payload) {
                    if (Arr::get($item, "artifacts.0.finishReason") === "SUCCESS") {
                        // store the usage
                        Usage::create([
                            "provider" => "stability_ai",
                            "payload" => [
                                "engine" => "stable-diffusion-xl-1024-v1-0",
                                "steps" => $payload["steps"],
                                "artifacts" => 1,
                            ]
                        ]);
                    }
                }
            ];
        }

        // call the stability ai api
        $completes = $this->run($requests);

        return $completes;
    }

    /**
     * Call the stable image generate api endpoint
     *
     * @param array $settings
     * @return array
     * @throws Exception
     */
    public function stableImageGenerate(array $settings = []): array
    {
        $requests = [];
        foreach ($settings as $payload) {

            // make the payload
            $payload = array_merge([
                "aspect_ratio" => "16:9",
                "model" => "core"
            ], $payload);

            switch ($payload["model"]) {
                case "sd3":
                    $endpoint = "v2beta/stable-image/generate/sd3";
                    $engine = "stable_image_sd3";
                    break;
                case "sd3-turbo":
                    $endpoint = "v2beta/stable-image/generate/sd3";
                    $engine = "stable_image_sd3_turbo";
                    break;
                default:
                    $endpoint = "v2beta/stable-image/generate/core";
                    $engine = "stable_image_core";
            }

            $multipart = new MultipartStream(array_map(function ($value, $key) {
                return [
                    "name" => $key,
                    "contents" => $value,
                ];
            }, array_values($payload), array_keys($payload)));

            // make the request
            $requests[] = [
                "request" => new Request(
                    'POST',
                    $endpoint,
                    [
                        "Authorization" => "Bearer " . $this->key,
                        "Accept" => "application/json",
                    ],
                    $multipart
                ),
                "after" => function ($complete) use ($payload, $engine) {

                    // store the usage
                    Usage::create([
                        "provider" => "stability_ai",
                        "payload" => [
                            "engine" => $engine,
                            "steps" => 0,
                            "artifacts" => 1,
                        ]
                    ]);
                }
            ];
        }

        // call the stability ai api
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
