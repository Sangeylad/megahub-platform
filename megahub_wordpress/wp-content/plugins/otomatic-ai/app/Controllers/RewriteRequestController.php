<?php

namespace OtomaticAi\Controllers;

use Exception;
use OtomaticAi\Models\Preset;
use OtomaticAi\Utils\Language;
use OtomaticAi\Vendors\Illuminate\Support\Arr;
use OtomaticAi\Vendors\Illuminate\Support\Str;
use OtomaticAi\Vendors\Illuminate\Validation\Rule;

class RewriteRequestController extends Controller
{
    public function __invoke()
    {
        $this->verifyNonce();

        $this->validate([
            "engine" => ["required", Rule::in('informative', 'commercial', 'local', 'discover', 'news', 'news-now', "rss", "rss-now", "sitemap", "url")],
            "title" => ["required", "string"],
            "language" => ["required", "string"],
        ]);

        switch ($this->input('engine')) {
            case "informative":
                $response = $this->makeInformativeResponse();
                break;
            case "commercial":
                $response = $this->makeCommercialResponse();
                break;
            case "discover":
                $response = $this->makeDiscoverResponse();
                break;
            case "local":
                $response = $this->makeLocalResponse();
                break;
            case "rss":
                $response = $this->makeRssResponse();
                break;
            case "sitemap":
                $response = $this->makeSitemapResponse();
                break;
            case "url":
                $response = $this->makeUrlResponse();
                break;
            case "news":
                $response = $this->makeNewsResponse();
                break;
        }

        $this->response($response);
    }

    private function makeInformativeResponse(): array
    {
        try {
            // get the openai preset
            $preset = Preset::findFromAPI("requests_informative_rewrite");

            // run the preset
            $response = $preset->process([
                "language" => Language::find($this->input('language', 'en'))->value,
                "request" => $this->input('title'),
            ]);

            // get the response content
            $content = json_decode(Arr::get($response, 'choices.0.message.content'), true, 512, JSON_THROW_ON_ERROR);
            $content = Arr::get($content, "value");
            $content = Str::clean($content);

            if (!empty($content)) {
                return [
                    "title" => $content,
                ];
            }
        } catch (Exception $e) {
            $this->response(["message" => "An error occurred", "error" => $e->getMessage()], 503);
        }

        return [
            "title" => $this->input('title'),
        ];
    }

    private function makeCommercialResponse(): array
    {
        try {
            // get the openai preset
            $preset = Preset::findFromAPI("requests_commercial_rewrite");

            // run the preset
            $response = $preset->process([
                "language" => Language::find($this->input('language', 'en'))->value,
                "request" => $this->input('title'),
            ]);

            // get the response content
            $content = json_decode(Arr::get($response, 'choices.0.message.content'), true, 512, JSON_THROW_ON_ERROR);
            $content = Arr::get($content, "value");
            $content = Str::clean($content);

            if (!empty($content)) {
                return [
                    "title" => $content,
                ];
            }
        } catch (Exception $e) {
            $this->response(["message" => "An error occurred", "error" => $e->getMessage()], 503);
        }

        return [
            "title" => $this->input('title'),
        ];
    }

    private function makeDiscoverResponse(): array
    {
        try {
            // get the openai preset
            $preset = Preset::findFromAPI("requests_discover_rewrite");

            // run the preset
            $response = $preset->process([
                "language" => Language::find($this->input('language', 'en'))->value,
                "request" => $this->input('title'),
            ]);

            // get the response content
            $content = json_decode(Arr::get($response, 'choices.0.message.content'), true, 512, JSON_THROW_ON_ERROR);
            $content = Arr::get($content, "value");
            $content = Str::clean($content);

            if (!empty($content)) {
                return [
                    "title" => $content,
                ];
            }
        } catch (Exception $e) {
            $this->response(["message" => "An error occurred", "error" => $e->getMessage()], 503);
        }

        return [
            "title" => $this->input('title'),
        ];
    }

