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

class Client
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
     * Get the user account
     *
     * @return array
     * @throws Exception
     */
    public function account(): array
    {
        return $this->request('GET', 'v1/user/account', [
            "headers" => [
                "Authorization" => $this->key,
            ]
        ]);
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
        // make the payload
        $payload = array_merge([
            "samples" => 1,
            "steps" => 30,
            "width" => 1344,
            "height" => 768,
            "cfg_scale" => 7,
            "text_prompts" => []
        ], $settings);

        // fix the prompt limit
        Arr::set($payload, "text_prompts.0.text", Str::limit(Arr::get($payload, "text_prompts.0.text"), 1900, ''));

        // call the api endpoint
        $response = $this->request("POST", "v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image", [
            "headers" => [
                "Authorization" => $this->key,
            ],
            "json" => $payload
        ]);

        // count successful generations
        $successfulGenerations = count(array_filter(Arr::get($response, "artifacts", []), function ($item) {
            return $item["finishReason"] === "SUCCESS";
        }));

        // throw exception if no successful images was return
        if ($successfulGenerations === 0) {
            throw new NoSuccessfulGenerationException();
        }

        // store the usage
        Usage::create([
            "provider" => "stability_ai",
            "payload" => [
                "engine" => "stable-diffusion-xl-1024-v1-0",
                "steps" => $payload["steps"],
                "artifacts" => $successfulGenerations,
            ]
        ]);

        return $response;
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
        // make the payload
        $settings = array_merge([
            "aspect_ratio" => "16:9",
            "model" => "core",
        ], $settings);

        switch ($settings["model"]) {
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

        // call the api endpoint
        $response = $this->request("POST", $endpoint, [
            "headers" => [
                "Authorization" => "Bearer " . $this->key,
                "Accept" => "application/json",
            ],
            "multipart" => array_map(function ($value, $key) {
                return [
                    "name" => $key,
                    "contents" => $value,
                ];
            }, array_values($settings), array_keys($settings))
        ]);

        // throw exception if no successful images was return
        if (Arr::get($response, "finish_reason") !== "SUCCESS") {
            throw new NoSuccessfulGenerationException();
        }

        // store the usage
        Usage::create([
            "provider" => "stability_ai",
            "payload" => [
                "engine" => $engine,
                "steps" => 0,
                "artifacts" => 1,
            ]
        ]);

        return $response;
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
