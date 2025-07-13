<?php

namespace OtomaticAi\Utils\Linking;

use OtomaticAi\Models\Linking as LinkingModel;
use OtomaticAi\Vendors\Illuminate\Support\Arr;
use OtomaticAi\Vendors\Illuminate\Support\Str;
use WP_Post;

class ManualLinking
{
    private WP_Post $post;
    private array $counters = [];

    public function __construct($post)
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
        // get the list of keyword => url
        $keywords = LinkingModel::byKeywords();

        // add links to the parsed blocks
        $contentBlocks = parse_blocks($content);
        $contentBlocks = $this->addManualLinks($contentBlocks, $keywords);

        // recreate html from updated parsed blocks
        $content = serialize_blocks($contentBlocks);

        return $content;
    }

    private function addManualLinks($blocks, $keywords)
    {
        // run through all the blocks
        foreach ($blocks as $blockIndex => $block) {

            // catch only specific blocks
            if (in_array(Arr::get($block, "blockName"), ["core/paragraph", "core/list-item"])) {

                // run through innerContent array
                foreach (Arr::get($block, "innerContent") as $innerContentIndex => $innerContent) {

                    $inserted = false;

                    // replace keywords with regex
                    foreach ($keywords as $keyword => $link) {

                        // reject if the link is the current permalink
                        if ($this->isCurrentPost($link->url)) {
                            continue;
                        }

                        // reject if the post_type is incorrect
                        if (!in_array(get_post_type($this->post), $link->post_types)) {
                            continue;
                        }

                        // quit if max_links is exceeded
                        if ($this->isMaxLinksExceeded($link)) {
                            continue;
                        }

                        // create the pattern
                        $pattern = '/\b(' . $keyword . ')\b/iu';

                        if ($link->is_obfuscate) {
                            $href = base64_encode($link->url);
                            $html = [];
                            $id = Str::random(8);
                            $html[] = '<span id="' . $id . '" data="' . $href . '" style="cursor: pointer;">${1}</span>';
                            $html[] = '<script>';
                            if ($link->is_blank) {
                                $html[] = 'document.querySelector("#' . $id . '").addEventListener("click", function(e){window.open(atob(e.currentTarget.getAttribute("data")));})';
                            } else {
                                $html[] = 'document.querySelector("#' . $id . '").addEventListener("click", function(e){document.location.href = atob(e.currentTarget.getAttribute("data"));})';
                            }
                            $html[] = '</script>';
                            $replacement = implode("", $html);
                        } else {
                            // create the link and attributes
                            $attributes = ["href" =>  $link->url];
                            if ($link->is_blank) {
                                $attributes["target"] = "_blank";
                            }
                            if (!$link->is_follow) {
                                $attributes["rel"] = "nofollow";
                            }
                            $attributes = implode(" ", array_map(function ($val, $key) {
                                return $key . "=" . '"' . $val . '"';
                            }, array_values($attributes), array_keys($attributes)));
                            $replacement = '<a ' . $attributes . '>${1}</a>';
                        }

                        // replace the keyword
                        $innerContent = preg_replace($pattern, $replacement, $innerContent, 1, $count);

                        if ($count > 0) {
                            $this->increaseMaxLinks($link, $count);

                            $inserted = true;
                            break;
                        }
                    }

                    // update the block value
                    if ($inserted) {
                        Arr::set($blocks, $blockIndex . ".innerContent." . $innerContentIndex, $innerContent);
                        break;
                    }
                }
            }

            // if the block has children, run for children
            if (count(Arr::get($block, "innerBlocks", [])) > 0) {
                Arr::set($blocks, $blockIndex . ".innerBlocks", $this->addManualLinks(Arr::get($block, "innerBlocks"), $keywords));
            }
        }

        return $blocks;
    }

    private function isMaxLinksExceeded(LinkingModel $link)
    {
        if ($link->max_links === 0) {
            return false;
        }

        return Arr::get($this->counters, $link->id, 0) >= $link->max_links;
    }

    private function increaseMaxLinks(LinkingModel $link, int $counter = 1)
    {
        Arr::set($this->counters, $link->id, Arr::get($this->counters, $link->id, 0) + $counter);
    }

    private function isCurrentPost(string $url)
    {
        $permalink = parse_url(get_permalink($this->post), PHP_URL_HOST) . parse_url(get_permalink($this->post), PHP_URL_PATH);
        $permalink = Str::finish($permalink, '/');
        $permalink = Str::lower($permalink);

        $url = parse_url($url, PHP_URL_HOST) . parse_url($url, PHP_URL_PATH);
        $url = Str::finish($url, '/');
        $url = Str::lower($url);

        return $url == $permalink;
    }
}
