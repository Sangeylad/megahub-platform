<?php

namespace OtomaticAi\Utils\RSS;

use OtomaticAi\Vendors\GuzzleHttp\Client;

class Reader
{
    /** @var SimpleXMLElement */
    protected $xml;

    /** @var Item[] */
    public $items;

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
     * Loads RSS or Atom feed.
     * @param  string
     * @param  string
     * @param  string
     * @return Reader
     */
    static public function load($url, $user = null, $pass = null)
    {
        $xml = self::loadXml($url, $user, $pass);
        if ($xml->channel) {
            return self::fromRss($xml);
        } else {
            return self::fromAtom($xml);
        }
        return $xml;
    }

    /**
     * Loads RSS feed.
     * @param  string  RSS feed URL
     * @param  string  optional user name
     * @param  string  optional password
     * @return Reader
     * @throws ReaderException
     */
    static public function loadRss($url, $user = null, $pass = null)
    {
        return self::fromRss(self::loadXml($url, $user, $pass));
    }


    /**
     * Loads Atom feed.
     * @param  string  Atom feed URL
     * @param  string  optional user name
     * @param  string  optional password
     * @return Reader
     * @throws ReaderException
     */
    static public function loadAtom($url, $user = null, $pass = null)
    {
        return self::fromAtom(self::loadXml($url, $user, $pass));
    }

    private static function fromRss($xml)
    {
        if (!$xml->channel) {
            throw new ReaderException('Invalid feed.');
        }

        self::adjustNamespaces($xml);
        $items = [];
        foreach ($xml->channel->item as $item) {

            // converts namespaces to dotted tags
            self::adjustNamespaces($item);

            // generate 'url' & 'timestamp' tags
            $item->url = (string) $item->link;
            if (isset($item->{'dc:date'})) {
                $item->timestamp = strtotime($item->{'dc:date'});
            } elseif (isset($item->pubDate)) {
                $item->timestamp = strtotime($item->pubDate);
            }

            $items[] = new Item($item);
        }
        $feed = new self;
        $feed->xml = $xml->channel;
        $feed->items = $items;

        return $feed;
    }

    private static function fromAtom($xml)
    {
        if (
            !in_array('http://www.w3.org/2005/Atom', $xml->getDocNamespaces(), true)
            && !in_array('http://purl.org/atom/ns#', $xml->getDocNamespaces(), true)
        ) {
            throw new ReaderException('Invalid feed.');
        }

        // generate 'url' & 'timestamp' tags
        $items = [];
        foreach ($xml->entry as $entry) {
            $entry->url = (string) $entry->link['href'];
            $entry->timestamp = strtotime($entry->updated);

            $items[] = new Item($entry);
        }
        $feed = new self;
        $feed->xml = $xml;
        $feed->items = $items;

        return $feed;
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

    /**
     * Load XML from HTTP.
     * @param  string
     * @param  string
     * @param  string
     * @return \SimpleXMLElement
     * @throws ReaderException
     */
    static private function loadXml($url, $user, $pass)
    {
        try {
            $client = new Client();
            $response = $client->get($url);
            $content = $response->getBody()->getContents();
            return new \SimpleXMLElement($content, LIBXML_NOWARNING | LIBXML_NOERROR | LIBXML_NOCDATA);
        } catch (\Exception $e) {
            throw new ReaderException('Cannot load feed.');
        }
    }

    /**
     * Generates better accessible namespaced tags.
     * @param  SimpleXMLElement
     * @return void
     */
    private static function adjustNamespaces($el)
    {
        foreach ($el->getNamespaces(true) as $prefix => $ns) {
            $children = $el->children($ns);
            foreach ($children as $tag => $content) {
                $el->{$prefix . ':' . $tag} = $content;
            }
        }
    }
}
