<?php

namespace OtomaticAi\Content\Html;

use OtomaticAi\Content\Contracts\ShouldDisplay;
use OtomaticAi\Utils\Crawler;
use OtomaticAi\Vendors\Illuminate\Support\Arr;

class BlockquoteElement implements ShouldDisplay
{
    const KEY = "html-blockquote-element";

    public $content;
    public $source;

    public function __construct($content = null, $source = null)
    {
        $this->content = $content;
        $this->source = $source;
    }

    public function display()
    {
        $html = [];

        if ($this->content !== null) {
            $html[] = '<!-- wp:quote -->';
            $html[] = '<blockquote class="wp-block-quote">';
            $html[] = '<!-- wp:paragraph -->';
            $html[] = '<p>' . $this->content . '</p>';
            if ($this->source !== null) {
                $html[] = '<cite>' . $this->source . '</cite>';
            }
            $html[] = '<!-- /wp:paragraph -->';
            $html[] = '</blockquote>';
            $html[] = '<!-- /wp:quote -->';
        }

        return implode("\n", $html);
    }

    public function toText()
    {
        return $this->content;
    }

    static public function make($html)
    {
        $crawler = new Crawler($html);

        if ($crawler->filter("blockquote")->count() > 0) {
            $node = $crawler->filter("blockquote")->first();

            if ($node->filter("p")->count() > 0) {

                $blockquote = new self($node->filter("p")->html());

                // cite
                if ($node->filter("cite")->count() > 0) {
                    $blockquote->source = $node->filter("cite")->html();
                }

                return $blockquote;
            }
        }

        return null;
    }

    public function toArray()
    {
        return [
            "key" => self::KEY ?? "",
            "content" => $this->content,
            "source" => $this->source,
        ];
    }

    static public function fromArray($array)
    {
        return new self(Arr::get($array, "content"), Arr::get($array, "source"));
    }
}
