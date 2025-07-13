<?php

namespace OtomaticAi\Modules;

use Exception;
use OtomaticAi\Models\Preset;
use OtomaticAi\Models\Publication;
use OtomaticAi\Modules\Contracts\Module as ModuleContract;
use OtomaticAi\Vendors\Illuminate\Support\Arr;

class ProcessCustomFieldsModule implements ModuleContract
{
    /**
     * The publication
     *
     * @var Publication
     */
    private Publication $publication;

    /**
     * Create a new job instance.
     *
     * @param Publication $publication
     */
    public function __construct(Publication $publication)
    {
        $this->publication = $publication;
    }

    /**
     * Execute the job.
     * 
     * @return void
     * @throws Exception
     */
    public function handle(): void
    {
        // verify that the job is runnable
        if (!self::isRunnable($this->publication)) {
            return;
        }

        $items = [];
        foreach (Arr::get($this->publication->project->modules, 'wordpress.custom_fields', []) as $customField) {
            $key = Arr::get($customField, "key");
            $value = Arr::get($customField, "value");

            if (empty($key)) {
                continue;
            }

            if (Arr::get($customField, "is_prompt", false)) {
                if (empty($value)) {
                    continue;
                }

                try {
                    $preset = Preset::make([
                        "model" => 'gpt-3.5-turbo',
                        "messages" => [
                            [
                                "role" => "user",
                                "content" => $value,
                            ]
                        ],
                    ]);

                    // run the preset
                    $response = $preset->process([
                        "language" => $this->publication->project->language->value,
                        "request" => $this->publication->generation_title,
                    ]);

                    // get the response content
                    $value = Arr::get($response, 'choices.0.message.content');
                } catch (Exception $e) {
                    continue;
                }
            }

            $items[] = [
                "key" =>  $key,
                "value" =>  $value,
            ];
        }

        // add custom fielfs to extras
        if (count($items) > 0) {
            $extras = $this->publication->extras;
            $extras["custom_fields"] = $items;
            $this->publication->extras = $extras;
        }
    }

    /**
     * Determine if the module is enabled
     *
     * @param Publication $publication
     * @return boolean
     */
    static public function isEnabled(Publication $publication): bool
    {
        return count(Arr::get($publication->project->modules, 'wordpress.custom_fields', [])) > 0;
    }

    /**
     * Determine if the module is runnable
     *
     * @param Publication $publication
     * @return boolean
     */
    static public function isRunnable(Publication $publication): bool
    {
        // must have custom fields
        // publication sections must not be empty
        return self::isEnabled($publication) && $publication->sections->isNotEmpty();
    }
}
