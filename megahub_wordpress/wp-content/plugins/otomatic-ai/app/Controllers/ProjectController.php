<?php

namespace OtomaticAi\Controllers;

use Exception;
use OtomaticAi\Models\Persona;
use OtomaticAi\Models\Project;
use OtomaticAi\Models\Publication;
use OtomaticAi\Utils\Auth;
use OtomaticAi\Utils\Planning;
use OtomaticAi\Utils\RSS\Reader;
use OtomaticAi\Vendors\Carbon\Carbon;
use OtomaticAi\Vendors\Illuminate\Support\Arr;
use OtomaticAi\Vendors\Illuminate\Support\Collection;
use OtomaticAi\Vendors\Illuminate\Validation\Rule;

class ProjectController extends Controller
{
    public function index()
    {
        $this->verifyNonce();

        $this->validate([
            "page" => ["nullable", "integer"],
            "sort_order" => ["nullable", "string"],
            "sort_direction" => ["nullable", "string", Rule::in(["asc", "desc"])],
            "search" => ["nullable", "string"],
        ]);

        $projects = $this->makeQuery();
        $projects->with(["persona"]);
        $projects = $projects->paginate(25, ['*'], 'page', $this->input('page', 1))->onEachSide(1);

        $this->response($projects);
    }

    public function show()
    {
        $this->verifyNonce();

        $this->validate([
            "id" => ["required"],
        ]);

        $project = Project::find($this->input("id"));

        if ($project === null) {
            $this->response(["message" => "An error occurred", "error" => "Unable to find the project #" . $this->input("id") . "."], 503);
        }

        $this->response($project);
    }

    public function store()
    {
        $this->verifyNonce();

        $this->validateName();
        $this->validateLanguage();
        $this->validatePersona();
        $this->validateType();
        $this->validateRequests();
        $this->validatePlanning();

        $validatedModules = $this->validateModules();

        // create the project
        $project = new Project([
            "name" => $this->input("name", "new project"),
            "language" => $this->input("language"),
            "type" => $this->input("type"),
            "enabled" => true,
            "modules" =>  Arr::get($validatedModules, "modules", []),
            "planning" => $this->input("planning", []),
        ]);

        if (!empty($this->input("persona_id"))) {
            $persona = Persona::find($this->input("persona_id"));
            if ($persona) {
                $project->persona()->associate($persona);
            }
        }
        $project->save();

        // create publications and store
        $requests = $this->input("requests", []);

        // flatten requests
        $requests = $this->flattenRequests($requests);

        if (count($requests) > 0) {
            if ($this->input("planning.per_day", 1) === 0) {

                foreach ($requests as $key => $request) {
                    $key = strval($request["key"]);
                    $parentKey = isset($request["parent_key"]) ? strval($request["parent_key"]) : '';

                    // create a new publication
                    $publication = new Publication([
                        "title" => $request["title"],
                        "meta" => Arr::get($request, "meta", []),
                        "published_at" => Carbon::now(),
                    ]);

                    // attache the project to publication
                    $publication->project()->associate($project);

                    // get the parent publication and attach it if exist
                    $parentPublication = Arr::get($requests, $parentKey . ".publication");
                    if ($parentPublication) {
                        $publication->parent()->associate($parentPublication);
                    }

                    // save the publication
                    $publication->save();
                    $requests[$key]["publication"] = $publication;
                }
            } else {
                $planning = new Planning($requests);
                $planning
                    ->perDay($this->input("planning.per_day", 1))
                    ->startTime($this->input("planning.start_time.hours", 6),  $this->input("planning.start_time.minutes", 30))
                    ->endTime($this->input("planning.end_time.hours", 21),  $this->input("planning.end_time.minutes", 0))
                    ->weekdays($this->input("planning.days", [Planning::MONDAY, Planning::THURSDAY, Planning::WEDNESDAY, Planning::THURSDAY, Planning::FRIDAY]))
                    ->each(function ($request, $date) use ($project, &$requests) {

                        // create a new publication
                        $publication = new Publication([
                            "title" => $request["title"],
                            "meta" => Arr::get($request, "meta", []),
                            "published_at" => $date,
                        ]);

                        // attache the project to publication
                        $publication->project()->associate($project);

                        // get the parent publication and attach it if exist
                        $parentPublication = Arr::get($requests, Arr::get($request, "parent_key") . ".publication");
                        if ($parentPublication) {
                            $publication->parent()->associate($parentPublication);
                        }

                        // save the publication
                        $publication->save();
                        $requests[$request["key"]]["publication"] = $publication;
                    });
            }
        }

        $this->response($project);
    }

