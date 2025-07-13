<?php

namespace OtomaticAi\Controllers\Linking;

use Exception;
use OtomaticAi\Controllers\Controller;
use OtomaticAi\Models\Linking;
use OtomaticAi\Models\Preset;
use OtomaticAi\Models\WP\Post;
use OtomaticAi\Vendors\Illuminate\Support\Arr;
use OtomaticAi\Vendors\Illuminate\Support\Str;
use OtomaticAi\Vendors\Illuminate\Validation\Rule;

class ManualController extends Controller
{
    public function index()
    {
        $this->verifyNonce();

        $this->validate([
            "sort_order" => ["nullable", "string"],
            "sort_direction" => ["nullable", "string", Rule::in(["asc", "desc"])],
        ]);

        $links = $this->makeQuery();
        $links->with("post");
        $links = $links->get();

        $this->response($links);
    }

    public function store()
    {
        $this->verifyNonce();

        $this->validate([
            "mode" => ["required", Rule::in(["post", "custom"])],
            "post_id" => [
                "nullable",
                "required_if:mode,post",
                function ($attribute, $value, $fail) {
                    if ($this->input("mode") === "post" && !Post::find($value)) {
                        $fail('The ' . $attribute . ' is incorrect.');
                    }
                }
            ],
            "custom_url" => ["nullable", "required_if:mode,custom", "url"],
            "keywords" => ["required", "string"],
            "max_links" => ["integer", "min:0"],
            "post_types" => ["required", "array"],
            "is_blank" => ["boolean"],
            "is_follow" => ["boolean"],
            "is_obfuscated" => ["boolean"],
        ]);

        $keywords = $this->input("keywords");
        $keywords = explode("\n", $keywords);
        $keywords = array_map("trim", $keywords);
        $keywords = array_values(array_filter($keywords, function ($str) {
            return !empty($str);
        }));

        // create the link
        $link = new Linking;
        if ($this->input("mode") === "post") {
            $post = Post::find($this->input("post_id"));
            if ($post) {
                $link->post()->associate($post);
            }
        }

        $link->mode = $this->input("mode");
        $link->custom_url = $this->input("custom_url");
        $link->keywords = $keywords;
        $link->max_links = $this->input("max_links");
        $link->post_types = $this->input("post_types");
        $link->is_blank = $this->input("is_blank");
        $link->is_follow = $this->input("is_follow");
        $link->is_obfuscated = $this->input("is_obfuscated");

        if ($link->save()) {
            $this->emptyResponse();
        } else {
            $this->response(["message" => "An error occurred", "error" => "Unable to save the new link."], 503);
        }
    }

    public function update()
    {
        $this->verifyNonce();

        $this->validate([
            "id" => ["required"],
            "mode" => ["required", Rule::in(["post", "custom"])],
            "post_id" => [
                "nullable",
                "required_if:mode,post",
                function ($attribute, $value, $fail) {
                    if ($this->input("mode") === "post" && !Post::find($value)) {
                        $fail('The ' . $attribute . ' is incorrect.');
                    }
                }
            ],
            "custom_url" => ["nullable", "required_if:mode,custom", "url"],
            "keywords" => ["required", "string"],
            "max_links" => ["integer", "min:0"],
            "post_types" => ["required", "array"],
            "is_blank" => ["boolean"],
            "is_follow" => ["boolean"],
            "is_obfuscated" => ["boolean"],
        ]);

        // get the link
        $link = Linking::find($this->input("id"));
        if ($link === null) {
            $this->response(["message" => "An error occurred", "error" => "Unable to find the link #" . $this->input("id") . "."], 503);
        }

        $keywords = $this->input("keywords");
        $keywords = explode("\n", $keywords);
        $keywords = array_map("trim", $keywords);
        $keywords = array_values(array_filter($keywords, function ($str) {
            return !empty($str);
        }));

        // update the link
        if ($this->input("mode") === "post") {
            $post = Post::find($this->input("post_id"));
            if ($post) {
                $link->post()->associate($post);
            }
        }

        $link->mode = $this->input("mode");
        $link->custom_url = $this->input("custom_url");
        $link->keywords = $keywords;
        $link->max_links = $this->input("max_links");
        $link->post_types = $this->input("post_types");
        $link->is_blank = $this->input("is_blank");
        $link->is_follow = $this->input("is_follow");
        $link->is_obfuscated = $this->input("is_obfuscated");

        if ($link->save()) {
            $this->emptyResponse();
        } else {
            $this->response(["message" => "An error occurred", "error" => "Unable to update the link."], 503);
        }
    }

    public function destroy()
    {
        $this->verifyNonce();

        $this->validate([
            "id" => ["required", "integer"],
        ]);

        $link = Linking::find($this->input('id'));
        if ($link) {
            $link->delete();
        }

        $this->emptyResponse();
    }

    public function generateKeywords()
    {
        $this->verifyNonce();

        $this->validate([
            "keyword" => ["required", "string"],
        ]);

        try {
            // get the openai preset
            $preset = Preset::findFromAPI("linking_link_keywords");

            // run the preset
            $response = $preset->process([
                "request" => $this->input("keyword"),
            ]);

            // get the response content
            $response = json_decode(Arr::get($response, 'choices.0.message.content'), true, 512, JSON_THROW_ON_ERROR);
            $keywords = Arr::get($response, "values");
            if (!empty($keywords)) {
                $keywords = array_map(function ($str) {
                    return Str::clean($str);
                }, $keywords);
                $keywords = array_values(array_filter($keywords, function ($str) {
                    return !empty($str);
                }));
                $this->response($keywords);
            }
        } catch (Exception $e) {
            $this->response(["message" => "An error occurred", "error" => $e->getMessage()], 503);
        }

        $this->response([]);
    }

    public function searchPosts()
    {
        $this->verifyNonce();

        $this->validate([
            "query" => ["required", "string"],
        ]);

        $postTypes = get_post_types([
            "public" => true,
        ], "object");

        $postTypes = array_filter($postTypes, function ($type) {
            return !in_array($type->name, ["attachment"]);
        });

        $posts = Post::select("ID", "post_title", "post_type")
            ->where("post_title", "like", "%" . $this->input("query") . "%")
            ->whereIn("post_type", Arr::pluck($postTypes, "name"))
            ->limit(20)
            ->get();
        $this->response($posts);
    }

    private function makeQuery()
    {
        $links = Linking::query();

        // sort 
        if (!empty($sortOrder = $this->input('sort_order', ''))) {
            $links->orderBy($sortOrder, $this->input('sort_direction', 'desc'));
        } else {
            $links->orderBy("id", "desc");
        }

        return $links;
    }
}
