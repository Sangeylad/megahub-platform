<?php

namespace OtomaticAi\Modules;

use Exception;
use OtomaticAi\Api\OtomaticAi\Client;
use OtomaticAi\Content\Section;
use OtomaticAi\Content\Video\Youtube;
use OtomaticAi\Models\Preset;
use OtomaticAi\Models\Publication;
use OtomaticAi\Modules\Contracts\Module as ModuleContract;
use OtomaticAi\Utils\Auth;
use OtomaticAi\Vendors\Illuminate\Support\Arr;
use OtomaticAi\Vendors\Illuminate\Support\Str;

class ProcessVideoModule implements ModuleContract
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
        if (!self::isRunnable($this->publication))
            return;

        // log the start of the job
        $this->publication->addLog("Video module started.");

        // get the video
        $video = null;
        switch (Arr::get($this->publication->project->modules, "video.service")) {
            case "youtube":
                $video = $this->getYoutubeVideo($this->publication->generation_title);
                break;
        }

        // add the video to sections
        // log the end of the job
        if (!empty($video)) {

            // get publication sections
            $sections = $this->publication->sections;

            // add the video to selected position
            switch (Arr::get($this->publication->project->modules, 'video.position')) {
                case "top":
                    $sections->prepend(new Section(null, [$video]));
                    break;
                case "bottom":
                    $sections->push(new Section(null, [$video]));
                    break;
                case "middle":
                    $sections->get(intval(floor($sections->count() - 1 / 2)))->addElement($video);
                    break;
                case "random":
                    $sections->get(rand(0, $sections->count() - 1))->addElement($video);
                    break;
            }

            // update publication sections
            $this->publication->sections = $sections;

            $this->publication->addLog("Video module completed successfully.", "success");
        } else {
            $this->publication->addLog("Video module completed with errors.", "warning");
        }
    }

    /**
     * Generate an Youtube video for the provided search
     *
     * @param string $search
     * @return Youtube|null
     */
    private function getYoutubeVideo(string $search)
    {
        // log the video generation
        $this->publication->addLog("Video generation with Youtube started.");

        try {

            // make the search for youtube
            $search = $this->makeYoutubeSearch($search);

            // call the api
            $api = new Client;
            $result = $api->youtube($search, $this->publication->project->language->key);

            // get the videos
            $videos = is_array($result) ? $result : [];

            // get a random video
            if (!empty($videos)) {
                $video = Arr::random($videos);
                return new Youtube($video["id"], $video["title"]);
            } else {
                $this->publication->addLog("Video generation failed. No videos found.", "warning");
            }
        } catch (Exception $e) {
            $this->publication->addLog("Video generation failed. " . $e->getMessage(), "warning");
        }
    }

    /**
     * Make the Youtube search terms for the provided search
     *
     * @param string $search
     * @return string
     * @throws Exception
     */
    private function makeYoutubeSearch(string $search): string
    {
        $search = Str::lower($search);
        return $search;

        // $preset = Preset::findFromAPI("main_keyword");

        // $response = $preset->process([
        //     "language" => $this->publication->project->language->value,
        //     "request" => $this->publication->generation_title,
        // ]);

        // // get the response content
        // $response = json_decode(Arr::get($response, 'choices.0.message.content'), true, 512, JSON_THROW_ON_ERROR);
        // $content = Arr::get($response, "value");
        // $content = Str::clean($content);

        // return Str::lower($content);
    }

    /**
     * Determine if the module is enabled
     *
     * @param Publication $publication
     * @return boolean
     */
    static public function isEnabled(Publication $publication): bool
    {
        return Arr::get($publication->project->modules, "video.enabled", false);
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

        return true;
    }
}
