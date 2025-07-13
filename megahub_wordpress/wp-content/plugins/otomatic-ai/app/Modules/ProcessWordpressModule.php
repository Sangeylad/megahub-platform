<?php

namespace OtomaticAi\Modules;

use Exception;
use OtomaticAi\Models\Preset;
use OtomaticAi\Models\Publication;
use OtomaticAi\Modules\Contracts\Module as ModuleContract;
use OtomaticAi\Utils\Auth;
use OtomaticAi\Vendors\Illuminate\Support\Arr;
use OtomaticAi\Vendors\Illuminate\Support\Str;

class ProcessWordpressModule implements ModuleContract
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

        // perform automatic tags
        $this->handleAutomaticTags();

        // perform automatic categories
        $this->handleAutomaticCategory();

        // perform yoast title
        $this->handleYoastTitle();

        // perform yoast description
        $this->handleYoastDescription();

        // perform rank math title
        $this->handleRankMathTitle();

        // perform rank math description
        $this->handleRankMathDescription();
    }

    /**
     * Generate automatic tags
     *
     * @return void
     */
    private function handleAutomaticTags(): void
    {
        // verify that the automatic tags are enabled
        if (!self::automaticTagsEnabled($this->publication)) {
            return;
        }

        // log the start of the job
        $this->publication->addLog("Automatic tags module started.");

        try {

            // get the openai preset
            $preset = Preset::findFromAPI('tags');

            // run the preset
            $response = $preset->process([
                "language" => $this->publication->project->language->value,
                "request" => $this->publication->generation_title,
            ]);

            // get the response content
            $response = json_decode(Arr::get($response, 'choices.0.message.content'), true, 512, JSON_THROW_ON_ERROR);
            $items = Arr::get($response, "values");

            if (!empty($items)) {

                // clean tags
                $items = array_map(function ($str) {
                    return Str::clean($str);
                }, $items);
                $items = array_slice($items, 0, 5);
                $items = array_map([Str::class, 'lower'], $items);

                // add tags to extras
                $extras = $this->publication->extras;
                $extras["tags"] =  $items;
                $this->publication->extras = $extras;

                $this->publication->addLog("Automatic tags module completed successfully.", "success");
            } else {
                $this->publication->addLog("Automatic tags module failed. No tags generated.", "warning");
            }
        } catch (Exception $e) {
            $this->publication->addLog("Automatic tags module failed. " . $e->getMessage(), "warning");
        }
    }

    /**
     * Generate automatic category
     *
     * @return void
     */
    private function handleAutomaticCategory(): void
    {
        // verify that the automatic tags are enabled
        if (!self::automaticCategoryEnabled($this->publication)) {
            return;
        }

        // log the start of the job
        $this->publication->addLog("Automatic category module started.");

        try {

            // get categories
            $categories = array_map(function ($cat) {
                return ["id" => $cat->term_id, "name" => $cat->name];
            }, get_categories(['hide_empty' => 0]));
            $categories = Arr::keyBy($categories, 'name');

            // get the openai preset
            $preset = Preset::findFromAPI("automatic_category");

            // run the preset
            $response = $preset->process([
                "language" => $this->publication->project->language->value,
                "categories" => implode(", ", Arr::pluck($categories, "name")),
                "request" => $this->publication->generation_title,
            ]);

            // get the response content
            $response = json_decode(Arr::get($response, 'choices.0.message.content'), true, 512, JSON_THROW_ON_ERROR);
            $category = Arr::get($response, "category");
            if (is_array($category)) {
                $category = Arr::first($category);
            }

            if (isset($categories[$category])) {
                // add category to extras
                $extras = $this->publication->extras;
                $extras["category"] = $categories[$category]["id"];
                $this->publication->extras = $extras;

                $this->publication->addLog("Automatic category module completed successfully.", "success");
            } else {
                $this->publication->addLog("Automatic category module failed. No category found.", "warning");
            }
        } catch (Exception $e) {
            $this->publication->addLog("Automatic category module failed. " . $e->getMessage(), "warning");
        }
    }

    /**
     * Generate a Yoast SEO title
     *
     * @return void
     */
    private function handleYoastTitle(): void
    {
        // verify that the yoast title generation is enabled
        if (!self::yoastTitleEnabled($this->publication)) {
            return;
        }

        // log the start of the job
        $this->publication->addLog("Yoast SEO title module started.");

        try {

            // get the openai preset
            $preset = Preset::findFromAPI('yoast_seo_title_emojis');

            // run the preset
            $response = $preset->process([
                "language" => $this->publication->project->language->value,
                "request" => $this->publication->generation_title,
                "has_emojis" => Arr::get($this->publication->project->modules, "wordpress.yoast_seo.title.emojis.enabled", false),
            ]);

            // get the response content
            $response = json_decode(Arr::get($response, 'choices.0.message.content'), true, 512, JSON_THROW_ON_ERROR);
            $content = Arr::get($response, "value");
            $content = Str::clean($content);

            if (!empty($content)) {

                // clean content
                $content = Str::clean($content);

                // add title to extras
                $extras = $this->publication->extras;
                if (!isset($extras["yoast_seo"])) {
                    $extras["yoast_seo"] = [];
                }
                $extras["yoast_seo"]["title"] =  $content;
                $this->publication->extras = $extras;

                $this->publication->addLog("Yoast SEO title module completed successfully.", "success");
            } else {
                $this->publication->addLog("Yoast SEO title module failed. No title generated.", "warning");
            }
        } catch (Exception $e) {
            $this->publication->addLog("Yoast SEO title module failed. " . $e->getMessage(), "warning");
        }
    }

    /**
     * Generate a Yoast SEO description
     *
     * @return void
     */
    private function handleYoastDescription(): void
    {
        // verify that the yoast title generation is enabled
        if (!self::yoastDescriptionEnabled($this->publication))
            return;

        // log the start of the job
        $this->publication->addLog("Yoast SEO description module started.");

        try {

            // get the openai preset
            $preset = Preset::findFromAPI('yoast_seo_description');

            // run the preset
            $response = $preset->process([
                "language" => $this->publication->project->language->value,
                "request" => $this->publication->generation_title,
            ]);

            // get the response content
            $response = json_decode(Arr::get($response, 'choices.0.message.content'), true, 512, JSON_THROW_ON_ERROR);
            $content = Arr::get($response, "value");
            $content = Str::clean($content);

            if (!empty($content)) {

                // add description to extras
                $extras = $this->publication->extras;
                if (!isset($extras["yoast_seo"])) {
                    $extras["yoast_seo"] = [];
                }
                $extras["yoast_seo"]["description"] =  $content;
                $this->publication->extras = $extras;

                $this->publication->addLog("Yoast SEO description module completed successfully.", "success");
            } else {
                $this->publication->addLog("Yoast SEO description module failed. No description generated.", "warning");
            }
        } catch (Exception $e) {
            $this->publication->addLog("Yoast SEO description module failed. " . $e->getMessage(), "warning");
        }
    }

    /**
     * Generate a Rank Math title
     *
     * @return void
     */
    private function handleRankMathTitle(): void
    {
        // verify that the rank math title generation is enabled
        if (!self::rankMathTitleEnabled($this->publication)) {
            return;
        }

        // log the start of the job
        $this->publication->addLog("Rank Math title module started.");

        try {

            // get the openai preset
            $preset = Preset::findFromAPI('yoast_seo_title_emojis');

            // run the preset
            $response = $preset->process([
                "language" => $this->publication->project->language->value,
                "request" => $this->publication->generation_title,
                "has_emojis" => Arr::get($this->publication->project->modules, "wordpress.rank_math.title.emojis.enabled", false),
            ]);

            // get the response content
            $response = json_decode(Arr::get($response, 'choices.0.message.content'), true, 512, JSON_THROW_ON_ERROR);
            $content = Arr::get($response, "value");
            $content = Str::clean($content);

            if (!empty($content)) {

                // clean content
                $content = Str::clean($content);

                // add title to extras
                $extras = $this->publication->extras;
                if (!isset($extras["rank_math"])) {
                    $extras["rank_math"] = [];
                }
                $extras["rank_math"]["title"] =  $content;
                $this->publication->extras = $extras;

                $this->publication->addLog("Rank Math title module completed successfully.", "success");
            } else {
                $this->publication->addLog("Rank Math title module failed. No title generated.", "warning");
            }
        } catch (Exception $e) {
            $this->publication->addLog("Rank Math title module failed. " . $e->getMessage(), "warning");
        }
    }

    /**
     * Generate a Rank Math description
     *
     * @return void
     */
    private function handleRankMathDescription(): void
    {
        // verify that the rank math description generation is enabled
        if (!self::rankMathDescriptionEnabled($this->publication))
            return;

        // log the start of the job
        $this->publication->addLog("Rank Math description module started.");

        try {

            // get the openai preset
            $preset = Preset::findFromAPI('yoast_seo_description');

            // run the preset
            $response = $preset->process([
                "language" => $this->publication->project->language->value,
                "request" => $this->publication->generation_title,
            ]);

            // get the response content
            $response = json_decode(Arr::get($response, 'choices.0.message.content'), true, 512, JSON_THROW_ON_ERROR);
            $content = Arr::get($response, "value");
            $content = Str::clean($content);

            if (!empty($content)) {

                // add description to extras
                $extras = $this->publication->extras;
                if (!isset($extras["rank_math"])) {
                    $extras["rank_math"] = [];
                }
                $extras["rank_math"]["description"] =  $content;
                $this->publication->extras = $extras;

                $this->publication->addLog("Rank Math description module completed successfully.", "success");
            } else {
                $this->publication->addLog("Rank Math description module failed. No description generated.", "warning");
            }
        } catch (Exception $e) {
            $this->publication->addLog("Rank Math description module failed. " . $e->getMessage(), "warning");
        }
    }

    /**
     * Determine if the automatic tags module is runnable
     *
     * @param Publication $publication
     * @return boolean
     */
    static private function automaticTagsEnabled(Publication $publication): bool
    {
        // must be enabled
        if (!Arr::get($publication->project->modules, "wordpress.tags.automatic.enabled", false)) {
            return false;
        }

        return true;
    }

    /**
     * Determine if the automatic category module is runnable
     *
     * @param Publication $publication
     * @return boolean
     */
    static private function automaticCategoryEnabled(Publication $publication): bool
    {
        // must be enabled
        if (!Arr::get($publication->project->modules, "wordpress.categories.automatic.enabled", false)) {
            return false;
        }

        return true;
    }

    /**
     * Determine if the Yoast SEO title module is runnable
     *
     * @param Publication $publication
     * @return boolean
     */
    static private function yoastTitleEnabled(Publication $publication): bool
    {
        // must be enabled
        if (!Arr::get($publication->project->modules, "wordpress.yoast_seo.title.enabled", false)) {
            return false;
        }

        return true;
    }

    /**
     * Determine if the Yoast SEO description module is runnable
     *
     * @param Publication $publication
     * @return boolean
     */
    static private function yoastDescriptionEnabled(Publication $publication): bool
    {
        // must be enabled
        if (!Arr::get($publication->project->modules, "wordpress.yoast_seo.description.enabled", false)) {
            return false;
        }

        return true;
    }

    /**
     * Determine if the Rank Math title module is runnable
     *
     * @param Publication $publication
     * @return boolean
     */
    static private function rankMathTitleEnabled(Publication $publication): bool
    {
        // must be enabled
        if (!Arr::get($publication->project->modules, "wordpress.rank_math.title.enabled", false)) {
            return false;
        }

        return true;
    }

    /**
     * Determine if the Rank Math description module is runnable
     *
     * @param Publication $publication
     * @return boolean
     */
    static private function rankMathDescriptionEnabled(Publication $publication): bool
    {
        // must be enabled
        if (!Arr::get($publication->project->modules, "wordpress.rank_math.description.enabled", false)) {
            return false;
        }

        return true;
    }

    /**
     * Determine if the module is enabled
     *
     * @param Publication $publication
     * @return boolean
     */
    static public function isEnabled(Publication $publication): bool
    {
        return self::automaticTagsEnabled($publication) || self::automaticCategoryEnabled($publication) || self::yoastTitleEnabled($publication) || self::yoastDescriptionEnabled($publication) || self::rankMathTitleEnabled($publication) || self::rankMathDescriptionEnabled($publication);
    }

    /**
     * Determine if the module is runnable
     *
     * @param Publication $publication
     * @return boolean
     */
    static public function isRunnable(Publication $publication): bool
    {
        // must be enabled
        // publication sections must not be empty
        return self::isEnabled($publication) && $publication->sections->isNotEmpty();
    }
}
