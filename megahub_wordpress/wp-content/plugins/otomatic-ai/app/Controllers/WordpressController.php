<?php

namespace OtomaticAi\Controllers;

use OtomaticAi\Models\WP\Post;
use OtomaticAi\Models\WP\Term;
use OtomaticAi\Vendors\Illuminate\Support\Arr;

class WordpressController extends Controller
{
    public function users()
    {
        $this->verifyNonce();

        $this->response(get_users());
    }

    public function userRoles()
    {
        $this->verifyNonce();

        $roles = get_editable_roles();
        $roles = array_map(function ($role) {
            return $role["name"];
        }, $roles);

        $this->response($roles);
    }

    public function postTypes()
    {
        $this->verifyNonce();

        $postTypes = get_post_types([
            "public" => true,
        ], "object");

        $postTypes = array_filter($postTypes, function ($type) {
            return !in_array($type->name, ["attachment"]);
        });

        $postTypes = array_map(function ($type) {
            return [
                "name" => $type->name,
                "label" => $type->labels->singular_name
            ];
        }, $postTypes);

        $postTypes = array_values($postTypes);

        $this->response($postTypes);
    }

    public function templates()
    {
        $this->verifyNonce();

        $this->response(get_page_templates());
    }

    public function categories()
    {
        $this->verifyNonce();

        $this->response(get_categories(['hide_empty' => 0]));
    }

    public function statuses()
    {
        $this->verifyNonce();

        $this->response(get_post_statuses());
    }

    public function tags()
    {
        $this->verifyNonce();

        $this->validate([
            "query" => ["required", "string"],
        ]);

        $query = $this->input("query", '');
        $this->response(Term::tags()->where('name', 'LIKE', '%' . $query . '%')->get());
    }
}
