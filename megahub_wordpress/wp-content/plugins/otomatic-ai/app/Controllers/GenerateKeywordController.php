<?php

namespace OtomaticAi\Controllers;

use Exception;
use OtomaticAi\Models\Preset;
use OtomaticAi\Utils\Language;
use OtomaticAi\Vendors\Illuminate\Support\Arr;
use OtomaticAi\Vendors\Illuminate\Support\Str;
use OtomaticAi\Vendors\Illuminate\Validation\Rule;

class GenerateKeywordController extends Controller
{
    public function __invoke()
    {
        $this->verifyNonce();

        $this->validate([
            "engine" => ["required", Rule::in('informative', 'commercial', 'local', 'discover', 'news')],
            "query" => ["required", "string"],
            "language" => ["required", "string"],
        ]);

        switch ($this->input('engine')) {
            case "informative":
                $response["keywords"] = $this->makeInformativeResponse();
                break;
            case "commercial":
                $response["keywords"] = $this->makeCommercialResponse();
                break;
            case "discover":
                $response["keywords"] = $this->makeDiscoverResponse();
                break;
            case "local":
                $response["keywords"] = $this->makeLocalResponse();
                break;
            case "news":
                $response["keywords"] = $this->makeNewsResponse();
                break;
        }

        $this->response($response);
    }

    private function makeInformativeResponse(): array
    {
        try {
            // get the openai preset
            $preset = Preset::findFromAPI("keywords_informative_v2");

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
                    "length" => $this->input('length', 50),
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
                    $output[$index] = [];
                    $output[$index] = array_merge($output[$index], $items);
                }
            }

            ksort($output);

            $output = Arr::flatten($output);

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
            $preset = Preset::findFromAPI("keywords_commercial_v2");

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
                    "length" => $this->input('length', 50),
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
                    $output[$index] = [];
                    $output[$index] = array_merge($output[$index], $items);
                }
            }

            ksort($output);

            $output = Arr::flatten($output);

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
            $preset = Preset::findFromAPI("keywords_discover_v2");

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
                    "length" => $this->input('length', 50),
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
                    $output[$index] = [];
                    $output[$index] = array_merge($output[$index], $items);
                }
            }

            ksort($output);

            $output = Arr::flatten($output);

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
            $preset = Preset::findFromAPI("keywords_local_v2");

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
                    "length" => $this->input('length', 50),
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
                    $output[$index] = [];
                    $output[$index] = array_merge($output[$index], $items);
                }
            }

            ksort($output);

            $output = Arr::flatten($output);

            return $output;
        } catch (Exception $e) {
            $this->response(["message" => "An error occurred", "error" => $e->getMessage()], 503);
        }

        return [];
    }

    private function makeNewsResponse(): array
    {
        try {
            // get the openai preset
            $preset = Preset::findFromAPI("keywords_news_v2");

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
                    "length" => $this->input('length', 50),
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
                    $output[$index] = [];
                    $output[$index] = array_merge($output[$index], $items);
                }
            }

            ksort($output);

            $output = Arr::flatten($output);

            return $output;
        } catch (Exception $e) {
            $this->response(["message" => "An error occurred", "error" => $e->getMessage()], 503);
        }

        return [];
    }
}
