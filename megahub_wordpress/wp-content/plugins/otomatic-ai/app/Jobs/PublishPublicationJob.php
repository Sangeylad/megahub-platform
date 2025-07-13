<?php

namespace OtomaticAi\Jobs;

use Exception;
use OtomaticAi\Api\OtomaticAi\Client;
use OtomaticAi\Models\Publication;
use OtomaticAi\Models\WP\Post;
use OtomaticAi\Content\Image\Image;
use OtomaticAi\Modules\ProcessCustomFieldsModule;
use OtomaticAi\Modules\ProcessTextModule;
use OtomaticAi\Modules\ProcessImageModule;
use OtomaticAi\Modules\ProcessVideoModule;
use OtomaticAi\Modules\ProcessTwitterModule;
use OtomaticAi\Modules\ProcessInstagramModule;
use OtomaticAi\Modules\ProcessTiktokModule;
use OtomaticAi\Modules\ProcessFacebookModule;
use OtomaticAi\Modules\ProcessWordpressModule;
use OtomaticAi\Utils\Auth;
use OtomaticAi\Vendors\Carbon\Carbon;
use OtomaticAi\Vendors\Illuminate\Database\Capsule\Manager as Database;
use OtomaticAi\Vendors\Illuminate\Support\Arr;

class PublishPublicationJob extends Job
{
    private Publication $publication;
    private float $startTime;
    private float $endTime;

    /**
     * Create a new job instance.
     */
    public function __construct(Publication $publication)
    {
        $this->publication = $publication;
        $this->publication->load('project', 'project.persona');
    }