    public function update()
    {
        $this->verifyNonce();
        $this->validate([
            "id" => ["required"],
        ]);
        $this->validateName();
        $this->validateLanguage();
        $this->validatePersona();

        $validatedModules = $this->validateModules();

        // get the project
        $project = Project::find($this->input("id"));
        $project->name = $this->input("name");
        $project->language = $this->input("language");

        if (!empty($this->input("persona_id")) && !empty($persona = Persona::find($this->input("persona_id")))) {
            $project->persona()->associate($persona);
        } else {
            $project->persona()->dissociate();
        }

        $project->modules = Arr::get($validatedModules, "modules", []);

        if ($project->save()) {
            $this->emptyResponse();
        } else {
            $this->response(["message" => "An error occurred", "error" => "Unable to update the project."], 503);
        }
    }

    private function flattenRequests($requests, $parentKey = null)
    {
        $output = [];
        for ($i = 0; $i < count($requests); $i++) {
            $copy = $requests[$i];
            unset($copy["children"]);
            $localKey = $parentKey !== null ? $parentKey . '-' . ($i + 1) : ($i + 1);
            $copy["key"] = $localKey;
            if ($parentKey !== null) {
                $copy["parent_key"] = $parentKey;
            }

            $output[] = $copy;
            if (!empty($requests[$i]["children"])) {
                $output = array_merge($output, $this->flattenRequests($requests[$i]["children"], $localKey));
            }
        }

        return (new Collection($output))->keyBy('key')->toArray();
    }

    public function validateRequestsKeywordStep()
    {
        $this->verifyNonce();

        if ($this->input("type") === "rss" || $this->input("type") === "rss-now") {
            $feed = $this->input("modules.autopilot.query");

            if (!empty($feed)) {
                try {
                    Reader::load($feed);
                    $this->emptyResponse();
                } catch (Exception $e) {
                }
            }

            $this->response(["message" => "Unable to load feed.", "errors" => ['modules.autopilot.query' => ["Unable to load feed."]]], 422);
        }

        $this->emptyResponse();
    }

    public function validateRequestsStep()
    {
        $this->verifyNonce();

        $this->validateRequests();

        $this->emptyResponse();
    }

    public function validateContentStep()
    {
        $this->verifyNonce();

        $this->validateTextModule();
        $this->validatePersona();
        $this->validateImageModule();
        $this->validateVideoModule();
        $this->validateFacebookModule();
        $this->validateInstagramModule();
        $this->validateTwitterModule();
        $this->validateTiktokModule();
        $this->validateWordpressModule();

        $this->emptyResponse();
    }

    public function validatePlanningStep()
    {
        $this->verifyNonce();

        $this->validatePlanning();

        $this->emptyResponse();
    }

    public function enable()
    {
        $this->verifyNonce();

        $this->validate([
            "project" => ["required", "integer"],
        ]);

        $project = Project::find($this->input('project'));
        if ($project) {
            $project->enabled = true;
            $project->save();
        }

        $this->emptyResponse();
    }

    public function disable()
    {
        $this->verifyNonce();

        $this->validate([
            "project" => ["required", "integer"],
        ]);

        $project = Project::find($this->input('project'));
        if ($project) {
            $project->enabled = false;
            $project->save();
        }

        $this->emptyResponse();
    }

    public function destroy()
    {
        $this->verifyNonce();

        $this->validate([
            "project" => ["required", "integer"],
        ]);

        $project = Project::find($this->input('project'));
        if ($project) {
            $project->delete();
        }

        $this->emptyResponse();
    }

    private function makeQuery()
    {
        $projects = Project::query();

        // sort 
        if (!empty($sortOrder = $this->input('sort_order', ''))) {
            $projects->orderBy($sortOrder, $this->input('sort_direction', 'desc'));
        } else {
            $projects->orderBy("id", "desc");
        }

        if (!empty($type = $this->input('type', ''))) {
            $projects->where("type", $type);
        }
        if (($enabled = $this->input('enabled', null)) !== null) {
            $projects->where("enabled", $enabled);
        }

        return $projects;
    }

    // validators
    private function validateName()
    {
        $this->validate([
            "name" => ["required", "string"],
        ]);
    }

    private function validateLanguage()
    {
        $this->validate([
            "language" => ["required", "string"],
        ]);
    }

