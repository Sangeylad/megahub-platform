<?php

namespace OtomaticAi\Controllers;

use Exception;
use OtomaticAi\Models\Preset;
use OtomaticAi\Models\Project;
use OtomaticAi\Utils\Language;
use OtomaticAi\Vendors\Illuminate\Support\Arr;
use OtomaticAi\Vendors\Illuminate\Support\Str;

class BuyerPersonaController extends Controller
{
    public function generate()
    {
        $this->verifyNonce();

        $this->validate([
            "language" => ["required", "string"],
            "titles" => ["required", "array"],
        ]);

        $titles = $this->input("titles", []);

        $titles = Arr::random($titles, min(count($titles), 15));
        if (count($titles) > 0) {
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
                foreach ($responses as $index => $response) {
                    $response = json_decode(Arr::get($response, 'choices.0.message.content'), true, 512, JSON_THROW_ON_ERROR);
                    $keyword = Arr::get($response, "value");

                    if (isset($titles[$index])) {
                        $titles[$index] = $keyword;
                    }
                }

                $preset = Preset::findFromAPI("buyer_persona");
                $response = $preset->process([
                    "language" => Language::find($this->input('language', 'en'))->value,
                    "keywords" => implode("\n", $titles),
                ]);
                $response = json_decode(Arr::get($response, 'choices.0.message.content'), true, 512, JSON_THROW_ON_ERROR);
                $content = Arr::get($response, "value");
                $content = Str::clean($content);

                $this->response(["description" => $content]);
            } catch (Exception $e) {
            }
        }

        $this->response(["description" => ""]);
    }

    public function generateFromProject()
    {
        $this->verifyNonce();

        $this->validate([
            "language" => ["required", "string"],
            "project" => ["required"],
        ]);

        $project = Project::find($this->input("project"));
        if ($project === null) {
            $this->response(["description" => ""]);
        }

        $titles = $project->publications()->select("title")->inRandomOrder()->take(15)->get()->pluck("title")->toArray();
        if (count($titles) > 0) {
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
                foreach ($responses as $index => $response) {
                    $response = json_decode(Arr::get($response, 'choices.0.message.content'), true, 512, JSON_THROW_ON_ERROR);
                    $keyword = Arr::get($response, "value");

                    if (isset($titles[$index])) {
                        $titles[$index] = $keyword;
                    }
                }

                $preset = Preset::findFromAPI("buyer_persona");
                $response = $preset->process([
                    "language" => Language::find($this->input('language', 'en'))->value,
                    "keywords" => implode("\n", $titles),
                ]);
                $response = json_decode(Arr::get($response, 'choices.0.message.content'), true, 512, JSON_THROW_ON_ERROR);
                $content = Arr::get($response, "value");
                $content = Str::clean($content);

                $this->response(["description" => $content]);
            } catch (Exception $e) {
            }
        }

        $this->response(["description" => ""]);
    }
}
