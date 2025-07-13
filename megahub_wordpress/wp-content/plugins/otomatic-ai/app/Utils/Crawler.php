<?php

namespace OtomaticAi\Utils;

use OtomaticAi\Vendors\Symfony\Component\DomCrawler\Crawler as BaseCrawler;

class Crawler extends BaseCrawler
{
    public function __construct($html = null, string $uri = null, string $baseHref = null)
    {
        if (\is_string($html)) {
            // fix
            $htmlContent = $this->convertToHtmlEntities($html, "UTF-8");
            $internalErrors = \libxml_use_internal_errors(\true);
            if (\LIBXML_VERSION < 20900) {
                $disableEntities = \libxml_disable_entity_loader(\true);
            }
            $dom = new \DOMDocument('1.0', "UTF-8");
            $dom->validateOnParse = \true;
            if ('' !== \trim($htmlContent)) {
                @$dom->loadHTML($htmlContent);
            }
            \libxml_use_internal_errors($internalErrors);
            if (\LIBXML_VERSION < 20900) {
                \libxml_disable_entity_loader($disableEntities);
            }
            // end fix

            if ($dom->documentElement) {
                parent::__construct($html, $uri, $baseHref);
            } else {
                parent::__construct($dom->childNodes, $uri, $baseHref);
            }
        } else if ($html !== null) {
            parent::__construct($html, $uri, $baseHref);
        }
    }

    private function convertToHtmlEntities(string $htmlContent, string $charset = 'UTF-8'): string
    {
        \set_error_handler(function () {
            throw new \Exception();
        });
        try {
            return \mb_encode_numericentity($htmlContent, [0x80, 0x10ffff, 0, 0x1fffff], $charset);
        } catch (\Exception | \ValueError $e) {
            try {
                $htmlContent = \iconv($charset, 'UTF-8', $htmlContent);
                $htmlContent = \mb_encode_numericentity($htmlContent, [0x80, 0x10ffff, 0, 0x1fffff], 'UTF-8');
            } catch (\Exception | \ValueError $e) {
            }
            return $htmlContent;
        } finally {
            \restore_error_handler();
        }
    }
}
