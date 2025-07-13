<?php

namespace OtomaticAi\Utils;

use Exception;
use OtomaticAi\Vendors\Carbon\Carbon;
use OtomaticAi\Vendors\GuzzleHttp\Client as HttpClient;
use OtomaticAi\Vendors\GuzzleHttp\Pool;
use OtomaticAi\Vendors\GuzzleHttp\Psr7\Request;
use OtomaticAi\Vendors\GuzzleHttp\Psr7\Response;
use OtomaticAi\Vendors\Illuminate\Support\Arr;

class GoogleNews
{

    /**
     * The google news endpoint
     *
     * @var string
     */
    static private string $endpoint = "https://news.google.com/rss/search";

    /**
     * The GuzzleHttp client
     *
     * @var ?HttpClient
     */
    static private ?HttpClient $client = null;

    static public function search(string $search, Language $language)
    {
        $requests = [
            new Request(
                'GET',
                self::$endpoint . "?" . http_build_query([
                    'tbm' => "nws",
                    'q' => $search,
                    'hl' => $language->key,
                ])
            )
        ];

        return Arr::get(self::run($requests), 0, []);
    }

    static public function searchPool(array $searches, Language $language)
    {
        $requests = [];
        foreach ($searches as $search) {
            $requests[] = new Request(
                'GET',
                self::$endpoint . "?" . http_build_query([
                    'tbm' => "nws",
                    'q' => $search,
                    'hl' => $language->key,
                ])
            );
        }

        return self::run($requests);
    }

    /**
     * Get the http client
     *
     * @return HttpClient
     */
    static private function client()
    {
        if (self::$client === null) {
            self::$client = new HttpClient();
        }

        return self::$client;
    }

    /**
     * Perform an http pool requests
     *
     * @param array $requests
     * @return array
     * @throws Exception
     */
    static private function run(array $requests)
    {
        $output = [];

        // create the pool
        $pool = new Pool(self::client(), $requests, [
            'concurrency' => 10,
            'fulfilled' => function (Response $response, $index) use (&$output, $requests) {
                $content = $response->getBody()->getContents();

                $items = [];
                $rss = @simplexml_load_string($content);
                if ($rss !== false) {
                    foreach ($rss->channel->item as $item) {

                        // parse title
                        $title = (string) $item->title;
                        $source = (string) $item->source;
                        $title = str_replace("- " . $source, "", $title);
                        $title = trim($title);
                        if (empty($title))
                            continue;

                        // parse url
                        $url = null;
                        $guid = (string) $item->guid;
                        $permalink = base64_decode($guid);
                        $regex = "/(https?:\/\/[\w\d\.\/\?\-\_\=\+\%\&]*)/i";
                        preg_match_all($regex, $permalink, $matches, PREG_PATTERN_ORDER);
                        if (count($matches[0]) > 0) {
                            $url = $matches[0][0];
                        }
                        if (empty($url))
                            continue;

                        // pubDate
                        $pubDate = (string) $item->pubDate;
                        if ((!empty($pubDate))) {
                            $pubDate = new Carbon($pubDate);
                            $pubDate = $pubDate->format("Y-m-d H:i:s");
                        } else {
                            $pubDate = null;
                        }

                        // add to items
                        $items[] =  [
                            "title" => $title,
                            "url" =>  $url,
                            "pub_date" => $pubDate,
                        ];
                    }
                }

                $output[$index] = $items;
            },
            'rejected' => function (Exception $reason, $index) {
                throw $reason;
            },
        ]);

        // call the pool
        $promise = $pool->promise();
        $promise->wait();

        return $output;
    }
}
