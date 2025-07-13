<?php

namespace OtomaticAi\Content\Image;

use OtomaticAi\Content\Contracts\ShouldDisplay;

abstract class Image implements ShouldDisplay
{
    public $image;
    public $title;
    public $description;
    public $legend;

    public function __construct($image, $title, $description = null, $legend = null)
    {
        $this->image = $image;
        $this->title = $title;
        $this->description = $description;
        $this->legend = $legend;
    }

    public function display()
    {
        $html = [];

        if (($attachementId = $this->image->save($this->title, $this->description, $this->legend)) !== null) {
            $html[] = '<!-- wp:image {"id":' . $attachementId . ',"sizeSlug":"full"} -->';
            $html[] = "<figure class='wp-block-image size-full'>";
            $html[] = wp_get_attachment_image($attachementId, "full");
            if (!empty($this->legend)) {
                $html[] = "<figcaption class='wp-element-caption'>";
                $html[] = $this->legend;
                $html[] = "</figcaption>";
            }
            $html[] = "</figure>";
            $html[] = "<!-- /wp:image -->";
        }

        return implode("\n", $html);
    }

    public function toText()
    {
        return "";
    }

    static public function fromArray($array)
    {
        switch ($array["key"]) {
            case "image-stable-diffusion":
                return StableDiffusion::fromArray($array);
            case "image-dall-e":
                return DallE::fromArray($array);
            case "image-unsplash":
                return Unsplash::fromArray($array);
            case "image-pexels":
                return Pexels::fromArray($array);
            case "image-pixabay":
                return Pixabay::fromArray($array);
            case "image-google-image":
                return GoogleImage::fromArray($array);
            case "image-bing-image":
                return BingImage::fromArray($array);
        }
    }
}
