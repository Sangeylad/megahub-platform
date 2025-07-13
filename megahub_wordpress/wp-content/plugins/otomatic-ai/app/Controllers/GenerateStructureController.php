<?php

namespace OtomaticAi\Controllers;

use OtomaticAi\Models\Preset;
use OtomaticAi\Utils\Language;
use OtomaticAi\Vendors\Illuminate\Support\Arr;
use OtomaticAi\Vendors\Illuminate\Support\Str;

class GenerateStructureController extends Controller
{
    public function generateStructure()
    {
        $this->verifyNonce();

        $this->validate([
            "title" => ["required", "string"],
            "language" => ["required", "string"],
            "length" => ["nullable", "string"],
            "h2_length" => ["nullable", "integer", "min:0"],
            "h3_length" => ["nullable", "integer", "min:0"],
        ]);

        $structure = [];

        // get the openai preset
        $preset = Preset::findFromAPI("structure_v3_openai_gpt_3_5_turbo");

        // get the length
        $h2Length = 7;
        $h3Length = 3;
        switch ($this->input('length', ' medium')) {
            case "short":
                $h2Length = 2;
                $h3Length = 3;
                break;
            case "medium":
                $h2Length = 4;
                $h3Length = 3;
                break;
            case "long":
                $h2Length = 6;
                $h3Length = 3;
                break;
            case "custom":
                $h2Length = $this->input("h2_length", 7);
                $h3Length = $this->input("h3_length", 3);
                break;
        }

        // run the preset
        $response = $preset->process([
            "language" =>  Language::find($this->input('language', ' en'))->value,
            "title" => $this->input('title'),
            "h2_length" => $h2Length,
            "h3_length" => $h3Length,
        ]);

        // get the response content
        $structure = json_decode(Arr::get($response, 'choices.0.message.content'), true, 512, JSON_THROW_ON_ERROR);
        $this->response(Arr::get($structure, "sections", []));
    }

    public function generateH2()
    {
        $this->validate([
            "title" => ["required", "string"],
            "language" => ["required", "string"],
            "length" => ["nullable", "string"],
            "h2_list" => ["nullable", "array"],
            "h3_length" => ["nullable", "integer"],
        ]);

        // get the length
        $h3Length = 3;
        switch ($this->input('length', ' medium')) {
            case "short":
                $h3Length = 3;
                break;
            case "medium":
                $h3Length = 3;
                break;
            case "long":
                $h3Length = 3;
                break;
            case "custom":
                $h3Length = $this->input("h3_length", 3);
                break;
        }

        // get the openai preset
        $preset = Preset::findFromAPI("generate_h2_openai_gpt_3_5_turbo");

        // run the preset
        $response = $preset->process([
            "language" =>  Language::find($this->input('language', ' en'))->value,
            "title" => $this->input('title'),
            "h2_list" => implode("\n", $this->input("h2_list", [])),
            "h3_length" => $h3Length,
        ]);

        // get the response content
        $structure = json_decode(Arr::get($response, 'choices.0.message.content'), true, 512, JSON_THROW_ON_ERROR);

        if (!empty(Arr::get($structure, "sections", []))) {
            $sections = Arr::get($structure, "sections");
            $this->response(Arr::isList($sections) ? Arr::get($sections, 0, []) : $sections);
        }

        $this->response(Arr::get($structure, "section", []));
    }

    public function generateH3()
    {
        $this->validate([
            "title" => ["required", "string"],
            "language" => ["required", "string"],
            "h2_title" => ["required", "string"],
            "h3_list" => ["nullable", "array"],
        ]);

        // get the openai preset
        $preset = Preset::findFromAPI("generate_h3_openai_gpt_3_5_turbo");

        // run the preset
        $response = $preset->process([
            "language" =>  Language::find($this->input('language', ' en'))->value,
            "title" => $this->input('title'),
            "h2_title" => $this->input('h2_title'),
            "h3_list" => implode("\n", $this->input("h3_list", [])),
        ]);

        // get the response content
        $response = json_decode(Arr::get($response, 'choices.0.message.content'), true, 512, JSON_THROW_ON_ERROR);

        $this->response($response);
    }
}
