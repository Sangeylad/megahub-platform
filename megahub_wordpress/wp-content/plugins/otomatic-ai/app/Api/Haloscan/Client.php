<?php

namespace OtomaticAi\Api\Haloscan;

use Exception;
use OtomaticAi\Api\Haloscan\Exceptions\ApiException;
use OtomaticAi\Utils\Settings;
use OtomaticAi\Vendors\GuzzleHttp\Client as HttpClient;
use OtomaticAi\Vendors\GuzzleHttp\Exception\ClientException;

class Client
{
    /**
     * The haloscan api endpoint
     *
     * @var string
     */
    private string $endpoint = "https://api.haloscan.com/api";

    /**
     * The GuzzleHttp client
     *
     * @var HttpClient
     */
    private HttpClient $client;

    /**
     * Create a new Haloscan Api client
     *
     * @param string|null $key
     * @throws Exception
     */
    function __construct(string $key = null)
    {
        // get the key
        if (empty($key)) {
            $key = Settings::get("api.haloscan.api_key");
        }
        if (empty($key)) {
            throw new Exception("No Haloscan Api Key provided.");
        }

        // create the http client
        $this->client = new HttpClient(
            [
                "base_uri" => rtrim($this->endpoint, "/") . '/',
                "headers" => [
                    "Accept" => "application/json",
                    "Content-Type" => "application/json",
                    "Haloscan-Api-Key" => $key,
                ]
            ]
        );
    }

    /**
     * Call the keywords bulk api endpoint
     *
     * @param array $settings
     * @return array
     * @throws Exception
     */
    public function keywordsBulk(array $settings = []): array
    {
        // call the api endpoint
        $response = $this->request("POST", "keywords/bulk", [
            "json" => $settings
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
