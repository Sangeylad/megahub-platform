<?php

namespace OtomaticAi\Content\Html;

use OtomaticAi\Content\Contracts\ShouldDisplay;
use OtomaticAi\Utils\Crawler;
use OtomaticAi\Vendors\Illuminate\Support\Arr;

class ListElement implements ShouldDisplay
{
    const KEY = "html-list-element";

    public $type;
    public $elements;

    public function __construct($type = "ul", $elements = [])
    {
        $this->type = $type;
        $this->elements = $elements;
    }

    public function addElement($element)
    {
        $this->elements[] = $element;
    }

    public function display()
    {
        $html = [];

        if (count($this->elements) > 0) {
            $html[] = '<!-- wp:list ' . ($this->type === 'ol' ? '{"ordered":true} ' : '') . '-->';
            $html[] = "<" . $this->type . ">";
            foreach ($this->elements as $element) {
                $html[] = "<!-- wp:list-item -->";
                $html[] = "<li>" . $element . "</li>";
                $html[] = "<!-- /wp:list-item -->";
            }
            $html[] = "</" . $this->type . ">";
            $html[] = '<!-- /wp:list -->';
        }

        return implode("\n", $html);
    }

    public function toText()
    {
        return implode("\n", $this->elements);
    }

    static public function make($html)
    {
        $crawler = new Crawler($html);

        if ($crawler->filter("ul,ol")->count() > 0) {
            $node = $crawler->filter("ul,ol")->first();
            $list = new self($node->nodeName());

            foreach ($node->filter("li") as $el) {
                $el = new Crawler($el);
                $list->addElement($el->html());
            }

            return $list;
        }

        return null;
    }

    public function toArray()
    {
        return [
            "key" => self::KEY ?? "",
            "type" => $this->type,
            "elements" => $this->elements,
        ];
    }

    static public function fromArray($array)
    {
        return new self(Arr::get($array, "type", "ul"), Arr::get($array, "elements", []));
    }
}
