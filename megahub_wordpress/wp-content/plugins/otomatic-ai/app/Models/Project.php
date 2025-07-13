<?php

namespace OtomaticAi\Models;

use OtomaticAi\Casts\Language;
use OtomaticAi\Utils\Auth;
use OtomaticAi\Utils\Settings;
use OtomaticAi\Vendors\Illuminate\Database\Eloquent\Model;
use OtomaticAi\Vendors\Illuminate\Support\Arr;
use OtomaticAi\Vendors\Illuminate\Database\Eloquent\Builder;

class Project extends Model
{
    protected $fillable = ["name", "language", "type", "enabled", "input", "modules", "planning"];

    /**
     * The accessors to append to the model's array form.
     *
     * @var array
     */
    protected $appends = [
        'is_complete',
    ];

    protected $casts = [
        'language' => Language::class,
        'enabled' => 'boolean',
        'input' => 'array',
        'modules' => 'array',
        'planning' => 'array',
        'metrics' => 'array',
    ];

    /**
     * Create a new Eloquent model instance.
     *
     * @param  array  $attributes
     * @return void
     */
    public function __construct(array $attributes = [])
    {
        global $wpdb;

        $this->table = $wpdb->prefix . 'otomatic_ai_projects';
        parent::__construct($attributes);
    }

    /**
     * Get the publications for the project.
     */
    public function publications()
    {
        return $this->hasMany(Publication::class);
    }

    /**
     * Get the persona that owns the project.
     */
    public function persona()
    {
        return $this->belongsTo(Persona::class);
    }

    /**
     * Indicate if the project has publish all his publication
     */
    public function getIsCompleteAttribute()
    {
        return Arr::get($this->metrics, 'idle', 0) + Arr::get($this->metrics, 'pending', 0) === 0;
    }

