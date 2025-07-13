<?php

namespace OtomaticAi\Controllers;

use Exception;
use OtomaticAi\Api\OtomaticAi\Client;
use OtomaticAi\Utils\Language;
use OtomaticAi\Vendors\Carbon\Carbon;
use OtomaticAi\Vendors\Illuminate\Support\Arr;

class HelpCenterController extends Controller
{
    const CACHE_OPTION_NAME = "otomatic_ai_help_center_cache";

    public function __invoke()
    {
        $this->verifyNonce();

        $output = ["categories" => [], "tags" => [], "videos" => []];

        if (function_exists('get_option')) {
            $cache = get_option(self::CACHE_OPTION_NAME, null);

            // fetch or refresh cache
            if (
                empty($cache) ||
                Carbon::createFromFormat(
                    "Y-m-d H:i:s",
                    Arr::get(
                        $cache,
                        "cached_at",
                        Carbon::now()->subMonth()
                    )
                )
                ->lt(
                    Carbon::now()->subMinutes(5)
                )
            ) {
                try {
                    $api = new Client;
                    $output = $api->helpCenter();

                    $cache = [
                        "data" => $output,
                        "cached_at" => Carbon::now()->format("Y-m-d H:i:s"),
                    ];

                    if (function_exists('update_option')) {
                        update_option(self::CACHE_OPTION_NAME, $cache, false);
                    }
                } catch (Exception $e) {
                }
            } else {
                $output = Arr::get($cache, "data", $output);
            }
        }

        $output = $this->transformOutput($output);

        $this->response($output);
    }

    private function transformOutput(array $output): array
    {
        $default = "en";
        $language = Language::findFromLocale();

        // categories
        foreach (Arr::get($output, "categories", []) as $index => $category) {
            $name = Arr::get($category, "name." . $language->key, Arr::get($category, "name." . $default));
            Arr::set($output, "categories." . $index . ".name", $name);
        }

        // tags
        foreach (Arr::get($output, "tags", []) as $index => $tag) {
            $name = Arr::get($tag, "name." . $language->key, Arr::get($tag, "name." . $default));
            Arr::set($output, "tags." . $index . ".name", $name);
        }

        // videos
        foreach (Arr::get($output, "videos", []) as $index => $video) {
            // title
            $title = Arr::get($video, "title." . $language->key, Arr::get($video, "title." . $default));
            Arr::set($output, "videos." . $index . ".title", $title);

            // video_id
            $videoId = Arr::get($video, "video_id." . $language->key, Arr::get($video, "video_id." . $default));
            Arr::set($output, "videos." . $index . ".video_id", $videoId);

            // category
            $categoryId = Arr::get($video, "category.key");
            Arr::set($output, "videos." . $index . ".category", $categoryId);

            // tags
            $tags = array_map(function ($t) {
                return $t["key"];
            }, Arr::get($video, "tags", []));
            Arr::set($output, "videos." . $index . ".tags", $tags);
        }

        return $output;
    }
}
