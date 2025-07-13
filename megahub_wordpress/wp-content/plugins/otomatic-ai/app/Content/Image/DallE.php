<?php

namespace OtomaticAi\Content\Image;

use OtomaticAi\Utils\Image as UtilsImage;
use OtomaticAi\Vendors\Illuminate\Support\Arr;

class DallE extends Image
{
    const KEY = "image-dall-e";

    public $base64;

    public function __construct($base64, $title, $description = null, $legend = null)
    {
        parent::__construct(UtilsImage::fromBase64($base64), $title, $description, $legend);

        $this->base64 = $base64;
    }

    public function toArray()
    {
        return [
            "key" => self::KEY ?? "",
            "base64" => $this->base64,
            "title" => $this->title,
            "description" => $this->description,
            "legend" => $this->legend,
        ];
    }

    static public function fromArray($array)
    {
        return new self(Arr::get($array, "base64"), Arr::get($array, "title"), Arr::get($array, "description"), Arr::get($array, "legend"));
    }
}
