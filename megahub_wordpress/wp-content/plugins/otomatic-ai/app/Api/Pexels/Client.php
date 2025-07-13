<?php

namespace OtomaticAi\Api\Pexels;

use Exception;
use OtomaticAi\Utils\Settings;
use OtomaticAi\Vendors\GuzzleHttp\Client as HttpClient;

class Client
{
    /**
     * The pexels api endpoint
     *
     * @var string
     */
    private string $endpoint = "https://api.pexels.com/v1";

    /**
     * The GuzzleHttp client
     *
     * @var HttpClient
     */
    private HttpClient $client;

    /**
     * Create a new Pexels Api client
     *
     * @param string|null $key
     * @throws Exception
     */
    function __construct(string $key = null)
    {
        // get the key
        if (empty($key)) {
            $key = Settings::get("api.pexels.api_key");
        }
        if (empty($key)) {
            throw new Exception("No Pexels Api Key provided.");
        }

        // create the http client
        $this->client = new HttpClient(
            [
                "base_uri" => rtrim($this->endpoint, "/") . '/',
                "headers" => [
                    "Authorization" => $key,
                ]
            ]
        );
    }

    /**
     * Call the search photos api endpoint
     *
     * @param array $settings
     * @return array
     * @throws Exception
     */
    public function searchPhotos(array $settings = []): array
    {
        // make the payload
        $settings = array_merge([
            "query" => null,
            "orientation" => 'landscape',
            "page" => 1,
            "per_page" => 10,
        ], $settings);

        // call the api endpoint
        $response = $this->request("GET", "search", [
            "query" => $settings
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

        $response = $this->client->request($method, $uri, $options);
        $response = $response->getBody()->getContents();
        $response = json_decode($response, true);

        return $response;
    }
}
