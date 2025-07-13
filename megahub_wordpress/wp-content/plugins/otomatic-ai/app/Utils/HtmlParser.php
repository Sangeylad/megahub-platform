<?php

namespace OtomaticAi\Utils;

use OtomaticAi\Content\Html\BlockquoteElement;
use OtomaticAi\Content\Html\CodeElement;
use OtomaticAi\Content\Html\DescriptionListElement;
use OtomaticAi\Content\Html\ListElement;
use OtomaticAi\Content\Html\ParagraphElement;
use OtomaticAi\Content\Html\TableElement;
use OtomaticAi\Content\Section;
use OtomaticAi\Content\SectionCollection;
use OtomaticAi\Vendors\Illuminate\Support\Arr;
use OtomaticAi\Vendors\Illuminate\Support\Str;
use OtomaticAi\Vendors\League\CommonMark\CommonMarkConverter;

class HtmlParser
{
    private $availableNodes = [
        "h2", "h3", "h4", "h5", "h6", "p", "ul", "ol", "table", "blockquote", "dl", "code"
    ];

    private $crawler;

    public function __construct($html)
    {
        $html = $this->convertMarkdown($html);
        $html = $this->fixMissingParagraphes($html);

        $this->crawler = new Crawler($html);
    }

    public function getSections(array $config = [])
    {
        $sections = new SectionCollection([new Section()]);
        $key = [];

        $config = array_merge([
            "keep_titles" => true,
            "blacklist_titles" => [],
            "max_depth" => 2,
        ], $config);
        $config["blacklist_titles"] = array_map(function ($title) {
            return Str::lower($title);
        }, $config["blacklist_titles"]);

        foreach ($this->crawler->filter(implode(",", $this->availableNodes)) as $node) {

            // hn
            if (preg_match('/h([\d+])/i', $node->nodeName, $matches)) {

                // skip if keep_title is disabled
                if (!$config["keep_titles"]) {
                    continue;
                }

                // get depth and skip h1
                $depth = intval($matches[1]);
                if ($depth <= 1) {
                    continue;
                }

                $title = Footprint::clear($node->textContent);

                // verify that the title is not empty
                if (empty($title)) {
                    continue;
                }

                // remove blacklisted titles
                if (in_array(Str::lower($title), $config["blacklist_titles"])) {
                    continue;
                }

                // sub 2 to depth to set h2 as 0
                $depth = $depth - 2;

                // normalize $depth to fix missing depth
                $depth = min(count($key), $depth);
                $depth = min($depth, $config["max_depth"]);

                if ($depth < count($key) - 1) {
                    $key = array_slice($key, 0, $depth + 1);
                }

                // set 0 if the $depth not exist in $key
                if (!isset($key[$depth])) {
                    $key[$depth] = 0;
                }

                $key[$depth] = $key[$depth] + 1;

                $sections->put(implode(".", $key), new Section($title));

                // add the title to blacklist
                $config["blacklist_titles"][] = Str::lower($title);
            }
            // other
            else {

                $nodeName = $node->nodeName;
                $node = new Crawler($node);
                if (!$sections->has(implode(".", $key))) {
                    $sections->put(implode(".", $key), new Section());
                }

                switch ($nodeName) {
                    case 'p':
                        if ($node->closest($this->makeClosestSelector("p")) === null) {
                            $sections->get(implode(".", $key))->addElement(
                                ParagraphElement::make($this->addMissingLineBreak($node->outerHtml()))
                            );
                        }
                        break;
                    case 'ul':
                    case 'ol':
                        if ($node->closest($this->makeClosestSelector(["ul", "ol"])) === null) {
                            $sections->get(implode(".", $key))->addElement(
                                ListElement::make($node->outerHtml())
                            );
                        }
                        break;
                    case 'table':
                        if ($node->closest($this->makeClosestSelector("table")) === null) {
                            $sections->get(implode(".", $key))->addElement(
                                TableElement::make($node->outerHtml())
                            );
                        }
                        break;
                    case 'blockquote':
                        if ($node->closest($this->makeClosestSelector("blockquote")) === null) {
                            $sections->get(implode(".", $key))->addElement(
                                BlockquoteElement::make($node->outerHtml())
                            );
                        }
                        break;
                    case 'dl':
                        if ($node->closest($this->makeClosestSelector("dl")) === null) {
                            $sections->get(implode(".", $key))->addElement(
                                DescriptionListElement::make($node->outerHtml())
                            );
                        }
                        break;
                    case 'code':
                        if ($node->closest($this->makeClosestSelector("code")) === null) {
                            $sections->get(implode(".", $key))->addElement(
                                CodeElement::make($node->outerHtml())
                            );
                        }
                        break;
                }
            }
        }

        // filter empty sections
        $sections = $sections->filter(function ($section) {
            return !$section->isEmpty();
        });

        // reverse sections to start by the end
        $sections = $sections->reverse();

        // put children sections in parent sections
        $sections->each(function ($section, $key) use (&$sections) {
            $keys = explode(".", $key);
            $parentKey = $keys;
            array_pop($parentKey);
            $parentKey = implode(".", $parentKey);
            if (count($keys) > 1 && $sections->has($parentKey)) {
                $sections->get($parentKey)->addChild($section, false);
            }
        });

        // reverse sections to get original order
        $sections = $sections->reverse();

        // keep only depth 0 sections
        $sections = $sections->filter(function ($section, $key) {
            return count(explode(".", $key)) === 1;
        });

        return $sections->values();
    }

    public function filter($selector)
    {
        return $this->crawler->filter($selector);
    }

    private function convertMarkdown($content)
    {
        $content = preg_replace('/^```html/i', '', $content);
        $content = preg_replace('/```$/i', '', $content);
        $content = preg_replace('/\*\*(.*?)\*\*/i', '<strong>${1}</strong>', $content);

        return $content;
    }

    private function fixMissingParagraphes($content)
    {
        $tags = ["h2", "h3", "h4", "h5", "h6", "ul", "ol", "table", "blockquote", "dl", "code"];

        if (!empty($content)) {
            // start content
            if (!Str::startsWith($content, '<')) {
                $content = "<p>" . $content;
            }

            // open tag
            $searches = implode('|', array_map(function ($tag) {
                return "<\\/" . $tag . ">";
            }, $tags));
            $regex = "/(" . $searches . ")[^<]/";
            $content = preg_replace_callback($regex, function ($matches) {
                return $matches[1] . "<p>" . str_replace($matches[1], '', $matches[0]);
            }, $content);

            // end tag
            $searches = implode('|', array_map(function ($tag) {
                return "<" . $tag;
            }, $tags));
            $regex = "/[^<](" . $searches . ")/";
            $content = preg_replace_callback($regex, function ($matches) {
                return str_replace($matches[1], '', $matches[0]) . "</p>" . $matches[1];
            }, $content);

            // start content
            if (!Str::endsWith($content, '>')) {
                $content = $content . '</p>';
            }
        }
        return $content;
    }

    private function addMissingLineBreak($content)
    {
        return str_replace("\n", "<br>", $content);
    }

    private function makeClosestSelector($node)
    {
        $selectors = array_combine($this->availableNodes, $this->availableNodes);
        Arr::forget($selectors, $node);

        return implode(",", array_values($selectors));
    }
}
