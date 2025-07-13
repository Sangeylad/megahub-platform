<?php

namespace OtomaticAi\Api\GoogleImage;

use Exception;
use OtomaticAi\Vendors\GuzzleHttp\Client as HttpClient;

class Client
{
    /**
     * The google image endpoint
     *
     * @var string
     */
    private string $endpoint = "https://www.google.com/search";

    /**
     * The GuzzleHttp client
     *
     * @var HttpClient
     */
    private HttpClient $client;

    /**
     * Create a new Google Image client
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
                    "User-Agent" => 'Mozilla/5.0 (Linux; Android 6.0.1; Nexus 5X Build/MMB29P) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.96',
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
            'tbm' => 'isch',
            'q' => null,
            'hl' => "en",
            'safe' => "medium",
            'rsz' => '3',
            'tbs' => '',
        ], $settings);

        // call the api endpoint
        $response = $this->request("GET", "", [
            "query" => $settings
        ]);

        preg_match_all('/data-ou="(http[^"]*)"/', $response, $images);
        $images = array_map(function ($str) {

            $pattern = '/,\\["(http[^"]((?!gstatic).)*)",\\d+?,\\d+?\\]/';
            $replacement = '$1';
            $real_url = preg_replace($pattern, $replacement, $str);
            return $real_url;
        }, $images[1]);

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
