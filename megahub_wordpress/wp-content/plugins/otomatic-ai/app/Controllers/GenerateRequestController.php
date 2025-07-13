<?php

namespace OtomaticAi\Controllers;

use Exception;
use OtomaticAi\Models\Preset;
use OtomaticAi\Utils\GoogleNews;
use OtomaticAi\Utils\Language;
use OtomaticAi\Utils\RobotsTxt;
use OtomaticAi\Utils\RSS\Reader;
use OtomaticAi\Vendors\Carbon\Carbon;
use OtomaticAi\Vendors\Illuminate\Support\Arr;
use OtomaticAi\Vendors\Illuminate\Support\Collection;
use OtomaticAi\Vendors\Illuminate\Support\Str;
use OtomaticAi\Vendors\Illuminate\Validation\Rule;
use OtomaticAi\Vendors\vipnytt\SitemapParser;
use OtomaticAi\Vendors\GuzzleHttp\Client;
use OtomaticAi\Vendors\GuzzleHttp\Pool;
use OtomaticAi\Vendors\GuzzleHttp\Psr7\Request;
use OtomaticAi\Vendors\GuzzleHttp\Psr7\Response;

class GenerateRequestController extends Controller
{
    public function __invoke()
    {
        $this->verifyNonce();

        $this->validate([
            "engine" => ["required", Rule::in('siloing', 'informative', 'commercial', 'local', 'discover', 'news', 'news-now', 'rss', 'rss-now', 'sitemap', 'url')],
            "query" => ["required", "string"],
            "length" => ["nullable", "numeric", "min:1", "max:50"],
            "page" => ["nullable", "numeric", "min:1", "max:50"],
            "depth" => ["nullable", "numeric", "min:1"],
            "language" => ["required", "string"],
        ]);

        switch ($this->input('engine')) {
            case "informative":
                $response["requests"] = $this->makeInformativeResponse();
                break;
            case "commercial":
                $response["requests"] = $this->makeCommercialResponse();
                break;
            case "discover":
                $response["requests"] = $this->makeDiscoverResponse();
                break;
            case "local":
                $response["requests"] = $this->makeLocalResponse();
                break;
            case "news":
            case "news-now":
                $response["requests"] = $this->makeNewsResponse();
                break;
            case "siloing":
                $response["requests"] = $this->makeSiloingResponse();
                break;
            case "rss":
            case "rss-now":
                $response["requests"] = $this->makeRssResponse();
                break;
            case "sitemap":
                $response["requests"] = $this->makeSitemapResponse();
                break;
            case "url":
                $response["requests"] = $this->makeUrlResponse();
                break;
        }

        $this->response($response);
    }

    private function makeInformativeResponse(): array
    {
        try {
            // get the openai preset
            $preset = Preset::findFromAPI("requests_informative_multi");

            // make keywords
            $keywords = explode("\n", $this->input('query', ""));
            $keywords = array_map(function ($str) {
                return Str::clean($str);
            }, $keywords);
            $keywords = array_values(array_filter($keywords, function ($str) {
                return !empty($str);
            }));

            if (empty($keywords)) {
                return [];
            }

            // make payloads
            $payloads = [];
            foreach ($keywords as $keyword) {
                $payloads[] = [
                    "language" => Language::find($this->input('language', 'en'))->value,
                    "length" => $this->input('length', 1),
                    "request" => $keyword,
                ];
            }

            // run the pool preset
            $responses = $preset->processPool($payloads);

            // get the response content
            $output = [];
            foreach ($responses as $index => $response) {
                $response = json_decode(Arr::get($response, 'choices.0.message.content'), true, 512, JSON_THROW_ON_ERROR);
                $items = Arr::get($response, "values");
                if (!empty($items)) {
                    $items = array_map(function ($str) {
                        return Str::clean($str);
                    }, $items);
                    $items = array_values(array_filter($items, function ($str) {
                        return !empty($str);
                    }));
                    foreach ($items as $item) {
                        $output[] = [
                            "title" => $item,
                            "meta" => [
                                "keyword" => $keywords[$index]
                            ]
                        ];
                    }
                }
            }

            ksort($output);

            return $output;
        } catch (Exception $e) {
            $this->response(["message" => "An error occurred", "error" => $e->getMessage()], 503);
        }

        return [];
    }

