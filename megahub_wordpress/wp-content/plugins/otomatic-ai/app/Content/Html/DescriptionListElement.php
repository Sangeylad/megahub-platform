<?php

namespace OtomaticAi\Content\Html;

use OtomaticAi\Content\Contracts\ShouldDisplay;
use OtomaticAi\Utils\Crawler;
use OtomaticAi\Vendors\Illuminate\Support\Arr;

class DescriptionListElement implements ShouldDisplay
{
    const KEY = "html-description-list-element";

    public $elements;

    public function __construct($elements = [])
    {
        $this->elements = $elements;
    }

    public function addElement($type, $content)
    {
        $this->elements[] = ["type" => $type, "content" => $content];
    }

    public function display()
    {
        $html = [];

        if (count($this->elements) > 0) {
            $html[] = '<!-- wp:html -->';
            $html[] = '<dl>';
            foreach ($this->elements as $element) {
                $html[] = '<' . $element['type'] . '>' . $element['content'] . '</' . $element['type'] . '>';
            }
            $html[] = '</dl>';
            $html[] = '<!-- /wp:html -->';
        }

        return implode("\n", $html);
    }

    public function toText()
    {
        $parts = [];
        foreach ($this->elements as $element) {
            $parts[] = $element['content'];
        }

        return implode("\n", $parts);
    }

    static public function make($html)
    {
        $crawler = new Crawler($html);

        if ($crawler->filter("dl")->count() > 0) {
            $node = $crawler->filter("dl")->first();

            $descriptionList = new self();

            foreach ($node->filter('dt,dd') as $el) {
                $el = new Crawler($el);
                $descriptionList->addElement($el->nodeName(), $el->html());
            }

            return $descriptionList;
        }

        return null;
    }

    public function toArray()
    {
        return [
            "key" => self::KEY ?? "",
            "elements" => $this->elements,
        ];
    }

    static public function fromArray($array)
    {
        return new self(Arr::get($array, "elements", []));
    }
}
