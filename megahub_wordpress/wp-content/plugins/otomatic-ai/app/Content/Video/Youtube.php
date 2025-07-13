<?php

namespace OtomaticAi\Content\Video;

use OtomaticAi\Content\Contracts\ShouldDisplay;
use OtomaticAi\Vendors\Illuminate\Support\Arr;

class Youtube implements ShouldDisplay
{
    const KEY = "video-youtube";

    public $id;
    public $title;
    public $description;

    public function __construct($id, $title = "", $description = "")
    {
        $this->id = $id;
        $this->title = $title;
        $this->description = $description;
    }

    public function display()
    {
        $html = [];

        $html[] = '<!-- wp:embed {"url":"https://www.youtube.com/watch?v=' . $this->id . '","type":"video","providerNameSlug":"youtube","responsive":true,"className":"wp-embed-aspect-16-9 wp-has-aspect-ratio"} -->';
        $html[] = '<figure class="wp-block-embed is-type-video is-provider-youtube wp-block-embed-youtube wp-embed-aspect-16-9 wp-has-aspect-ratio">';
        $html[] = '<div class="wp-block-embed__wrapper">';
        $html[] = 'https://www.youtube.com/watch?v=' . $this->id;
        $html[] = '</div>';
        $html[] = '</figure>';
        $html[] = '<!-- /wp:embed -->';

        return implode("\n", $html);
    }

    public function toText()
    {
        return "";
    }

    public function toArray()
    {
        return [
            "key" => self::KEY ?? "",
            "id" => $this->id,
            "title" => $this->title,
            "description" => $this->description,
        ];
    }

    static public function fromArray($array)
    {
        return new self(Arr::get($array, "id"), Arr::get($array, "title"), Arr::get($array, "description"));
    }
}