    private function validatePersona()
    {
        $this->validate([
            "persona_id" => ["nullable"],
        ]);
    }

    private function validateType()
    {
        $this->validate([
            "type" => ["required"],
        ]);
    }

    private function validateRequests()
    {
        $this->validate([
            "requests" => ["required_unless:type,rss,news", "array"],
        ]);
    }

    private function validateModules()
    {
        $rules = array_merge_recursive(
            $this->getTextModuleRules(),
            $this->getImageModuleRules(),
            $this->getVideoModuleRules(),
            $this->getFacebookModuleRules(),
            $this->getInstagramModuleRules(),
            $this->getTwitterModuleRules(),
            $this->getTiktokModuleRules(),
            $this->getWordpressModuleRules(),
            $this->getAutopilotModuleRules(),
        );

        return $this->validate($rules["rules"], [], $rules["custom_attributes"]);
    }

    // validation rules
    private function getTextModuleRules()
    {
        return [
            "rules" => [
                "modules.text.enabled" => ["boolean"],
                "modules.text.model" => ["required"],
                "modules.text.custom_preset.enabled" => ["boolean"],
                "modules.text.custom_preset.prompt" => ["nullable", "string"],
                "modules.text.custom_preset.temperature" => ["numeric", "min:0.01", "max:1"],
                "modules.text.custom_preset.top_p" => ["numeric", "min:0.01", "max:1"],
                "modules.text.custom_preset.presence_penalty" => ["numeric", "min:-2", "max:2"],
                "modules.text.custom_preset.frequency_penalty" => ["numeric", "min:-2", "max:2"],
                "modules.text.buyer_persona.description" => ["nullable", "string"],
                "modules.text.custom_instructions" => ["nullable", "string"],
                "modules.text.writing_style" => ["nullable", "string"],
                "modules.text.external_links.enabled" => ["boolean"],
                "modules.text.length" => ["required"],
                "modules.text.h2_length" => ["nullable", "integer", "min:0"],
                "modules.text.h3_length" => ["nullable", "integer", "min:0"],
                "modules.text.structure" => ["array"],
                "modules.text.sources.enabled" => ["boolean"],
                "modules.text.sources.is_follow" => ["boolean"],
                "modules.text.options.table.enabled" => ["boolean"],
                "modules.text.options.list.enabled" => ["boolean"],
                "modules.text.options.faq.enabled" => ["boolean"],
                "modules.text.options.introduction.enabled" => ["boolean"],
                "modules.text.options.brief.enabled" => ["boolean"],
                "modules.text.options.summary.enabled" => ["boolean"],
                "modules.text.options.bold_words.enabled" => ["boolean"],
            ],
            "custom_attributes" => [
                "modules.text.model" => "AI model",
                "modules.text.custom_preset.prompt" => "prompt",
                "modules.text.custom_preset.temperature" => "temperature",
                "modules.text.custom_preset.top_p" => "Top P",
                "modules.text.custom_preset.presence_penalty" => "presence penalty",
                "modules.text.custom_preset.frequency_penalty" => "frequency penalty",
                "modules.text.buyer_persona.description" => "Buyer Persona",
                "modules.text.custom_instructions" => "custom instructions",
                "modules.text.writing_style" => "writing style",
                "modules.text.length" => "Text length",
                "modules.text.structure" => "Structure",
                "modules.text.sources.enabled" => "sources",
                "modules.text.sources.is_follow" => "Is Follow",
                "modules.text.options.table.enabled" => "table",
                "modules.text.options.faq.enabled" => "FAQ",
                "modules.text.options.introduction.enabled" => "introduction",
                "modules.text.options.brief.enabled" => "brief",
                "modules.text.options.summary.enabled" => "summary",
                "modules.text.options.bold_words.enabled" => "bold words",
            ]
        ];
    }