    /**
     * Execute the job.
     */
    public function handle()
    {
        global $wpdb;

        // start timer
        $this->startTime = microtime(true);

        // verify that the publication can be publish
        if (!$this->canPublish()) {
            return;
        }

        // clear publication logs
        $this->publication->clearLogs();

        // log the start of the job
        $this->publication->addLog("Publication started.");

        // set error, exception and shutdown handlers
        $this->setErrorHandler();
        $this->setExceptionHandler();
        $this->setShutdownHandler();

        // set the publication status to pending
        $this->publication->status = "pending";
        $this->publication->save();

        // set the time limit to 1200 seconds
        set_time_limit(1200);
        Database::update("SET SESSION wait_timeout=1200;");
        Database::update("SET SESSION interactive_timeout=1200;");
        $wpdb->query("SET SESSION wait_timeout=1200;");
        $wpdb->query("SET SESSION interactive_timeout=1200;");

        // refresh auth
        Auth::refreshDomain();

        // save start event
        $this->collectEvent("publish-job-start", [
            "type" => $this->publication->project->type,
            "model" => Arr::get($this->publication->project->modules, "text.model", 'gpt-3.5-turbo'),
        ]);

        // set the current user
        if (!empty(Arr::get($this->publication->project->modules, 'wordpress.author_id'))) {
            wp_set_current_user(Arr::get($this->publication->project->modules, 'wordpress.author_id'));
        } else if (!empty($first = Arr::get(get_users(["fields" => 'ID']), 0))) {
            wp_set_current_user($first);
        }

        // instantiate modules jobs
        $jobs = [];

        // text module
        if (ProcessTextModule::isEnabled($this->publication)) {
            $jobs[] = new ProcessTextModule($this->publication);
        }

        // image module
        if (ProcessImageModule::isEnabled($this->publication)) {
            $jobs[] = new ProcessImageModule($this->publication);
        }

        // video module
        if (ProcessVideoModule::isEnabled($this->publication)) {
            $jobs[] = new ProcessVideoModule($this->publication);
        }

        // instagram module
        if (ProcessInstagramModule::isEnabled($this->publication)) {
            $jobs[] = new ProcessInstagramModule($this->publication);
        }

        // twitter module
        if (ProcessTwitterModule::isEnabled($this->publication)) {
            $jobs[] = new ProcessTwitterModule($this->publication);
        }

        // tiktok module
        if (ProcessTiktokModule::isEnabled($this->publication)) {
            $jobs[] = new ProcessTiktokModule($this->publication);
        }

        // facebook module
        if (ProcessFacebookModule::isEnabled($this->publication)) {
            $jobs[] = new ProcessFacebookModule($this->publication);
        }

        // wordpress module
        if (ProcessWordpressModule::isEnabled($this->publication)) {
            $jobs[] = new ProcessWordpressModule($this->publication);
        }

        // custom fields module
        if (ProcessCustomFieldsModule::isEnabled($this->publication)) {
            $jobs[] = new ProcessCustomFieldsModule($this->publication);
        }

        try {
            // run modules jobs
            foreach ($jobs as $job) {
                $job->handle();
            }
        } catch (Exception $e) {
            return $this->fail($e);
        }

        // make content
        $content = $this->publication->sections->display();

        // quit if no content generated
        if (empty($content)) {
            return $this->fail(new Exception("No content generated"));
        }

        // create or update the post
        $post = $this->publication->post;
        if (!$post) {
            $post = new Post;
        }
        $post->post_title = $this->publication->title;
        $post->post_status = Arr::get($this->publication->project->modules, 'wordpress.status');
        $post->post_content = $content;
        $post->post_type = Arr::get($this->publication->project->modules, 'wordpress.post_type', 'post');

        // author id
        if (!empty(Arr::get($this->publication->project->modules, 'wordpress.author_id'))) {
            $post->post_author = Arr::get($this->publication->project->modules, 'wordpress.author_id');
        }

        // post_parent with publication parent
        if (Arr::get($this->publication->project->modules, 'wordpress.post_type', 'post') === 'page') {
            $parent = $this->publication->parent;
            if ($parent && $parent->status === 'success') {
                $post->post_parent = $parent->post_id;
            } else {
                $parentPageId = Arr::get($this->publication->project->modules, "wordpress.parent_page_id");
                if (!empty($parentPageId) && !empty(Post::find($parentPageId))) {
                    $post->post_parent = $parentPageId;
                }
            }
        }

        $post->save();

        // ---------------
        // extras details
        // ---------------

        // thumbnail
        if (($image = Arr::get($this->publication->extras, "thumbnail")) !== null) {
            $image = Image::fromArray($image);
            if ($image !== null) {
                if (($attachementId = $image->image->save($this->publication->title, $image->description, $image->legend)) !== null) {
                    if (set_post_thumbnail($post->ID, $attachementId) === false) {
                        $this->publication->addLog("Unable to save the post thumbnail.", "warning");
                    }
                }
            }
        }

        // page template
        if (!empty(Arr::get($this->publication->project->modules, 'wordpress.template'))) {
            if (update_post_meta($post->ID, "_wp_page_template", Arr::get($this->publication->project->modules, 'wordpress.template')) === false) {
                $this->publication->addLog("Unable to save the page template.", "warning");
            }
        }

        // attach categories
        $categories = [];
        if (!empty($category = Arr::get($this->publication->extras, "category"))) {
            $categories[] = $category;
        } else if (!Arr::get($this->publication->project->modules, 'wordpress.categories.automatic.enabled', false) && count(Arr::get($this->publication->project->modules, 'wordpress.categories.custom', [])) > 0) {
            $categories = Arr::get($this->publication->project->modules, 'wordpress.categories.custom', []);
        }
        if (count($categories) > 0) {
            $arr = wp_set_post_categories($post->ID, $categories);
            if (is_wp_error($arr)) {
                $this->publication->addLog("Unable to attach the categories. " . $arr->get_error_message(), "warning");
            } else if ($arr === false) {
                $this->publication->addLog("Unable to attach the categories.", "warning");
            }
        }

        // add custom tags
        $tags = [];
        if (count(Arr::get($this->publication->project->modules, 'wordpress.tags.custom', [])) > 0) {
            $tags = array_merge($tags, Arr::get($this->publication->project->modules, 'wordpress.tags.custom', []));
        }

        // add automatic tags
        if (count($automaticTags = Arr::get($this->publication->extras, "tags", [])) > 0) {
            $tags = array_merge($tags, $automaticTags);
        }

        // attach tags
        if (count($tags) > 0) {
            $arr = wp_set_post_tags($post->ID, $tags);
            if (is_wp_error($arr)) {
                $this->publication->addLog("Unable to attach the tags. " . $arr->get_error_message(), "warning");
            } else if ($arr === false) {
                $this->publication->addLog("Unable to attach the tags.", "warning");
            }
        }

        // Yoast SEO title
        if (($yoastSeoTitle = Arr::get($this->publication->extras, "yoast_seo.title", null)) !== null) {
            if (update_post_meta($post->ID, "_yoast_wpseo_title", $yoastSeoTitle) === false) {
                $this->publication->addLog("Unable to save the Yoast SEO title.", "warning");
            }
        }

        // Yoast SEO description
        if (($yoastSeoDescription = Arr::get($this->publication->extras, "yoast_seo.description", null)) !== null) {
            if (update_post_meta($post->ID, "_yoast_wpseo_metadesc", $yoastSeoDescription) === false) {
                $this->publication->addLog("Unable to save the Yoast SEO description.", "warning");
            }
        }

        // Rank Math title
        if (($rankMathTitle = Arr::get($this->publication->extras, "rank_math.title", null)) !== null) {
            if (update_post_meta($post->ID, "rank_math_title", $rankMathTitle) === false) {
                $this->publication->addLog("Unable to save the Rank Math title.", "warning");
            }
        }

        // Rank Math description
        if (($rankMathDescription = Arr::get($this->publication->extras, "rank_math.description", null)) !== null) {
            if (update_post_meta($post->ID, "rank_math_description", $rankMathDescription) === false) {
                $this->publication->addLog("Unable to save the Rank Math description.", "warning");
            }
        }

        // custom fields
        foreach (Arr::get($this->publication->extras, "custom_fields", []) as $customField) {
            $key = Arr::get($customField, "key");
            $value = Arr::get($customField, "value");
            if (!empty($key)) {
                if (update_post_meta($post->ID, $key, $value) === false) {
                    $this->publication->addLog("Unable to save the custom field `" . $key . "`.", "warning");
                }
            }
        }

        // attach the post to the publication
        $this->publication->post()->associate($post);

        $this->publication->status = "success";
        $this->publication->save();

        // end timer
        $this->endTime = microtime(true);

        // calculate execution time
        $executionTime = ($this->endTime - $this->startTime);

        $this->publication->addLog("Publication published successfully in " . round($executionTime, 2) . " seconds. Post ID: " . $this->publication->post->ID, "success");

        // save end event
        $this->collectEvent("publish-job-end", [
            "type" => $this->publication->project->type,
            "model" => Arr::get($this->publication->project->modules, "text.model", 'gpt-3.5-turbo'),
            "time" => $executionTime,
        ]);

        // refresh auth
        Auth::refreshDomain();

        $this->clearErrorHandler();
        $this->clearExceptionHandler();
    }

