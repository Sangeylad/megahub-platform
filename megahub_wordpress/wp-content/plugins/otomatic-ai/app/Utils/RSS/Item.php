<?php

namespace OtomaticAi\Utils\RSS;

class Item
{
    /** @var SimpleXMLElement */
    protected $xml;

    function __construct($xml)
    {
        $this->xml = $xml;
    }

    /**
     * Returns property value. Do not call directly.
     * @param  string  tag name
     * @return SimpleXMLElement
     */
    public function __get($name)
    {
        return $this->xml->{$name};
    }

    /**
     * Sets value of a property. Do not call directly.
     * @param  string  property name
     * @param  mixed   property value
     * @return void
     */
    public function __set($name, $value)
    {
        throw new \Exception("Cannot assign to a read-only property '$name'.");
    }

    /**
     * Converts a SimpleXMLElement into an array.
     * @param  SimpleXMLElement
     * @return array
     */
    public function toArray($xml = null)
    {
        if ($xml === null) {
            $xml = $this->xml;
        }

        if (!$xml->children()) {
            return (string) $xml;
        }

        $arr = [];
        foreach ($xml->children() as $tag => $child) {
            if (count($xml->$tag) === 1) {
                $arr[$tag] = $this->toArray($child);
            } else {
                $arr[$tag][] = $this->toArray($child);
            }
        }

        return $arr;
    }
}