    private function makeLocalResponse(): array
    {
        try {
            // get the openai preset
            $preset = Preset::findFromAPI("requests_local_rewrite");

            // run the preset
            $response = $preset->process([
                "language" => Language::find($this->input('language', 'en'))->value,
                "request" => $this->input('title'),
            ]);

            // get the response content
            $content = json_decode(Arr::get($response, 'choices.0.message.content'), true, 512, JSON_THROW_ON_ERROR);
            $content = Arr::get($content, "value");
            $content = Str::clean($content);

            if (!empty($content)) {
                return [
                    "title" => $content,
                ];
            }
        } catch (Exception $e) {
            $this->response(["message" => "An error occurred", "error" => $e->getMessage()], 503);
        }

        return [
            "title" => $this->input('title'),
        ];
    }

    private function makeNewsResponse()
    {
        try {
            // get the openai preset
            $preset = Preset::findFromAPI("requests_news_rewrite");

            // run the preset
            $response = $preset->process([
                "language" => Language::find($this->input('language', 'en'))->value,
                "request" => $this->input('title'),
            ]);

            // get the response content
            $content = json_decode(Arr::get($response, 'choices.0.message.content'), true, 512, JSON_THROW_ON_ERROR);
            $content = Arr::get($content, "value");
            $content = Str::clean($content);

            if (!empty($content)) {
                return [
                    "title" => $content,
                ];
            }
        } catch (Exception $e) {
            $this->response(["message" => "An error occurred", "error" => $e->getMessage()], 503);
        }

        return [
            "title" => $this->input('title'),
        ];
    }

    private function makeRssResponse()
    {
        try {
            // get the openai preset
            $preset = Preset::findFromAPI("requests_informative_rewrite");

            // run the preset
            $response = $preset->process([
                "language" => Language::find($this->input('language', 'en'))->value,
                "request" => $this->input('title'),
            ]);

            // get the response content
            $content = json_decode(Arr::get($response, 'choices.0.message.content'), true, 512, JSON_THROW_ON_ERROR);
            $content = Arr::get($content, "value");
            $content = Str::clean($content);

            if (!empty($content)) {
                return [
                    "title" => $content,
                ];
            }
        } catch (Exception $e) {
            $this->response(["message" => "An error occurred", "error" => $e->getMessage()], 503);
        }

        return [
            "title" => $this->input('title'),
        ];
    }

    private function makeSitemapResponse()
    {
        try {
            // get the openai preset
            $preset = Preset::findFromAPI("requests_informative_rewrite");

            // run the preset
            $response = $preset->process([
                "language" => Language::find($this->input('language', 'en'))->value,
                "request" => $this->input('title'),
            ]);

            // get the response content
            $content = json_decode(Arr::get($response, 'choices.0.message.content'), true, 512, JSON_THROW_ON_ERROR);
            $content = Arr::get($content, "value");
            $content = Str::clean($content);

            if (!empty($content)) {
                return [
                    "title" => $content,
                ];
            }
        } catch (Exception $e) {
            $this->response(["message" => "An error occurred", "error" => $e->getMessage()], 503);
        }

        return [
            "title" => $this->input('title'),
        ];
    }

    private function makeUrlResponse()
    {
        try {
            // get the openai preset
            $preset = Preset::findFromAPI("requests_informative_rewrite");

            // run the preset
            $response = $preset->process([
                "language" => Language::find($this->input('language', 'en'))->value,
                "request" => $this->input('title'),
            ]);

            // get the response content
            $content = json_decode(Arr::get($response, 'choices.0.message.content'), true, 512, JSON_THROW_ON_ERROR);
            $content = Arr::get($content, "value");
            $content = Str::clean($content);

            if (!empty($content)) {
                return [
                    "title" => $content,
                ];
            }
        } catch (Exception $e) {
            $this->response(["message" => "An error occurred", "error" => $e->getMessage()], 503);
        }

        return [
            "title" => $this->input('title'),
        ];
    }
}