    private function getImageModuleRules()
    {
        return [
            "rules" => [
                "modules.image.service" => ["string", "required"],
                "modules.image.thumbnail.enabled" => ["boolean"],
                "modules.image.content.enabled" => ["boolean"],
                "modules.image.content.length" => ["exclude_if:modules.image.content.enabled,false", "integer", "min:1", "max:10"],
                "modules.image.custom_instructions" => ["nullable", "string"],
                "modules.image.copyright.enabled" => ["boolean"],
                "modules.image.settings.stable_diffusion.style_preset" => ["nullable"],
                "modules.image.settings.stable_diffusion.model" => ["required_if:modules.image.service,stable_diffusion", "string"],
                "modules.image.settings.dall_e.model" => ["required_if:modules.image.service,dall_e", "string"],
                "modules.image.settings.dall_e.quality" => ["required_if:modules.image.service,dall_e", "string"],
            ],
            "custom_attributes" => [
                'modules.image.service' => 'service',
                'modules.image.thumbnail.enabled' => 'thumbnail image',
                'modules.image.content.enabled' => 'content images',
                'modules.image.content.length' => 'number of images',
                "modules.image.custom_instructions" => 'custom instructions',
                'modules.image.copyright.enabled' => 'copyright',
                'modules.image.settings.stable_diffusion.style_preset' => 'style preset',
                'modules.image.settings.stable_diffusion.model' => 'model',
                'modules.image.settings.dall_e.model' => 'model',
                'modules.image.settings.dall_e.quality' => 'quality',
            ]
        ];
    }

    private function getVideoModuleRules()
    {
        return [
            "rules" => [
                "modules.video.service" => ["string", "required"],
                "modules.video.enabled" => ["boolean"],
                "modules.video.position" => ["exclude_if:modules.video.enabled,false", Rule::in(['top', 'middle', 'bottom', 'random'])],
            ],
            "custom_attributes" => [
                "modules.video.service" => 'service',
                "modules.video.enabled" => 'video',
                "modules.video.position" => 'position',
            ]
        ];
    }

    private function getFacebookModuleRules()
    {
        return [
            "rules" => [
                "modules.facebook.enabled" => ["boolean"],
                "modules.facebook.length" => ["exclude_if:modules.facebook.enabled,false", "integer", "min:1", "max:5"],
                "modules.facebook.position" => ["exclude_if:modules.facebook.enabled,false", Rule::in(['top', 'middle', 'bottom', 'random'])],
            ],
            "custom_attributes" => [
                "modules.facebook.length" => 'number of posts',
                "modules.facebook.position" => 'position',
            ]
        ];
    }

    private function getInstagramModuleRules()
    {
        return [
            "rules" => [
                "modules.instagram.enabled" => ["boolean"],
                "modules.instagram.length" => ["exclude_if:modules.instagram.enabled,false", "integer", "min:1", "max:5"],
                "modules.instagram.position" => ["exclude_if:modules.instagram.enabled,false", Rule::in(['top', 'middle', 'bottom', 'random'])],
            ],
            "custom_attributes" => [
                "modules.instagram.length" => 'number of posts',
                "modules.instagram.position" => 'position',
            ]
        ];
    }

    private function getTwitterModuleRules()
    {
        return [
            "rules" => [
                "modules.twitter.enabled" => ["boolean"],
                "modules.twitter.length" => ["exclude_if:modules.twitter.enabled,false", "integer", "min:1", "max:5"],
                "modules.twitter.position" => ["exclude_if:modules.twitter.enabled,false", Rule::in(['top', 'middle', 'bottom', 'random'])],
            ],
            "custom_attributes" => [
                "modules.twitter.length" => 'number of posts',
                "modules.twitter.position" => 'position',
            ]
        ];
    }

    private function getTiktokModuleRules()
    {
        return [
            "rules" => [
                "modules.tiktok.enabled" => ["boolean"],
                "modules.tiktok.length" => ["exclude_if:modules.tiktok.enabled,false", "integer", "min:1", "max:5"],
                "modules.tiktok.position" => ["exclude_if:modules.tiktok.enabled,false", Rule::in(['top', 'middle', 'bottom', 'random'])],
            ],
            "custom_attributes" => [
                "modules.tiktok.length" => 'number of posts',
                "modules.tiktok.position" => 'position',
            ]
        ];
    }

