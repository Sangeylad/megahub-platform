<?php

namespace OtomaticAi\Content;

use OtomaticAi\Content\Image\StableDiffusion;
use OtomaticAi\Content\Image\Unsplash;
use OtomaticAi\Content\Contracts\ShouldDisplay;
use OtomaticAi\Content\Html\BlockquoteElement;
use OtomaticAi\Content\Html\CodeElement;
use OtomaticAi\Content\Html\DescriptionListElement;
use OtomaticAi\Content\Html\ListElement;
use OtomaticAi\Content\Html\ParagraphElement;
use OtomaticAi\Content\Html\TableElement;
use OtomaticAi\Content\Image\BingImage;
use OtomaticAi\Content\Image\DallE;
use OtomaticAi\Content\Image\GoogleImage;
use OtomaticAi\Content\Image\Pexels;
use OtomaticAi\Content\Image\Pixabay;
use OtomaticAi\Content\Social\Facebook;
use OtomaticAi\Content\Social\Instagram;
use OtomaticAi\Content\Social\Tiktok;
use OtomaticAi\Content\Social\Twitter;
use OtomaticAi\Content\Video\Youtube;
use OtomaticAi\Vendors\Illuminate\Support\Arr;

class Section implements ShouldDisplay
{
    const KEY = "section";

    public $title;
    public $elements;
    public $children;

    public function __construct($title = null, $elements = [], $children = [])
    {
        $this->title = $title;
        $this->elements = $elements;
        $this->children = $children;
    }

    public function setTitle($title)
    {
        $this->title = $title;
    }

    public function addElement($element, $end = true)
    {
        if ($element !== null) {
            if ($end) {
                $this->elements[] = $element;
            } else {
                $this->elements = Arr::prepend($this->elements, $element);
            }
        }
    }

    public function addElements(array $elements, $end = true)
    {
        if (count($elements) > 0) {
            foreach ($elements as $element) {
                $this->addElement($element, $end);
            }
        }
    }

    public function addChildren(array $sections, $end = true)
    {
        if (count($sections) > 0) {
            foreach ($sections as $section) {
                $this->addChild($section, $end);
            }
        }
    }

    public function addChild($section, $end = true)
    {
        if ($end) {
            $this->children[] = $section;
        } else {
            $this->children = Arr::prepend($this->children, $section);
        }
    }

    /**
     * Determine if the section is empty or not.
     *
     * @return boolean
     */
    public function isEmpty(): bool
    {
        return empty($this->title) && empty($this->elements) && empty($this->children);
    }

    public function display($depth = 0)
    {
        $html = [];

        // title
        if (!empty($this->title)) {
            $html[] = $this->displayTitle($depth);
        }

        // elements
        foreach ($this->elements as $element) {
            $html[] = $element->display();
        }

        $html = [implode("\n", $html)];

        // children
        foreach ($this->children as $child) {
            $html[] = $child->display($depth + 1);
        }

        return implode("\n", $html);
    }

    public function toText()
    {
        $parts = [];

        if (!empty($this->title)) {
            $parts[] = $this->title;
        }

        foreach ($this->elements as $element) {
            $parts[] = $element->toText();
        }

        foreach ($this->children as $child) {
            $parts[] = $child->toText();
        }

        return implode("\n", $parts);
    }

    private function displayTitle($depth)
    {
        $level = $depth + 2;
        $html = [];
        $html[] = '<!-- wp:heading ' . ($level !== 2 ? '{"level":' . $level . '} ' : '') . "-->";
        $html[] = '<h' . $level . '>' . $this->title . '</h' . $level . '>';
        $html[] = '<!-- /wp:heading -->';

        return implode("\n", $html);
    }

    public function toArray()
    {
        return [
            "key" => self::KEY ?? "",
            "title" => $this->title,
            "elements" => array_map(fn ($el) => $el->toArray(), $this->elements),
            "children" => array_map(fn ($el) => $el->toArray(), $this->children),
        ];
    }

    static public function fromArray($array)
    {
        $section = new self(
            Arr::get($array, "title")
        );

        foreach (Arr::get($array, "elements", []) as $el) {
            switch ($el["key"]) {
                case "html-blockquote-element":
                    $section->addElement(BlockquoteElement::fromArray($el));
                    break;
                case "html-code-element":
                    $section->addElement(CodeElement::fromArray($el));
                    break;
                case "html-description-list-element":
                    $section->addElement(DescriptionListElement::fromArray($el));
                    break;
                case "html-list-element":
                    $section->addElement(ListElement::fromArray($el));
                    break;
                case "html-paragraph-element":
                    $section->addElement(ParagraphElement::fromArray($el));
                    break;
                case "html-table-element":
                    $section->addElement(TableElement::fromArray($el));
                    break;
                case "social-facebook":
                    $section->addElement(Facebook::fromArray($el));
                    break;
                case "social-instagram":
                    $section->addElement(Instagram::fromArray($el));
                    break;
                case "social-tiktok":
                    $section->addElement(Tiktok::fromArray($el));
                    break;
                case "social-twitter":
                    $section->addElement(Twitter::fromArray($el));
                    break;
                case "video-youtube":
                    $section->addElement(Youtube::fromArray($el));
                    break;
                case "image-stable-diffusion":
                    $section->addElement(StableDiffusion::fromArray($el));
                    break;
                case "image-dall-e":
                    $section->addElement(DallE::fromArray($el));
                    break;
                case "image-unsplash":
                    $section->addElement(Unsplash::fromArray($el));
                    break;
                case "image-pexels":
                    $section->addElement(Pexels::fromArray($el));
                    break;
                case "image-pixabay":
                    $section->addElement(Pixabay::fromArray($el));
                    break;
                case "image-google-image":
                    $section->addElement(GoogleImage::fromArray($el));
                    break;
                case "image-bing-image":
                    $section->addElement(BingImage::fromArray($el));
                    break;
            }
        }
        foreach (Arr::get($array, "children", []) as $el) {
            switch ($el["key"]) {
                case "section":
                    $section->addChild(self::fromArray($el));
                    break;
                case "section-collection":
                    $section->addChildren(SectionCollection::fromArray($el)->all());
                    break;
            }

            // $section->addChild(self::fromArray($el));
        }

        return $section;
    }
}