    private function canPublish()
    {
        // project enable
        if (!$this->publication->project->enabled)
            return false;

        // publication not started
        if ($this->publication->status !== "idle")
            return false;

        // publication published_at less than now
        if ($this->publication->published_at->greaterThan(Carbon::now()))
            return false;

        // publication parent page published
        if (Arr::get($this->publication->project->modules, 'wordpress.post_type', 'post') === 'page') {
            $parent = $this->publication->parent;
            if ($parent && $parent->status !== 'success')
                return false;
        }

        // premium or trial
        if (!Auth::isPremium() && !Auth::isTrial()) {
            return false;
        }

        return true;
    }

    private function fail($error)
    {
        $this->publication->addLog("Publication failed. " . $error->getMessage(), "error");

        // save end event
        $this->collectEvent("publish-job-failed", [
            "type" => $this->publication->project->type,
            "model" => Arr::get($this->publication->project->modules, "text.model", 'gpt-3.5-turbo'),
            "message" => $error->getMessage(),
        ]);

        $this->publication->status = "failed";
        $this->publication->save();
    }

    private function setErrorHandler()
    {
        set_error_handler(function ($errno, $errstr, $errfile, $errline) {
            $errstr = htmlspecialchars($errstr);

            switch ($errno) {
                case E_ERROR:
                case E_USER_ERROR:
                    $this->fail(new Exception("Error: " . $errstr . " in " . $errfile . " on line " . $errline));
                    break;
            }

            return false;
        });
    }

    private function setExceptionHandler()
    {
        set_exception_handler(function ($e) {
            $this->fail(new Exception("Exception: " . $e->getMessage() . " in " . $e->getFile() . " on line " . $e->getLine()));
            throw $e;
        });
    }

    private function setShutdownHandler()
    {
        register_shutdown_function(function () {
            if ($this->publication->status === "pending") {
                $this->fail(new Exception("The generation was stopped by the server. Verify that your server supports long-running scripts."));
            }
        });
    }

    private function clearErrorHandler()
    {
        set_error_handler(null);
    }

    private function clearExceptionHandler()
    {
        set_exception_handler(null);
    }

    private function collectEvent(string $key, array $payload = [])
    {
        $api = new Client;
        $api->collectEvent($key, $payload);
    }
}
