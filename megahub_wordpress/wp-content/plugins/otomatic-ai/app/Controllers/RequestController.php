<?php

namespace OtomaticAi\Controllers;

use DOMDocument;
use Exception;
use OtomaticAi\Api\OtomaticAi\Client;
use OtomaticAi\Models\Preset;
use OtomaticAi\Utils\Language;
use OtomaticAi\Vendors\Illuminate\Support\Arr;
use OtomaticAi\Vendors\Illuminate\Support\Str;

class RequestController extends Controller
{
    public function trends()
    {
        $this->verifyNonce();

        $this->validate([
            "language" => ["required", "string"],
        ]);

        // retrieve google trends
        $url = "https://trends.google.com/trends/trendingsearches/daily/rss" . "?" . http_build_query([
            'geo' => Language::find($this->input('language', 'en'))->google_trends,
        ]);
        $content = @file_get_contents($url);
        if ($content === false) {
            $this->response(["message" => "An error occurred", "error" => "Unable to retrieve Google Trends."], 503);
        }

        $items = [];

        // parse the xml
        $feed = new DOMDocument();
        $feed->loadXML($content);
        $channel = $feed->getElementsByTagName('channel')->item(0);

        if (!empty($channel)) {
            foreach ($channel->getElementsByTagName('item') as $item) {

                // get title
                $title = $item->getElementsByTagName('title')->item(0);
                if (empty($title)) {
                    continue;
                }
                $title = $title->firstChild->nodeValue;

                // get traffic
                $traffic = $item->getElementsByTagNameNS('*', 'approx_traffic')->item(0);
                if (!empty($traffic)) {
                    $traffic = $traffic->firstChild->nodeValue;
                } else {
                    $traffic = null;
                }

                // get thumbnail
                $thumbnail = $item->getElementsByTagNameNS('*', 'picture')->item(0);
                if (!empty($thumbnail)) {
                    $thumbnail = $thumbnail->firstChild->nodeValue;
                } else {
                    $thumbnail = null;
                }

                if ($title !== null) {
                    $items[] = [
                        "title" => $title,
                        "traffic" => $traffic,
                        "thumbnail" => $thumbnail,
                    ];
                }
            }
        }

        $this->response($items);
    }

    public function suggestions()
    {
        $this->verifyNonce();

        $this->validate([
            "language" => ["required", "string"],
        ]);

        $items = [];

        // make search
        $search = null;
        $host = parse_url(get_site_url(), PHP_URL_HOST);

        if (!empty($host)) {
            $search = "site:" . $host;
        }
        if (empty($search))
            return $this->response($items);

        try {
            // call the api client
            $api = new Client;
            $result = $api->googleSearch($search, Language::find($this->input('language', 'en'))->key);

            // get the google organic results
            $organicResults = Arr::get($result, "organic_results", []);

            $titles = implode(' ', array_column($organicResults, 'title'));

            if (!empty($titles)) {
                $preset = Preset::findFromAPI("domain_suggestions");

                if ($preset) {
                    $response = $preset->process([
                        "language" => Language::find($this->input('language', 'en'))->value,
                        "request" => $titles,
                    ]);

                    // get the response content
                    $response = json_decode(Arr::get($response, 'choices.0.message.content'), true, 512, JSON_THROW_ON_ERROR);
                    $items = Arr::get($response, "values");
                    if (!empty($items)) {
                        $items = array_map(function ($str) {
                            return Str::clean($str);
                        }, $items);
                        $items = array_values(array_filter($items, function ($str) {
                            return !empty($str);
                        }));
                    }
                }
            }
        } catch (Exception $e) {
        }

        return $this->response(["domain" => $host, "items" => $items]);
    }

    public function details()
    {
        $this->verifyNonce();

        $this->validate([
            "language" => ["required", "string"],
            "query" => ["required", "string"],
        ]);

        try {
            // call the api client
            $api = new Client;
            $result = $api->googleSearch($this->input('query'), Language::find($this->input('language', 'en'))->key);

            return $this->response($result);
        } catch (Exception $e) {
        }

        return $this->emptyResponse();
    }
}
