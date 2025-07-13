<?php

namespace OtomaticAi\Utils\Linking;

use OtomaticAi\Utils\Linking\Templates\GridTemplate;
use OtomaticAi\Utils\Linking\Templates\InlineTemplate;
use OtomaticAi\Utils\Linking\Templates\Template;
use OtomaticAi\Utils\Settings;
use OtomaticAi\Vendors\Illuminate\Support\Arr;
use OtomaticAi\Vendors\Illuminate\Support\Collection;
use WP_Post;
use WP_Query;

class AutomaticLinking
{
    private WP_Post $post;

    public function __construct(WP_POST $post)
    {
        $this->post = $post;
    }

    /**
     * add linking to the content
     *
     * @param string $content
     * @return string
     */
    public function run(string $content): string
    {
        if (is_single($this->post)) {
            $content = $this->handlePostLinking($content);
        } else if (is_page($this->post)) {
            $content = $this->handlePageLinking($content);
        }

        return $content;
    }

    private function handlePostLinking(string $content): string
    {
        // verify that the pages linking is enabled
        if (!Settings::get("linking.posts.enabled", false)) {
            return $content;
        }

        $posts = $this->getRelatedPosts(Settings::get("linking.posts.sources", []), Settings::get("linking.posts.length", 0), Settings::get("linking.posts.orderby", 'rand'));

        if (count($posts) > 0) {

            $contentBlocks = parse_blocks($content);

            // get inter sections positions
            if (Settings::get("linking.posts.positions.inter_sections", false)) {
                $positions = $this->findInterSectionsIndex($contentBlocks);
            } else {
                $positions = [];
            }

            // add top position
            if (Settings::get("linking.posts.positions.top", false)) {
                $positions = Arr::prepend($positions, 0);
            }

            // add bottom position
            if (Settings::get("linking.posts.positions.bottom", false) || empty($positions)) {
                $positions[] = count($contentBlocks);
            }

            if (count($positions) > 0) {

                $chunks = (new Collection($posts))->chunk(ceil(count($posts) / count($positions)))->toArray();

                foreach ($chunks as $index => $chunkPosts) {
                    $position = $positions[$index];

                    $template = $this->createTemplate(Settings::get("linking.posts.template", []), $chunkPosts);
                    $blocks = parse_blocks($template->display());

                    $contentBlocks = array_merge(array_slice($contentBlocks, 0, $position), $blocks, array_slice($contentBlocks, $position));

                    // increase others positions
                    for ($i = $index + 1; $i < count($positions); $i++) {
                        $positions[$i] = $positions[$i] + count($blocks);
                    }
                }
            }

            $contentBlocks = $this->fixClassicBlocks($contentBlocks);
            $content = serialize_blocks($contentBlocks);
        }

        return $content;
    }

    private function handlePageLinking(string $content): string
    {
        // verify that the pages linking is enabled
        if (!Settings::get("linking.pages.enabled", false)) {
            return $content;
        }

        $posts = $this->getRelatedPosts(Settings::get("linking.pages.sources", []), Settings::get("linking.pages.length", 0));

        if (count($posts) > 0) {

            $contentBlocks = parse_blocks($content);

            // get inter sections positions
            if (Settings::get("linking.pages.positions.inter_sections", false)) {
                $positions = $this->findInterSectionsIndex($contentBlocks);
            } else {
                $positions = [];
            }

            // add top position
            if (Settings::get("linking.pages.positions.top", false)) {
                $positions = Arr::prepend($positions, 0);
            }

            // add bottom position
            if (Settings::get("linking.pages.positions.bottom", false) || empty($positions)) {
                $positions[] = count($contentBlocks);
            }

            if (count($positions) > 0) {

                $chunks = (new Collection($posts))->chunk(ceil(count($posts) / count($positions)))->toArray();

                foreach ($chunks as $index => $chunkPosts) {
                    $position = $positions[$index];

                    $template = $this->createTemplate(Settings::get("linking.pages.template", []), $chunkPosts);
                    $blocks = parse_blocks($template->display());

                    $contentBlocks = array_merge(array_slice($contentBlocks, 0, $position), $blocks, array_slice($contentBlocks, $position));

                    // increase others positions
                    for ($i = $index + 1; $i < count($positions); $i++) {
                        $positions[$i] = $positions[$i] + count($blocks);
                    }
                }
            }

            $contentBlocks = $this->fixClassicBlocks($contentBlocks);
            $content = serialize_blocks($contentBlocks);
        }

        return $content;
    }

