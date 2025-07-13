<?php

namespace OtomaticAi\Api\Pixabay;

use Exception;
use OtomaticAi\Utils\Settings;
use OtomaticAi\Vendors\GuzzleHttp\Client as HttpClient;

class Client
{
    /**
     * The pixabay api endpoint
     *
     * @var string
     */
    private string $endpoint = "https://pixabay.com/api";

    /**
     * The GuzzleHttp client
     *
     * @var HttpClient
     */
    private HttpClient $client;

    /**
     * The api key
     *
     * @var string
     */
    private string $key;

    /**
     * Create a new Pixabay Api client
     *
     * @param string|null $key
     * @throws Exception
     */
    function __construct(string $key = null)
    {
        // get the key
        if (empty($key)) {
            $key = Settings::get("api.pixabay.api_key");
        }
        if (empty($key)) {
            throw new Exception("No Pixabay Api Key provided.");
        }
        $this->key = $key;

        // create the http client
        $this->client = new HttpClient(
            [
                "base_uri" => rtrim($this->endpoint, "/") . '/',
            ]
        );
    }

    /**
     * Call the images api endpoint
     *
     * @param array $settings
     * @return array
     * @throws Exception
     */
    public function images(array $settings = []): array
    {

        // make the payload
        $settings = array_merge([
            'key' => $this->key,
            'q' => null,
            'safesearch' => true,
            'lang' => "en",
            'image_type' => 'illustration,photo',
        ], $settings);

        // call the api endpoint
        $response = $this->request("GET", "", [
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
