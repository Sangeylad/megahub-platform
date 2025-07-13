<?php

namespace OtomaticAi\Content\Social;

use OtomaticAi\Content\Contracts\ShouldDisplay;
use OtomaticAi\Vendors\Illuminate\Support\Arr;

class Twitter implements ShouldDisplay
{
    const KEY = "social-twitter";

    public $href;

    public function __construct($href)
    {
        $this->href = $href;
    }

    public function display()
    {
        $html = [];

        $html[] = '<!-- wp:embed {"url":"' . $this->href . '","type":"rich","providerNameSlug":"twitter","responsive":true} -->';
        $html[] = '<figure class="wp-block-embed is-type-rich is-provider-twitter wp-block-embed-twitter"><div class="wp-block-embed__wrapper">';
        $html[] = $this->href;
        $html[] = '</div></figure>';
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
            "href" => $this->href,
        ];
    }

    static public function fromArray($array)
    {
        return new self(Arr::get($array, "href"));
    }
}