    public function getModulesAttribute()
    {
        $oldModules = json_decode($this->attributes["modules"], true);
        $newModules = array_replace_recursive([
            "text" => [
                "enabled" => true,
                "model" => "gpt-3.5-turbo",
                "custom_preset" => [
                    "enabled" => false,
                    "prompt" => null,
                    "temperature" => 1,
                    "top_p" => 1,
                    "presence_penalty" => 0,
                    "frequency_penality" => 0,
                ],
                "buyer_persona" => [
                    "description" => null
                ],
                "custom_instructions" => null,
                "writing_style" => null,
                "external_links" => [
                    "enabled" => false,
                ],
                "length" => "long",
                "h2_length" => 3,
                "h3_length" => 3,
                "sources" => [
                    "enabled" => false,
                    "is_follow" => false,
                ],
                "structure" => [],
                "options" => [
                    "table" => [
                        "enabled" => false,
                    ],
                    "list" => [
                        "enabled" => false,
                    ],
                    "faq" => [
                        "enabled" => false,
                    ],
                    "introduction" => [
                        "enabled" => true,
                    ],
                    "brief" => [
                        "enabled" => false,
                    ],
                    "summary" => [
                        "enabled" => false,
                    ],
                    "bold_words" => [
                        "enabled" => true,
                    ],
                ]
            ],
            "image" => [
                "service" => "dall_e",
                "thumbnail" => [
                    "enabled" => true,
                ],
                "content" => [
                    "enabled" => false,
                    "length" => 3,
                ],
                "copyright" => [
                    "enabled" => false,
                ],
                "custom_instructions" => null,
                "settings" => [
                    "stable_diffusion" => [
                        "style_preset" => "",
                        "model" => "stable_image_core"
                    ],
                    "dall_e" => [
                        "model" => "dall-e-3",
                        "quality" => "standard",
                    ],
                    "unsplash" => [],
                ],
            ],
            "video" => [
                "service" => "youtube",
                "enabled" => false,
                "position" => "top",
            ],
            "facebook" => [
                "enabled" => false,
                "length" => 1,
                "position" => "middle",
            ],
            "twitter" => [
                "enabled" => false,
                "length" => 1,
                "position" => "middle",
            ],
            "instagram" => [
                "enabled" => false,
                "length" => 1,
                "position" => "middle",
            ],
            "tiktok" => [
                "enabled" => false,
                "length" => 1,
                "position" => "middle",
            ],
            "wordpress" => [
                "post_type" => "post",
                "author_id" => null,
                "parent_page_id" => null,
                "categories" => [],
                "tags" => [
                    "automatic" => [
                        "enabled" => false,
                    ],
                    "custom" => [],
                ],
                "template" => null,
                "status" => "publish",
                "yoast_seo" => [
                    "title" => [
                        "enabled" => false,
                        "emojis" => [
                            "enabled" => false
                        ]
                    ],
                    "description" => [
                        "enabled" => false,
                    ],
                ],
                "rank_math" => [
                    "title" => [
                        "enabled" => false,
                        "emojis" => [
                            "enabled" => false
                        ]
                    ],
                    "description" => [
                        "enabled" => false,
                    ],
                ],
                "custom_fields" => []
            ],
            "autopilot" => [
                "query" => null,
                "planning" => [
                    "per_day" => 1,
                    "start_time" => [
                        "hours" => 0,
                        "minutes" => 0,
                    ],
                    "end_time" => [
                        "hours" => 23,
                        "minutes" => 59,
                    ],
                ]
            ]
        ], $oldModules);

        // ai model
        if (empty(Arr::get($oldModules, "text.model")) && !empty(Settings::get("api.openai.model"))) {
            Arr::set($newModules, "text.model", Settings::get("api.openai.model"));
        }

        // gpt-4-turbo to gpt-4
        if (in_array($this->type, ["news", "rss", "sitemap", "url"]) && Arr::get($newModules, "text.model") === 'gpt-4') {
            Arr::set($newModules, "text.model", "gpt-4-turbo");
        }

        // add automatic categories
        if (Arr::isList($oldModules["wordpress"]["categories"])) {
            $newModules["wordpress"]["categories"] = [
                "automatic" => [
                    "enabled" => false,
                ],
                "custom" => $oldModules["wordpress"]["categories"]
            ];
        }

        // change custom template
        if (Arr::get($oldModules, "text.template") === "custom") {
            $preset = Preset::find(Arr::get($oldModules, "text.settings.custom.preset"));
            if ($preset) {
                Arr::set($newModules, "text.custom_preset", [
                    "enabled" => true,
                    "system" => Arr::get($preset->messages, '0.content'),
                    "user" => Arr::get($preset->messages, '1.content'),
                    "temperature" => $preset->temperature,
                    "top_p" => $preset->top_p,
                    "presence_penalty" => $preset->presence_penalty,
                    "frequency_penality" => $preset->frequency_penality,
                ]);
            }
        }

        // text.settings.structure.h2 -> text.length
        switch (Arr::get($newModules, "text.settings.structure.h2")) {
            case "auto":
                Arr::set($newModules, "text.length", "long");
                break;
            case "1";
                Arr::set($newModules, "text.length", "short");
                break;
            case "2";
                Arr::set($newModules, "text.length", "medium");
                break;
            case "3";
                Arr::set($newModules, "text.length", "medium");
                break;
            case "4";
                Arr::set($newModules, "text.length", "long");
                break;
        }

        // change classic template
        if (Arr::get($oldModules, "text.template") === "classic") {
            Arr::set($newModules, "text.length", "short");
        }

        // disable custom_presets on news
        if ($this->type === 'news') {
            Arr::set($newModules, "text.custom_preset.enabled", false);
        }

        // try to set the wordpress.author_id if is not set and persona is set
        if ($this->persona_id !== null && empty(Arr::get($newModules, "wordpress.author_id"))) {
            $persona = $this->persona;
            if (!empty($persona)) {
                $author = $persona->user;
                if (!empty($author)) {
                    Arr::set($newModules, "wordpress.author_id", $author->ID);
                }
            }
        }

        // format custom_preset
        if (
            Arr::get($newModules, "text.custom_preset.enabled", false) &&
            empty(Arr::get($newModules, "text.custom_preset.prompt"))
            && (!empty(Arr::get($oldModules, 'text.custom_preset.system')) || !empty(Arr::get($oldModules, 'text.custom_preset.user')))
        ) {
            $parts = [
                Arr::get($oldModules, 'text.custom_preset.system'),
                Arr::get($oldModules, 'text.custom_preset.user'),
            ];
            $parts = array_values(array_filter($parts));
            Arr::set($newModules, 'text.custom_preset.prompt', implode("\n\n", $parts));
        }

        // // update free parameters
        // if (!Auth::isPremium()) {
        //     Arr::set($newModules, "text.model", "gpt-3.5-turbo");
        //     Arr::set($newModules, "text.external_links.enabled", false);
        //     if (!in_array(Arr::get($newModules, "text.length"), ["short"])) {
        //         Arr::set($newModules, "text.length", "short");
        //     }
        //     Arr::set($newModules, "text.buyer_persona.description", null);
        //     Arr::set($newModules, "text.custom_instructions", null);
        //     Arr::set($newModules, "image.content.enabled", false);
        //     if (in_array(Arr::get($newModules, "image.service"), ["dall_e", "stable_diffusion"])) {
        //         Arr::set($newModules, "image.service", "unsplash");
        //     }
        //     Arr::set($newModules, "video.enabled", false);
        //     Arr::set($newModules, "facebook.enabled", false);
        //     Arr::set($newModules, "twitter.enabled", false);
        //     Arr::set($newModules, "instagram.enabled", false);
        //     Arr::set($newModules, "tiktok.enabled", false);
        //     Arr::set($newModules, "wordpress.categories.automatic.enabled", false);
        //     Arr::set($newModules, "wordpress.tags.automatic.enabled", false);
        //     Arr::set($newModules, "wordpress.yoast_seo.title.enabled", false);
        //     Arr::set($newModules, "wordpress.yoast_seo.description.enabled", false);
        // }

        return $newModules;
    }

    /**
     * Scope a query to only include completed publications.
     */
    public function scopeCompleted(Builder $query): void
    {
        $query->whereRaw("JSON_UNQUOTE(JSON_EXTRACT(metrics, '$.idle')) = ?", [0])
            ->whereRaw("JSON_UNQUOTE(JSON_EXTRACT(metrics, '$.pending')) = ?", [0]);
    }

    public function refreshMetrics()
    {
        $this->metrics = $this->publications()->toBase()
            ->selectRaw("count(*) as total")
            ->selectRaw("count(IF(status = 'idle', 1, null)) as idle")
            ->selectRaw("count(IF(status = 'pending', 1, null)) as pending")
            ->selectRaw("count(IF(status = 'success', 1, null)) as success")
            ->selectRaw("count(IF(status = 'failed', 1, null)) as failed")
            ->first();
        $this->save();
    }

    public function getFormattedModules()
    {
        $modules = $this->modules;

        // preset
        if (Arr::get($modules, 'text.template') === 'custom') {
            $preset = Preset::find(Arr::get($modules, 'text.settings.custom.preset'));
            if ($preset)
                Arr::set($modules, 'text.settings.custom.preset', Arr::only($preset->toArray(), ['model', 'messages', 'temperature', 'top_p', 'presence_penalty', 'frequency_penalty']));
            else
                Arr::set($modules, 'text.settings.custom.preset', null);
        }

        return $modules;
    }
}
