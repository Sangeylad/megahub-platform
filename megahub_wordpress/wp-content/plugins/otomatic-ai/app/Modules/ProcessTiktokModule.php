<?php

namespace OtomaticAi\Modules;

use Exception;
use OtomaticAi\Api\OtomaticAi\Client;
use OtomaticAi\Content\Social\Tiktok;
use OtomaticAi\Models\Publication;
use OtomaticAi\Models\Preset;
use OtomaticAi\Modules\Contracts\Module as ModuleContract;
use OtomaticAi\Utils\Auth;
use OtomaticAi\Vendors\Illuminate\Support\Arr;
use OtomaticAi\Vendors\Illuminate\Support\Str;

class ProcessTiktokModule implements ModuleContract
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

        // log the start of the job
        $this->publication->addLog("Tiktok module started.");

        // determine length
        $length = max(1, intval(Arr::get($this->publication->project->modules, "tiktok.length", 1)));

        try {
            // make the search terms
            $search = $this->makeSearch($this->publication->generation_title);

            // call the api
            $api = new Client;
            $result = $api->tiktok($search, $this->publication->project->language->key);

            // get the organic results
            $posts = is_array($result) ? $result : [];

            // randomize posts
            $posts = Arr::shuffle($posts);

            if (!empty($posts)) {

                // get x random posts
                $posts = Arr::random($posts, min(count($posts), $length));
                $posts = array_map(function ($post) {
                    return new Tiktok($post["link"]);
                }, $posts);

                // get publication sections
                $sections = $this->publication->sections;

                // add posts to sections
                switch (Arr::get($this->publication->project->modules, 'tiktok.position')) {
                    case "top":
                        $sections->first()->addElements($posts);
                        break;
                    case "bottom":
                        $sections->last()->addElements($posts);
                        break;
                    case "middle":
                        $sections->get(intval(floor($sections->count() - 1 / 2)))->addElements($posts);
                        break;
                    case "random":
                        $sections->get(rand(0, $sections->count() - 1))->addElements($posts);
                        break;
                }

                // update publication sections
                $this->publication->sections = $sections;

                // log the end of the job
                $this->publication->addLog("Tiktok module completed successfully.", "success");
            } else {
                $this->publication->addLog("Tiktok module failed. No posts found.", "warning");
            }
        } catch (Exception $e) {
            $this->publication->addLog("Tiktok module failed. " . $e->getMessage(), "warning");
        }
    }

    /**
     * Make the Tiktok search terms for the provided search
     *
     * @param string $search
     * @return string
     * @throws Exception
     */
    private function makeSearch(string $search): string
    {
        $search = Str::lower($search);

        $preset = Preset::findFromAPI("main_keyword");

        $response = $preset->process([
            "language" => $this->publication->project->language->value,
            "request" => $this->publication->generation_title,
        ]);

        // get the response content
        $response = json_decode(Arr::get($response, 'choices.0.message.content'), true, 512, JSON_THROW_ON_ERROR);
        $content = Arr::get($response, "value");
        $content = Str::clean($content);

        return Str::lower($content);
    }

    /**
     * Determine if the module is enabled
     *
     * @param Publication $publication
     * @return boolean
     */
    static public function isEnabled(Publication $publication): bool
    {
        return Arr::get($publication->project->modules, "tiktok.enabled", false);
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
        if (!self::isEnabled($publication)) {
            return false;
        }

        // publication sections must not be empty
        if ($publication->sections->isEmpty()) {
            return false;
        }

        // length must be greater than 0
        if (intval(Arr::get($publication->project->modules, "tiktok.length", 1)) <= 0) {
            return false;
        }

        return true;
    }
}
