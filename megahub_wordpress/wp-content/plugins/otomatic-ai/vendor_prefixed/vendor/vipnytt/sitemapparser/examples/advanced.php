<?php

namespace OtomaticAi\Vendors;

require_once \dirname(__FILE__) . "/../vendor/autoload.php";
use OtomaticAi\Vendors\vipnytt\SitemapParser;
use OtomaticAi\Vendors\vipnytt\SitemapParser\Exceptions\SitemapParserException;
/**
 * Advanced example
 */
$config = ['guzzle' => []];
try {
    $parser = new SitemapParser('MyCustomUserAgent', $config);
    $parser->parse('https://www.google.com/robots.txt');
    foreach ($parser->getSitemaps() as $url => $tags) {
        echo 'Sitemap<br>';
        echo 'URL: ' . $url . '<br>';
        echo 'LastMod: ' . $tags['lastmod'] . '<br>';
        echo '<hr>';
    }
    foreach ($parser->getURLs() as $url => $tags) {
        echo 'URL: ' . $url . '<br>';
        echo 'LastMod: ' . $tags['lastmod'] . '<br>';
        echo 'ChangeFreq: ' . $tags['changefreq'] . '<br>';
        echo 'Priority: ' . $tags['priority'] . '<br>';
        echo '<hr>';
    }
} catch (SitemapParserException $e) {
    echo $e->getMessage();
}
