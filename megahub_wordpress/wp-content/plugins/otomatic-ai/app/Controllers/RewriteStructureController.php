<?php

namespace OtomaticAi\Controllers;

use Exception;
use OtomaticAi\Models\Preset;
use OtomaticAi\Utils\Language;
use OtomaticAi\Vendors\Illuminate\Support\Arr;
use OtomaticAi\Vendors\Illuminate\Support\Str;

class RewriteStructureController extends Controller
{
    public function __invoke()
    {
        $this->verifyNonce();

        $this->validate([
            "title" => ["required", "string"],
            "language" => ["required", "string"],
        ]);

        try {
            // get the openai preset
            $preset = Preset::findFromAPI("rewrite_subtitle_openai_gpt_3_5_turbo");

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
                $this->response([
                    "title" => $content,
                ]);
            }
        } catch (Exception $e) {
            $this->response(["message" => "An error occurred", "error" => $e->getMessage()], 503);
        }

        $this->response([
            "title" => $this->input('title'),
        ]);
    }
}