    private function getWordpressModuleRules()
    {
        return [
            "rules" => [
                "modules.wordpress.post_type" => ["required", "string"],
                "modules.wordpress.author_id" => ["nullable"],
                "modules.wordpress.template" => ["nullable", "string"],
                "modules.wordpress.parent_page_id" => ["nullable"],
                "modules.wordpress.categories.automatic.enabled" => ["boolean"],
                "modules.wordpress.categories.custom" => ["array"],
                "modules.wordpress.tags.automatic.enabled" => ["boolean"],
                "modules.wordpress.tags.custom" => ["array"],
                "modules.wordpress.status" => ["string", "required"],
                "modules.wordpress.yoast_seo.title.enabled" => ["boolean"],
                "modules.wordpress.yoast_seo.title.emojis.enabled" => ["boolean"],
                "modules.wordpress.yoast_seo.description.enabled" => ["boolean"],
                "modules.wordpress.rank_math.title.enabled" => ["boolean"],
                "modules.wordpress.rank_math.title.emojis.enabled" => ["boolean"],
                "modules.wordpress.rank_math.description.enabled" => ["boolean"],
                "modules.wordpress.custom_fields" => ["array"],
            ],
            "custom_attributes" => [
                "modules.wordpress.post_type" => "post type",
                "modules.wordpress.author_id" => "author",
                "modules.wordpress.template" => "page template",
                "modules.wordpress.parent_page_id" => "parent page ID",
                "modules.wordpress.categories.automatic.enabled" => "automatic category",
                "modules.wordpress.categories.custom" => "categories",
                "modules.wordpress.tags.automatic.enabled" => "automatic tags",
                "modules.wordpress.tags.custom" => "tags",
                "modules.wordpress.status" => "post status",
                "modules.wordpress.yoast_seo.title.enabled" => "Yoast SEO title",
                "modules.wordpress.yoast_seo.title.emojis.enabled" => "emojis",
                "modules.wordpress.yoast_seo.description.enabled" => "Yoast SEO description",
                "modules.wordpress.rank_math.title.enabled" => "Rank Math title",
                "modules.wordpress.rank_math.title.emojis.enabled" => "emojis",
                "modules.wordpress.rank_math.description.enabled" => "Rank Math description",
                "modules.wordpress.custom_fields" => "custom fields",
            ]
        ];
    }

    private function getAutopilotModuleRules()
    {
        return [
            "rules" => [
                "modules.autopilot.query" => ["nullable", "string"],
                "modules.autopilot.planning.per_day" => ["integer", "min:0"],
                "modules.autopilot.planning.start_time.hours" => ["integer", "min:0", "max:23"],
                "modules.autopilot.planning.start_time.minutes" => ["integer", "min:0", "max:59"],
                "modules.autopilot.planning.end_time.hours" => ["integer", "min:0", "max:23"],
                "modules.autopilot.planning.end_time.minutes" => ["integer", "min:0", "max:59"],
            ],
            "custom_attributes" => [
                "modules.autopilot.query" => 'query',
                "modules.autopilot.planning.per_day" => 'number of posts per day',
            ]
        ];
    }

    // ----

    private function validateTextModule()
    {
        $rules = $this->getTextModuleRules();
        $this->validate($rules["rules"], [], $rules["custom_attributes"]);
    }

    private function validateImageModule()
    {
        $rules = $this->getImageModuleRules();
        $this->validate($rules["rules"], [], $rules["custom_attributes"]);
    }

    private function validateVideoModule()
    {
        $rules = $this->getVideoModuleRules();
        $this->validate($rules["rules"], [], $rules["custom_attributes"]);
    }

    private function validateFacebookModule()
    {
        $rules = $this->getFacebookModuleRules();
        $this->validate($rules["rules"], [], $rules["custom_attributes"]);
    }

    private function validateInstagramModule()
    {
        $rules = $this->getInstagramModuleRules();
        $this->validate($rules["rules"], [], $rules["custom_attributes"]);
    }

    private function validateTwitterModule()
    {
        $rules = $this->getTwitterModuleRules();
        $this->validate($rules["rules"], [], $rules["custom_attributes"]);
    }

    private function validateTiktokModule()
    {
        $rules = $this->getTiktokModuleRules();
        $this->validate($rules["rules"], [], $rules["custom_attributes"]);
    }

    private function validateWordpressModule()
    {
        $rules = $this->getWordpressModuleRules();
        $this->validate($rules["rules"], [], $rules["custom_attributes"]);
    }

    private function validatePlanning()
    {
        $this->validate([
            "planning.days.monday" => ["boolean"],
            "planning.days.tuesday" => ["boolean"],
            "planning.days.wednesday" => ["boolean"],
            "planning.days.thursday" => ["boolean"],
            "planning.days.friday" => ["boolean"],
            "planning.days.saturday" => ["boolean"],
            "planning.days.sunday" => ["boolean"],
            "planning.per_day" => ["integer", "min:0"],
            "planning.start_time.hours" => ["integer", "min:0", "max:23"],
            "planning.start_time.minutes" => ["integer", "min:0", "max:59"],
            "planning.end_time.hours" => ["integer", "min:0", "max:23"],
            "planning.end_time.minutes" => ["integer", "min:0", "max:59"],
        ]);
    }
}