    private function makeCommercialResponse(): array
    {
        try {
            // get the openai preset
            $preset = Preset::findFromAPI("requests_commercial_multi");

            // make keywords
            $keywords = explode("\n", $this->input('query', ""));
            $keywords = array_map(function ($str) {
                return Str::clean($str);
            }, $keywords);
            $keywords = array_values(array_filter($keywords, function ($str) {
                return !empty($str);
            }));

            if (empty($keywords)) {
                return [];
            }

            // make payloads
            $payloads = [];
            foreach ($keywords as $keyword) {
                $payloads[] = [
                    "language" => Language::find($this->input('language', 'en'))->value,
                    "length" => $this->input('length', 1),
                    "request" => $keyword,
                ];
            }

            // run the pool preset
            $responses = $preset->processPool($payloads);

            // get the response content
            $output = [];
            foreach ($responses as $index => $response) {
                $response = json_decode(Arr::get($response, 'choices.0.message.content'), true, 512, JSON_THROW_ON_ERROR);
                $items = Arr::get($response, "values");
                if (!empty($items)) {
                    $items = array_map(function ($str) {
                        return Str::clean($str);
                    }, $items);
                    $items = array_values(array_filter($items, function ($str) {
                        return !empty($str);
                    }));
                    foreach ($items as $item) {
                        $output[] = [
                            "title" => $item,
                            "meta" => [
                                "keyword" => $keywords[$index]
                            ]
                        ];
                    }
                }
            }

            ksort($output);

            return $output;
        } catch (Exception $e) {
            $this->response(["message" => "An error occurred", "error" => $e->getMessage()], 503);
        }

        return [];
    }

    private function makeDiscoverResponse(): array
    {
        try {
            // get the openai preset
            $preset = Preset::findFromAPI("requests_discover_multi");

            // make keywords
            $keywords = explode("\n", $this->input('query', ""));
            $keywords = array_map(function ($str) {
                return Str::clean($str);
            }, $keywords);
            $keywords = array_values(array_filter($keywords, function ($str) {
                return !empty($str);
            }));

            if (empty($keywords)) {
                return [];
            }

            // make payloads
            $payloads = [];
            foreach ($keywords as $keyword) {
                $payloads[] = [
                    "language" => Language::find($this->input('language', 'en'))->value,
                    "length" => $this->input('length', 1),
                    "request" => $keyword,
                ];
            }

            // run the pool preset
            $responses = $preset->processPool($payloads);

            // get the response content
            $output = [];
            foreach ($responses as $index => $response) {
                $response = json_decode(Arr::get($response, 'choices.0.message.content'), true, 512, JSON_THROW_ON_ERROR);
                $items = Arr::get($response, "values");
                if (!empty($items)) {
                    $items = array_map(function ($str) {
                        return Str::clean($str);
                    }, $items);
                    $items = array_values(array_filter($items, function ($str) {
                        return !empty($str);
                    }));
                    foreach ($items as $item) {
                        $output[] = [
                            "title" => $item,
                            "meta" => [
                                "keyword" => $keywords[$index]
                            ]
                        ];
                    }
                }
            }

            ksort($output);

            return $output;
        } catch (Exception $e) {
            $this->response(["message" => "An error occurred", "error" => $e->getMessage()], 503);
        }

        return [];
    }

