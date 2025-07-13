<?php

namespace OtomaticAi\Api\Unsplash;

use Exception;
use OtomaticAi\Api\Unsplash\Exceptions\ApiException;
use OtomaticAi\Utils\Settings;
use OtomaticAi\Vendors\GuzzleHttp\Exception\ClientException;
use OtomaticAi\Vendors\GuzzleHttp\Client as HttpClient;

class Client
{
    /**
     * The unsplash api endpoint
     *
     * @var string
     */
    private string $endpoint = "https://api.unsplash.com";

    /**
     * The GuzzleHttp client
     *
     * @var HttpClient
     */
    private HttpClient $client;

    /**
     * Create a new Unsplash Api client
     *
     * @param string|null $key
     * @throws Exception
     */
    function __construct(string $key = null)
    {
        // get the key
        if (empty($key)) {
            $key = Settings::get("api.unsplash.api_key");
        }
        if (empty($key)) {
            throw new Exception("No Unsplash Api Key provided.");
        }

        // create the http client
        $this->client = new HttpClient(
            [
                "base_uri" => rtrim($this->endpoint, "/") . '/',
                "headers" => [
                    "Authorization" => "Client-ID " . $key,
                    "Accept-Version" => "v1",
                    "Content-Type" => "application/json",

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
            "page" => 1,
            "per_page" => 10,
            "order_by" => 'relevant',
            "content_filter" => 'low',
            "orientation" => 'landscape',
        ], $settings);

        // call the api endpoint
        $response = $this->request("GET", "search/photos", [
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
