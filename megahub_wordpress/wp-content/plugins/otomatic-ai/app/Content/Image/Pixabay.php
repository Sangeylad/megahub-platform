<?php

namespace OtomaticAi\Content\Image;

use OtomaticAi\Utils\Image as UtilsImage;
use OtomaticAi\Vendors\Illuminate\Support\Arr;

class Pixabay extends Image
{
    const KEY = "image-pixabay";

    public $src;

    public function __construct($src, $title, $description = null, $legend = null)
    {
        parent::__construct(UtilsImage::fromUrl($src), $title, $description, $legend);

        $this->src = $src;
    }

    public function toArray()
    {
        return [
            "key" => self::KEY ?? "",
            "src" => $this->src,
            "title" => $this->title,
            "description" => $this->description,
            "legend" => $this->legend,
        ];
    }

    static public function fromArray($array)
    {
        return new self(Arr::get($array, "src"), Arr::get($array, "title"), Arr::get($array, "description"), Arr::get($array, "legend"));
    }
}
