<?php

namespace OtomaticAi\Content\Social;

use OtomaticAi\Content\Contracts\ShouldDisplay;
use OtomaticAi\Vendors\Illuminate\Support\Arr;

class Facebook implements ShouldDisplay
{
    const KEY = "social-facebook";

    public $href;

    public function __construct($href)
    {
        $this->href = $href;
    }

    public function display()
    {
        $html = [];

        $html[] = '<!-- wp:html -->';
        $html[] = '<div style="display: block;">';
        $html[] = '<div id="fb-root"></div>';
        $html[] = '<script async defer crossorigin="anonymous" src="https://connect.facebook.net/fr_FR/sdk.js#xfbml=1&version=v17.0"></script>';
        $html[] = '<div class="fb-post" data-href="' . $this->href . '" data-width="500" data-show-text="true"></div>';
        $html[] = '</div>';
        $html[] = '<!-- /wp:html -->';

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
            "href" => $this->href,
        ];
    }

    static public function fromArray($array)
    {
        return new self(Arr::get($array, "href"));
    }
}
