<?php

namespace OtomaticAi\Utils\Linking\Templates;

use OtomaticAi\Vendors\Illuminate\Support\Arr;
use WP_Post;

class InlineTemplate extends Template
{
    /**
     * Create the html template
     *
     * @param boolean $echo
     * @return string
     */
    public function display(bool $echo = false): string
    {
        $html = [];

        $html = array_merge($html, $this->makeTemplateTitleHtml());

        foreach ($this->posts as $post) {

            $style = $this->getWrapperStyle();
            $html[] = '<!-- wp:columns -->';
            $html[] = '<div class="wp-block-columns"' . (strlen($style) > 0 ? ' style="' . $style . '"' : '') . '>';

            // thumbnail
            if (Arr::get($this->elements, "thumbnail.enabled", false)) {
                $html[] = '<!-- wp:column {"width":"33.33%"} -->';
                $html[] = '<div class="wp-block-column" style="flex-basis:33.33%">';

                $html = array_merge($html, $this->makeThumbnailHtml($post));

                $html[] = '</div>';
                $html[] = '<!-- /wp:column -->';
            }

            if (Arr::get($this->elements, "thumbnail.enabled", false)) {
                $html[] = '<!-- wp:column {"width":"66.66%"} -->';
                $html[] = '<div class="wp-block-column" style="flex-basis:66.66%">';
            } else {
                $html[] = '<!-- wp:column {"width":"100%"} -->';
                $html[] = '<div class="wp-block-column" style="flex-basis:100%">';
            }

            // title
            $html = array_merge($html, $this->makeTitleHtml($post));

            // excerpt
            $html = array_merge($html, $this->makeExcerptHtml($post));

            if (Arr::get($this->elements, "thumbnail.enabled", false)) {
                $html[] = '</div>';
                $html[] = '<!-- /wp:column -->';
            } else {
                $html[] = '</div>';
                $html[] = '<!-- /wp:column -->';
            }

            $html[] = '</div>';
            $html[] = '<!-- /wp:columns -->';
        }

        if ($echo) {
            echo implode("\n", $html);
        }

        return implode("\n", $html);
    }

    private function makeThumbnailHtml(WP_Post $post): array
    {
        $html = [];

        if (Arr::get($this->elements, "thumbnail.enabled", false)) {
            $permalink = esc_url(get_permalink($post));
            $title = get_the_title($post);
            $thumbnailId = get_post_thumbnail_id($post);
            $thumbnail = get_the_post_thumbnail($post, 'large');

            if (strlen($thumbnail) > 0) {
                $html[] = '<!-- wp:image {"id":' . $thumbnailId . ',"sizeSlug":"large","linkDestination":"custom"} -->';
                $html[] = '<figure class="wp-block-image size-large">';
                $html[] = "<a href='" . $permalink . "' title='" . $title . "'>";
                $html[] = $thumbnail;
                $html[] = "</a>";
                $html[] = "</figure>";
                $html[] = "<!-- /wp:image -->";
            }
        }

        return $html;
    }

    private function makeTitleHtml(WP_Post $post): array
    {
        $html = [];

        if (Arr::get($this->elements, "title.enabled", false)) {
            $permalink = esc_url(get_permalink($post));
            $title = get_the_title($post);
            $style = $this->getTitleStyle(["text-decoration" => "none"]);

            $html[] = "<!-- wp:paragraph -->";
            $html[] = "<p>";
            $html[] = "<a href='" . $permalink . "'" . (strlen($style) > 0 ? ' style="' . $style . '"' : '') . ">" . $title . "</a>";
            $html[] = "</p>";
            $html[] = "<!-- /wp:paragraph -->";
        }

        return $html;
    }

    private function makeExcerptHtml(WP_Post $post): array
    {
        $html = [];

        if (Arr::get($this->elements, "excerpt.enabled", false)) {
            $excerpt = $this->getExcerpt($post, Arr::get($this->elements, "excerpt.length", 40));
            $style = $this->getExcerptStyle();

            $html[] = "<!-- wp:paragraph -->";
            $html[] = "<p" . (strlen($style) > 0 ? ' style="' . $style . '"' : '') . ">" . $excerpt . "</p>";
            $html[] = "<!-- /wp:paragraph -->";
        }

        return $html;
    }
}