    private function makeLocalResponse(): array
    {
        try {
            // get the openai preset
            $preset = Preset::findFromAPI("requests_local_multi");

            // make keywords
            $keywords = explode("\n", $this->input('query', ""));
            $keywords = array_map(function ($str) {
                return Str::clean($str);
            }, $keywords);
            $keywords = array_values(array_filter($keywords, function ($str) {
                return !empty($str);
            }));

            if (empty($keywords)) {
                return [];
            }

            // make payloads
            $payloads = [];
            foreach ($keywords as $keyword) {
                $payloads[] = [
                    "language" => Language::find($this->input('language', 'en'))->value,
                    "length" => $this->input('length', 1),
                    "request" => $keyword,
                ];
            }

            // run the pool preset
            $responses = $preset->processPool($payloads);

            // get the response content
            $output = [];
            foreach ($responses as $index => $response) {
                $response = json_decode(Arr::get($response, 'choices.0.message.content'), true, 512, JSON_THROW_ON_ERROR);
                $items = Arr::get($response, "values");
                if (!empty($items)) {
                    $items = array_map(function ($str) {
                        return Str::clean($str);
                    }, $items);
                    $items = array_values(array_filter($items, function ($str) {
                        return !empty($str);
                    }));
                    foreach ($items as $item) {
                        $output[] = [
                            "title" => $item,
                            "meta" => [
                                "keyword" => $keywords[$index]
                            ]
                        ];
                    }
                }
            }

            ksort($output);

            return $output;
        } catch (Exception $e) {
            $this->response(["message" => "An error occurred", "error" => $e->getMessage()], 503);
        }

        return [];
    }

    private function makeNewsResponse(): array
    {
        try {
            $perPage = $this->input('length', 5);
            $page = $this->input('page', 1);

            $titles = [];
            $items = GoogleNews::search($this->input('query', ""), Language::find($this->input('language', 'en')));

            // paginate
            $items = new Collection($items);
            $items = $items->skip($perPage * ($page - 1))->take($perPage)->toArray();

            foreach ($items as $item) {

                $title = $item['title'];
                $url = $item['url'];
                $guid = $item['url'];
                $guid = str_replace(["http://", "https://"], "", $guid);

                $titles[] =  [
                    "title" => $title,
                    "meta" => [
                        "url" => $url,
                        "guid" => $guid,
                    ]
                ];
            }

            // rewrite titles
            if (!empty($titles)) {

                // get the openai preset
                $preset = Preset::findFromAPI("requests_news_rewrite");

                // make payloads
                $payloads = [];
                foreach ($titles as $title) {
                    $payloads[] = [
                        "language" => Language::find($this->input('language', 'en'))->value,
                        "request" => $title["title"],
                    ];
                }

                // run the pool preset
                $responses = $preset->processPool($payloads);

                // get the response content
                foreach ($responses as $index => $response) {
                    $response = json_decode(Arr::get($response, 'choices.0.message.content'), true, 512, JSON_THROW_ON_ERROR);
                    $item = Arr::get($response, "value");
                    $item = Str::clean($item);
                    if (!empty($item) && isset($titles[$index])) {
                        $titles[$index]["title"] = $item;
                    }
                }

                ksort($titles);
            }
            return $titles;
        } catch (Exception $e) {
            $this->response(["message" => "An error occurred", "error" => $e->getMessage()], 503);
        }

        return [];
    }

