<?php

namespace OtomaticAi\Controllers;

use OtomaticAi\Models\Preset;
use OtomaticAi\Vendors\Illuminate\Validation\Rule;

class PresetController extends Controller
{
    public function index()
    {
        $this->verifyNonce();

        $this->validate([
            "sort_order" => ["nullable", "string"],
            "sort_direction" => ["nullable", "string", Rule::in(["asc", "desc"])],
        ]);

        $presets = $this->makeQuery();
        $presets = $presets->get();

        $this->response($presets);
    }

    public function show()
    {
        $this->verifyNonce();

        $this->validate([
            "id" => ["required"],
        ]);

        $preset = Preset::find($this->input("id"));

        if ($preset === null) {
            $this->response(["message" => "An error occurred", "error" => "Unable to find the prompt #" . $this->input("id") . "."], 503);
        }

        $this->response($preset);
    }

    public function store()
    {
        $this->verifyNonce();

        $this->validate([
            "name" => ["required", "string", "max:255"],
            "model" => ["required"],
            "messages.0.content" => ["nullable", "string"],
            "messages.1.content" => ["nullable", "string"],
            "temperature" => ["numeric", "min:0.01", "max:1"],
            "top_p" => ["numeric", "min:0.01", "max:1"],
            "presence_penalty" => ["numeric", "min:-2", "max:2"],
            "frequency_penalty" => ["numeric", "min:-2", "max:2"],
        ]);

        // create the preset
        $preset = new Preset;
        $preset->name = $this->input("name");
        $preset->model = $this->input("model");
        $preset->messages = $this->input("messages");
        $preset->temperature = $this->input("temperature", 1);
        $preset->top_p = $this->input("top_p", 1);
        $preset->presence_penalty = $this->input("presence_penalty", 0);
        $preset->frequency_penalty = $this->input("frequency_penalty", 0);

        if ($preset->save()) {
            $this->emptyResponse();
        } else {
            $this->response(["message" => "An error occurred", "error" => "Unable to save the new prompt."], 503);
        }
    }

    public function update()
    {
        $this->verifyNonce();

        $this->validate([
            "id" => ["required"],
            "name" => ["required", "string", "max:255"],
            "model" => ["required"],
            "messages.0.content" => ["nullable", "string"],
            "messages.1.content" => ["nullable", "string"],
            "temperature" => ["numeric", "min:0.01", "max:1"],
            "top_p" => ["numeric", "min:0.01", "max:1"],
            "presence_penalty" => ["numeric", "min:-2", "max:2"],
            "frequency_penalty" => ["numeric", "min:-2", "max:2"],
        ]);

        // get the preset
        $preset = Preset::find($this->input("id"));

        if ($preset === null) {
            $this->response(["message" => "An error occurred", "error" => "Unable to find the prompt #" . $this->input("id") . "."], 503);
        }

        // update the preset
        $preset->name = $this->input("name");
        $preset->model = $this->input("model");
        $preset->messages = $this->input("messages");
        $preset->temperature = $this->input("temperature", 1);
        $preset->top_p = $this->input("top_p", 1);
        $preset->presence_penalty = $this->input("presence_penalty", 0);
        $preset->frequency_penalty = $this->input("frequency_penalty", 0);

        if ($preset->save()) {
            $this->emptyResponse();
        } else {
            $this->response(["message" => "An error occurred", "error" => "Unable to update the prompt."], 503);
        }
    }

    public function destroy()
    {
        $this->verifyNonce();

        $this->validate([
            "preset" => ["required", "integer"],
        ]);

        $preset = Preset::find($this->input('preset'));
        if ($preset) {
            $preset->delete();
        }

        $this->emptyResponse();
    }

    private function makeQuery()
    {
        $presets = Preset::query();

        // sort 
        if (!empty($sortOrder = $this->input('sort_order', ''))) {
            $presets->orderBy($sortOrder, $this->input('sort_direction', 'desc'));
        } else {
            $presets->orderBy("id", "desc");
        }

        return $presets;
    }
}
