<?php

namespace OtomaticAi\Controllers;

use OtomaticAi\Models\Project;
use OtomaticAi\Models\Template;
use OtomaticAi\Vendors\Illuminate\Support\Arr;

class TemplateController extends Controller
{
    public function index()
    {
        $this->verifyNonce();

        $this->response(Template::all());
    }

    public function store()
    {
        $this->verifyNonce();

        $validated = $this->validate([
            "name" => ["string", "required"],
            "project" => ["required", "integer"],
        ]);

        $project = Project::find($this->input("project"));

        $payload = [
            "persona_id" => $project->persona_id,
            "modules" => $project->modules,
        ];

        Arr::forget($payload, "modules.text.structure");
        Arr::forget($payload, "modules.text.buyer_persona.description");

        $template = new Template([
            "name" => $validated["name"],
            "plugin_version" => OTOMATIC_AI_VERSION,
            "payload" => $payload,
        ]);

        if ($template->save()) {
            $this->emptyResponse();
        }

        $this->response(["message" => "An error occurred", "error" => "Unable to create the template."], 503);
    }

    public function destroy()
    {
        $this->verifyNonce();

        $this->validate([
            "template" => ["required", "integer"],
        ]);

        $template = Template::find($this->input('template'));
        if ($template) {
            $template->delete();
        }

        $this->emptyResponse();
    }

    public function export()
    {
        $this->verifyNonce();

        $this->validate([
            "template" => ["required", "integer"],
        ]);

        $template = Template::find($this->input('template'));
        if ($template) {

            $payload = $template->payload;

            Arr::forget($payload, 'persona_id');
            Arr::forget($payload, "modules.text.structure");
            Arr::forget($payload, "modules.text.buyer_persona.description");
            Arr::forget($payload, "modules.wordpress.author_id");
            Arr::forget($payload, "modules.wordpress.parent_page_id");
            Arr::forget($payload, "modules.wordpress.categories.custom");

            $data = [
                "name" => $template->name,
                "plugin_version" => $template->plugin_version,
                "payload" => $payload,
            ];

            $data = json_encode($data);
            $data = base64_encode($data);

            $this->response($data);
        }

        $this->emptyResponse();
    }

    public function import()
    {
        $this->verifyNonce();

        $this->validate([
            "import_data" => ["required", "string"],
        ]);

        $data = $this->input("import_data");
        $data = base64_decode($data);
        $data = json_decode($data, true);

        if (!isset($data["name"])) {
            $this->response(["message" => "The import code is invalid", "errors" => ['import_data' => ["The import code is invalid"]]], 422);
        }

        $template = new Template([
            "name" => Arr::get($data, "name", "new template"),
            "plugin_version" => Arr::get($data, "plugin_version", OTOMATIC_AI_VERSION),
            "payload" => Arr::get($data, "payload", []),
        ]);

        $template->save();

        $this->emptyResponse();
    }
}
