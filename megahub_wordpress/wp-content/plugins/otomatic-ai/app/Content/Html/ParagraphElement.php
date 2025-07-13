<?php

namespace OtomaticAi\Content\Html;

use OtomaticAi\Content\Contracts\ShouldDisplay;
use OtomaticAi\Utils\Crawler;
use OtomaticAi\Vendors\Illuminate\Support\Arr;

class ParagraphElement implements ShouldDisplay
{
    const KEY = "html-paragraph-element";

    public $content;

    public function __construct($content)
    {
        $this->content = $content;
    }

    public function display()
    {
        $html = [];

        $html[] = "<!-- wp:paragraph -->";
        $html[] = '<p>' . $this->content . '</p>';
        $html[] = "<!-- /wp:paragraph -->";

        return implode("\n", $html);
    }

    public function toText()
    {
        return $this->content;
    }

    static public function make($html)
    {
        $crawler = new Crawler($html);

        if ($crawler->filter("p")->count() > 0) {

            // get the p body
            $body = trim($crawler->filter("p")->html());

            // remove unnecessary <br>
            $body = preg_replace('/^(<br\s?\/?>)+/i', '', $body);
            $body = preg_replace('/(<br\s?\/?>)+$/i', '', $body);
            $body = preg_replace('/(<br\s?\/?>)+/i', '<br>', $body);

            if (!empty(trim($body))) {

                $paragraph = new self($body);

                return $paragraph;
            }
        }

        return null;
    }

    public function toArray()
    {
        return [
            "key" => self::KEY ?? "",
            "content" => $this->content,
        ];
    }

    static public function fromArray($array)
    {
        return new self(Arr::get($array, "content"));
    }
}
