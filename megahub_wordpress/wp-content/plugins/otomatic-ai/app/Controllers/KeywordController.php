<?php

namespace OtomaticAi\Controllers;

use Exception;
use OtomaticAi\Api\Haloscan\Client;
use OtomaticAi\Models\Preset;
use OtomaticAi\Utils\Language;
use OtomaticAi\Utils\Settings;
use OtomaticAi\Vendors\Illuminate\Support\Arr;
use OtomaticAi\Vendors\Illuminate\Validation\Rule;

class KeywordController extends Controller
{
    public function metrics()
    {
        $this->verifyNonce();

        $this->validate([
            "requests" => ["required", "array"],
            "engine" => ["required", Rule::in('informative', 'commercial', 'local', 'discover', 'news', 'news-now', 'siloing', 'rss', 'rss-now', 'sitemap', 'url')],
            "language" => ["required", "string"],
        ]);

        $requests = $this->input("requests", []);

        // verify that the HaloScan API key is set
        if (empty(Settings::get('api.haloscan.api_key'))) {
            $this->response($requests);
        }

        // get requests titles
        $titles = $this->getTitles($requests);

        // remove duplicate titles
        $titles = array_unique($titles);
        $titles = array_values($titles);

        try {
            // get the preset for generate main keyword
            $preset = Preset::findFromAPI("main_keyword");

            // make payloads
            $payloads = [];
            foreach ($titles as $title) {
                $payloads[] = [
                    "language" => Language::find($this->input('language', 'en'))->value,
                    "request" => $title,
                ];
            }

            // run the pool preset
            $responses = $preset->processPool($payloads);

            // get the response content
            $associatedKeywords = [];
            foreach ($responses as $index => $response) {
                $response = json_decode(Arr::get($response, 'choices.0.message.content'), true, 512, JSON_THROW_ON_ERROR);
                $keyword = Arr::get($response, "value");

                // associate title and main keyword
                $associatedKeywords[] = [
                    "keyword" => $keyword,
                    "title" => $titles[$index],
                ];
            }
        } catch (Exception $e) {
            $this->response(["message" => "An error occurred", "error" => $e->getMessage()], 503);
        }

        // take only keywords
        $keywords = array_column($associatedKeywords, "keyword");

        // remove duplicate keywords
        $keywords = array_unique($keywords);
        $keywords = array_values($keywords);

        // call haloscan api
        try {
            $api = new Client();
            $results = Arr::get($api->keywordsBulk([
                "keywords" => $keywords
            ]), "results", []);
            $results = Arr::keyBy($results, 'keyword');
        } catch (Exception $e) {
            $this->response($requests);
        }

        // add the metrics to the associatedKeywords
        foreach ($associatedKeywords as $index => $associatedKeyword) {
            $associatedKeywords[$index]["metrics"] = Arr::get($results, $associatedKeyword["keyword"]);
        }

        // key $associatedKeywords by title
        $associatedKeywords = Arr::keyBy($associatedKeywords, 'title');

        // update requests with the metrics
        $this->updateRequests($requests, function ($request) use ($associatedKeywords) {
            if (!isset($request["meta"])) {
                $request["meta"] = [];
            }

            if (isset($associatedKeywords[$request["title"]])) {
                $request["meta"]["metrics"] = $associatedKeywords[$request["title"]]["metrics"];
            }

            return $request;
        });

        $this->response($requests);
    }

    private function getTitles(array $requests): array
    {
        $titles = [];
        foreach ($requests as $request) {
            $titles[] = $request["title"];
            $titles = array_merge($titles, $this->getTitles(Arr::get($request, "children", [])));
        }

        return $titles;
    }

    private function updateRequests(array &$requests, $callback)
    {
        foreach ($requests as &$request) {
            $request = $callback($request);

            if (isset($request["children"])) {
                $this->updateRequests($request["children"], $callback);
            }
        }
    }
}
