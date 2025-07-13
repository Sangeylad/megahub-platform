<?php

namespace OtomaticAi\Api\BingImage;

use DOMDocument;
use DOMXPath;
use Exception;
use OtomaticAi\Vendors\GuzzleHttp\Client as HttpClient;
use OtomaticAi\Vendors\Illuminate\Support\Arr;

class Client
{
    /**
     * The bing image endpoint
     *
     * @var string
     */
    private string $endpoint = "https://www.bing.com/images/search";

    /**
     * The GuzzleHttp client
     *
     * @var HttpClient
     */
    private HttpClient $client;

    /**
     * Create a new Bing Image client
     *
     * @throws Exception
     */
    function __construct()
    {
        // create the http client
        $this->client = new HttpClient(
            [
                "base_uri" => rtrim($this->endpoint, "/"),
                "headers" => [
                    "User-Agent" => 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
                ]
            ],
        );
    }

    /**
     * Call the images endpoint
     *
     * @param array $settings
     * @return array
     * @throws Exception
     */
    public function images(array $settings = []): array
    {
        // make the payload
        $settings = array_merge([
            'q' => null,
        ], $settings);

        // call the api endpoint
        $response = $this->request("GET", "", [
            "query" => $settings
        ]);

        $doc = new DOMDocument();
        @$doc->loadHTML($response);
        $xpath = new DOMXPath($doc);
        $links = $xpath->query('.//*[contains(concat(" ",normalize-space(@class)," ")," imgpt ")]//a[@m]');

        $images = [];
        if (!is_null($links)) {
            foreach ($links as $element) {
                $value = json_decode($element->getAttribute("m"), true);
                $images[] = Arr::get($value, "murl");
            }
        }

        return $images;
    }

    /**
     * Perform an api request
     *
     * @param string $method
     * @param stirng $uri
     * @param array $options
     * @return string
     * @throws Exception
     */
    private function request(string $method, string $uri, array $options = [])
    {
        $response = $this->client->request($method, $uri, $options);
        $response = $response->getBody()->getContents();

        return $response;
    }
}