    private function getRelatedPosts(array $relations, int $amount = 0, string $orderby = 'rand', string $order = 'DESC')
    {
        $posts = [];

        // parent
        if (Arr::get($relations, "parent", true) && $this->post->post_parent !== 0) {
            if ($amount === 0 || count($posts) < $amount) {
                $attrs = [
                    'post_type' => 'page',
                    'posts_per_page' => 1,
                    'p' => $this->post->post_parent,
                    'post__not_in' => array_keys($posts),
                ];
                $query = new WP_Query($attrs);
                foreach ($query->posts as $post) {
                    $posts[$post->ID] = $post;
                }
            }
        }

        // children
        if (Arr::get($relations, "children", true)) {
            if ($amount === 0 || count($posts) < $amount) {
                $attrs = [
                    'post_type' => 'page',
                    'posts_per_page' => $amount === 0 ? -1 : $amount - count($posts),
                    'post_parent' => $this->post->ID,
                    'post__not_in' => array_keys($posts),
                    'order' => "ASC",
                    'orderby' => "date",
                ];

                if ($amount === 0) {
                    $attrs['posts_per_page'] = -1;
                }

                $query = new WP_Query($attrs);
                foreach ($query->posts as $post) {
                    $posts[$post->ID] = $post;
                }
            }
        }

        // sisters
        if (Arr::get($relations, "sisters", true) && $this->post->post_parent !== 0) {
            if ($amount === 0 || count($posts) < $amount) {
                $attrs = [
                    'post_type' => 'page',
                    'posts_per_page' => $amount === 0 ? -1 : $amount - count($posts),
                    'post_parent' => $this->post->post_parent,
                    'post__not_in' => array_merge(array_keys($posts), [$this->post->ID]),
                    'order' => "ASC",
                    'orderby' => "date",
                ];

                if ($amount === 0) {
                    $attrs['posts_per_page'] = -1;
                }

                $query = new WP_Query($attrs);
                foreach ($query->posts as $post) {
                    $posts[$post->ID] = $post;
                }
            }
        }

        // categories
        if (Arr::get($relations, "categories", true)) {
            if ($amount === 0 || count($posts) < $amount) {
                $categories = get_the_category($this->post);
                if (count($categories) > 0) {

                    $attrs = [
                        'post_type' => 'post',
                        'posts_per_page' => $amount === 0 ? -1 : $amount - count($posts),
                        'order' => $order,
                        'orderby' => $orderby,
                        'post__not_in' => array_merge(array_keys($posts), [$this->post->ID]),
                        'category__in' => array_map(function ($category) {
                            return $category->term_id;
                        }, $categories)
                    ];

                    if ($amount === 0) {
                        $attrs['posts_per_page'] = -1;
                    }

                    $query = new WP_Query($attrs);
                    foreach ($query->posts as $post) {
                        $posts[$post->ID] = $post;
                    }
                }
            }
        }

        if (Arr::get($relations, "tags", true)) {
            if ($amount === 0 || count($posts) < $amount) {
                $tags = get_the_tags();
                if ($tags !== false) {

                    $attrs = [
                        'post_type' => 'post',
                        'posts_per_page' => $amount === 0 ? -1 : $amount - count($posts),
                        'order' => $order,
                        'orderby' => $orderby,
                        'post__not_in' => array_merge(array_keys($posts), [$this->post->ID]),
                        'tag__in' => array_map(function ($tag) {
                            return $tag->term_id;
                        }, $tags)
                    ];

                    if ($amount === 0) {
                        $attrs['posts_per_page'] = -1;
                    }

                    $query = new WP_Query($attrs);
                    foreach ($query->posts as $post) {
                        $posts[$post->ID] = $post;
                    }
                }
            }
        }

        return $posts;
    }

    private function createTemplate(array $template = [], array $posts = []): Template
    {
        switch (Arr::get($template, "display_mode", "inline")) {
            case "grid":
                return new GridTemplate($posts, Arr::get($template, "elements", []), Arr::get($template, "title", []), Arr::get($template, "theme", []), Arr::get($template, "settings.grid", []));
            case "inline":
            default:
                return new InlineTemplate($posts, Arr::get($template, "elements", []), Arr::get($template, "title", []), Arr::get($template, "theme", []), Arr::get($template, "settings.inline", []));
        }
    }

    private function findInterSectionsIndex(array $blocks)
    {
        $indexes = [];
        foreach ($blocks as $index => $block) {
            if (Arr::get($block, "blockName") === "core/heading" && Arr::get($block, "attrs.level", 2) === 2) {
                $indexes[] = $index;
            }
        }

        array_shift($indexes);

        return $indexes;
    }

    private function fixClassicBlocks($blocks)
    {
        // run through all the blocks
        foreach ($blocks as $blockIndex => $block) {

            // catch only null blocks
            if (Arr::get($block, "blockName") === null) {

                // run through innerContent array
                foreach (Arr::get($block, "innerContent") as $innerContentIndex => $innerContent) {

                    // replace break lines
                    if (trim($innerContent) > 0 && !in_array($innerContent, ["\r\n", "\n\r", "\n"])) {
                        $pattern = '/((?:\\r)?\\n)/i';
                        $innerContent = preg_replace($pattern, "<br />", $innerContent);
                    }

                    // update the block value
                    Arr::set($blocks, $blockIndex . ".innerContent." . $innerContentIndex, $innerContent);
                }
            }

            // if the block has children, run for children
            if (count(Arr::get($block, "innerBlocks", [])) > 0) {
                Arr::set($blocks, $blockIndex . ".innerBlocks", $this->fixClassicBlocks(Arr::get($block, "innerBlocks")));
            }
        }

        return $blocks;
    }
}
