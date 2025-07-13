<?php

namespace OtomaticAi\Utils\Linking\Templates;

use OtomaticAi\Utils\Linking\Linking;
use OtomaticAi\Utils\Linking\Templates\Contracts\ShouldDisplay;
use OtomaticAi\Vendors\Illuminate\Support\Arr;
use OtomaticAi\Vendors\Illuminate\Support\Str;
use WP_Post;

abstract class Template implements ShouldDisplay
{
    /**
     * The posts list
     *
     * @var array
     */
    protected array $posts = [];

    /**
     * The elements to display
     *
     * @var array
     */
    protected array $elements = [];

    /**
     * The title to display
     *
     * @var array
     */
    protected array $title = [];

    /**
     * The template settings
     *
     * @var array
     */
    protected array $settings = [];

    /**
     * The template theme
     *
     * @var array
     */
    protected array $theme = [];

    /**
     * Instantiate a new template
     *
     * @param array $posts
     * @param array $elements
     * @param array $title
     * @param array $theme
     * @param array $settings
     */
    public function __construct(array $posts = [], array $elements = [], array $title = [], array $theme = [], array $settings = [])
    {
        $this->posts = $posts;
        $this->elements = $elements;
        $this->title = $title;
        $this->theme = $theme;
        $this->settings = $settings;
    }

    /**
     * Add a post to the posts list
     *
     * @param WP_Post $post
     * @return void
     */
    public function addPost(WP_Post $post): void
    {
        $this->posts[] = $post;
    }

    /**
     * Add posts to the posts list
     *
     * @param array $posts
     * @return void
     */
    public function addPosts(array $posts): void
    {
        $this->posts = array_merge($this->posts, $posts);
    }

    /**
     * Set the posts list
     *
     * @param array $posts
     * @return void
     */
    public function setPosts(array $posts): void
    {
        $this->posts = $posts;
    }

    /**
     * Get the posts list
     *
     * @return array
     */
    public function getPosts(): array
    {
        return $this->posts;
    }

    protected function makeTemplateTitleHtml(): array
    {
        $html = [];

        $title = Arr::get($this->title, "value", null);

        if (!empty($title)) {
            $node = Arr::get($this->title, "node", "h3");

            switch ($node) {
                case "p":
                    $html[] = "<!-- wp:paragraph -->";
                    $html[] = "<p>";
                    $html[] = $title;
                    $html[] = "</p>";
                    $html[] = "<!-- /wp:paragraph -->";
                    break;
                case "h2":
                case "h3":
                case "h4":
                case "h5":
                    $html[] = "<!-- wp:heading " . ($node !== "h2" ? '{"level":' . str_replace('h', '', $node) . '} ' : '') . "-->";
                    $html[] = "<" . $node . ">";
                    $html[] = $title;
                    $html[] = "</" . $node . ">";
                    $html[] = "<!-- /wp:heading -->";
                    break;
            }
        }

        return $html;
    }

    protected function getWrapperStyle(array $defaultStyles = []): string
    {
        $styles = array_merge($defaultStyles, Arr::get($this->theme, "wrapper", []));
        $styles = $this->buildStyles($styles);

        return implode(";", $styles);
    }

    protected function getTitleStyle(array $defaultStyles = []): string
    {
        $styles = array_merge($defaultStyles, Arr::get($this->theme, "title", []));
        $styles = $this->buildStyles($styles);

        return implode(";", $styles);
    }

    protected function getExcerptStyle(array $defaultStyles = []): string
    {
        $styles = array_merge($defaultStyles, Arr::get($this->theme, "excerpt", []));
        $styles = $this->buildStyles($styles);

        return implode(";", $styles);
    }

    protected function buildStyles(array $styles)
    {
        $styles = array_map(function ($value, $key) {
            if ($value) {
                return implode(":", [Str::kebab($key), $value]);
            }
        }, array_values($styles), array_keys($styles));
        $styles = array_filter($styles);
        $styles = array_values($styles);

        return $styles;
    }

    protected function getExcerpt(WP_Post $post, int $limit = 40): string
    {
        remove_filter("the_content", [Linking::class, 'filter'], 1);
        $excerpt = get_the_content(null, false, $post);
        add_filter("the_content", [Linking::class, 'filter'], 1);
        $excerpt = strip_shortcodes($excerpt);
        $excerpt = strip_tags($excerpt);
        $excerpt = wp_trim_words($excerpt, $limit);

        return $excerpt;
    }
}
