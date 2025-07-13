<?php

namespace OtomaticAi\Content\Html;

use OtomaticAi\Content\Contracts\ShouldDisplay;
use OtomaticAi\Utils\Crawler;
use OtomaticAi\Vendors\Illuminate\Support\Arr;

class CodeElement implements ShouldDisplay
{
    const KEY = "html-code-element";

    public $content;

    public function __construct($content = null)
    {
        $this->content = $content;
    }

    public function display()
    {
        $html = [];

        if ($this->content !== null) {
            $html[] = '<!-- wp:code -->';
            $html[] = '<pre class="wp-block-code">';
            $html[] = '<code>';
            $html[] = $this->content;
            $html[] = '</code>';
            $html[] = '</pre>';
            $html[] = '<!-- /wp:code -->';
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

        if ($crawler->filter("code")->count() > 0) {

            $code = new self($crawler->filter("code")->html());

            return $code;
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