    private function makeUrlResponse(): array
    {
        try {
            // make urls
            $urls = explode("\n", $this->input('query', ""));
            $urls = array_map(function ($str) {
                return Str::clean($str);
            }, $urls);
            $urls = array_values(array_filter($urls, function ($str) {
                return !empty($str);
            }));

            if (empty($urls)) {
                return [];
            }

            // get urls titles
            $titles = $this->getUrlsTitles($urls);

            // rewrite titles
            if (!empty($titles)) {

                // get the openai preset
                $preset = Preset::findFromAPI("requests_informative_rewrite");

                // make payloads
                $payloads = [];
                foreach ($titles as $title) {
                    $payloads[] = [
                        "language" => Language::find($this->input('language', 'en'))->value,
                        "request" => $title["title"],
                    ];
                }

                // run the pool preset
                $responses = $preset->processPool($payloads);

                // get the response content
                foreach ($responses as $index => $response) {
                    $response = json_decode(Arr::get($response, 'choices.0.message.content'), true, 512, JSON_THROW_ON_ERROR);
                    $item = Arr::get($response, "value");
                    $item = Str::clean($item);
                    if (!empty($item) && isset($titles[$index])) {
                        $titles[$index]["title"] = $item;
                    }
                }

                ksort($titles);
            }

            return $titles;
        } catch (Exception $e) {
            $this->response(["message" => "An error occurred", "error" => $e->getMessage()], 503);
        }

        return [];
    }

    private function makeRssResponse(): array
    {
        try {
            $perPage = $this->input('length', 5);
            $page = $this->input('page', 1);

            $titles = [];
            $rss = Reader::load($this->input('query', ""));

            // paginate
            $items = new Collection($rss->items);
            $items = $items->skip($perPage * ($page - 1))->take($perPage)->toArray();

            foreach ($items as $item) {

                $url = (string) $item->url;
                $title = (string) $item->title;
                $guid = (string) $item->guid;
                if (strlen($guid) < 0) {
                    $guid = str_replace(["http://", "https://"], "", $url);
                }
                $guid = str_replace(["http://", "https://"], "", $guid);

                $titles[] =  [
                    "title" => $title,
                    "meta" => [
                        "url" => $url,
                        "guid" => $guid,
                    ]
                ];
            }

            // rewrite titles
            if (!empty($titles)) {

                // get the openai preset
                $preset = Preset::findFromAPI("requests_informative_rewrite");

                // make payloads
                $payloads = [];
                foreach ($titles as $title) {
                    $payloads[] = [
                        "language" => Language::find($this->input('language', 'en'))->value,
                        "request" => $title["title"],
                    ];
                }

                // run the pool preset
                $responses = $preset->processPool($payloads);

                // get the response content
                foreach ($responses as $index => $response) {
                    $response = json_decode(Arr::get($response, 'choices.0.message.content'), true, 512, JSON_THROW_ON_ERROR);
                    $item = Arr::get($response, "value");
                    $item = Str::clean($item);
                    if (!empty($item) && isset($titles[$index])) {
                        $titles[$index]["title"] = $item;
                    }
                }

                ksort($titles);
            }
            return $titles;
        } catch (Exception $e) {
            $this->response(["message" => "An error occurred", "error" => $e->getMessage()], 503);
        }

        return [];
    }

    private function makeSitemapResponse(): array
    {
        try {

            // get sitemap
            $parser = new SitemapParser();
            $parser->parse($this->input('query', ""));
            $urls = array_keys($parser->getURLs());

            // get urls titles
            $titles = $this->getUrlsTitles($urls);

            // rewrite titles
            if (!empty($titles)) {

                // get the openai preset
                $preset = Preset::findFromAPI("requests_informative_rewrite");

                // make payloads
                $payloads = [];
                foreach ($titles as $title) {
                    $payloads[] = [
                        "language" => Language::find($this->input('language', 'en'))->value,
                        "request" => $title["title"],
                    ];
                }

                // run the pool preset
                $responses = $preset->processPool($payloads);

                // get the response content
                foreach ($responses as $index => $response) {
                    $response = json_decode(Arr::get($response, 'choices.0.message.content'), true, 512, JSON_THROW_ON_ERROR);
                    $item = Arr::get($response, "value");
                    $item = Str::clean($item);
                    if (!empty($item) && isset($titles[$index])) {
                        $titles[$index]["title"] = $item;
                    }
                }

                ksort($titles);
            }
            return $titles;
        } catch (Exception $e) {
            $this->response(["message" => "An error occurred", "error" => $e->getMessage()], 503);
        }

        return [];
    }

