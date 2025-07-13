<?php

namespace OtomaticAi\Content;

use OtomaticAi\Content\Contracts\ShouldDisplay;
use OtomaticAi\Vendors\Illuminate\Support\Collection;

class SectionCollection extends Collection implements ShouldDisplay
{
    const KEY = "section-collection";

    public function display($depth = 0)
    {
        $html = [];

        $this->each(function ($section) use (&$html, $depth) {
            $html[] = $section->display($depth);
        });

        return implode("\n", $html);
    }

    public function toText()
    {
        $parts = [];

        $this->each(function ($section) use (&$parts) {
            $parts[] = $section->toText();
        });

        return implode("\n", $parts);
    }

    public function toArray()
    {
        return [
            "key" => self::KEY ?? "",
            "items" => array_map(fn ($el) => $el->toArray(), $this->items),
        ];
    }

    static public function fromArray($array)
    {
        $collection = new self();
        foreach ($array["items"] as $arr) {
            $collection->push(Section::fromArray($arr));
        }
        return $collection;
    }
}