    private function makeSiloingResponse(): array
    {
        try {
            // get the openai preset
            $preset = Preset::findFromAPI("requests_siloing");

            // run the preset
            $response = $preset->process([
                "language" => Language::find($this->input('language', 'en'))->value,
                "request" => $this->input('query'),
            ]);

            // get the response content
            $content = Arr::get($response, 'choices.0.message.content');
            if ($content) {
                $content = json_decode($content, true, 512, JSON_THROW_ON_ERROR);
                return $this->parseSiloingJson($content, $this->input('query'), $this->input("depth", 1));
            }
        } catch (Exception $e) {
            $this->response(["message" => "An error occurred", "error" => $e->getMessage()], 503);
        }

        return [];
    }

    private function parseSiloingJson($array, $query, $maxDepth, $currentDepth = 0)
    {
        $array = Arr::isAssoc($array) ? [$array] : $array;
        $items = [];

        if ($currentDepth < $maxDepth) {
            foreach ($array as $child) {

                // quit if no title
                if (empty($child["title"]))
                    continue;

                // clean the title
                $title = Str::clean($child["title"]);

                // quit if title is empty
                if (empty($child["title"])) {
                    continue;
                }

                // detect if the title is equal to the query
                if (Str::lower($child["title"]) === Str::lower($query)) {

                    // parse children
                    if (!empty($child["children"])) {

                        // parse children
                        $children = $this->parseSiloingJson($child["children"], $query, $maxDepth, $currentDepth);

                        $items = array_merge($items, $children);
                    }
                } else {
                    $item = [
                        "title" => $title,
                        "meta" => [
                            "base_title" => $query
                        ]
                    ];

                    // children
                    if (!empty($child["children"])) {

                        // parse children
                        $children = $this->parseSiloingJson($child["children"], $query, $maxDepth, $currentDepth + 1);

                        // add children if not empty
                        if (count($children) > 0)
                            $item["children"] = $children;
                    }

                    $items[] = $item;
                }
            }
        }

        return $items;
    }

    private function getUrlsTitles(array $urls): array
    {
        $output = [];

        // create the client
        $client = new Client();

        // make the requests
        $requests = [];
        foreach ($urls as $url) {
            if (!$this->isDisabledByRobotsTxt($url)) {
                $requests[] = new Request(
                    'GET',
                    $url,
                );
            }
        }

        // create the pool
        $pool = new Pool($client, $requests, [
            'concurrency' => 20,
            'fulfilled' => function (Response $response, $index) use (&$output, $urls) {
                $response = $response->getBody()->getContents();
                // h1
                $title = preg_match('/<h1[^>]*>(.*?)<\/h1>/ims', $response, $matches) ? $matches[1] : null;
                if (!empty($urls[$index]) && !empty($title)) {
                    $output[$index] = [
                        "title" => $title,
                        "meta" => [
                            "url" => $urls[$index],
                        ]
                    ];
                } else {
                    // title
                    $title = preg_match('/<title[^>]*>(.*?)<\/title>/ims', $response, $matches) ? $matches[1] : null;
                    if (!empty($urls[$index]) && !empty($title)) {
                        $output[$index] = [
                            "title" => $title,
                            "meta" => [
                                "url" => $urls[$index],
                            ]
                        ];
                    }
                }
            },
            'rejected' => function (Exception $reason, $index) {
            },
        ]);

        // call the pool
        $promise = $pool->promise();
        $promise->wait();

        // sort and get only values
        ksort($output);
        return array_values($output);
    }

    /**
     * Determine if the scrap is disabled by the robots.txt
     *
     * @param string $url
     * @return boolean
     */
    private function isDisabledByRobotsTxt(string $url)
    {
        $robots = RobotsTxt::fromUrl($url);
        return !empty($robots->getRules("otomaticAI"));
    }
}
