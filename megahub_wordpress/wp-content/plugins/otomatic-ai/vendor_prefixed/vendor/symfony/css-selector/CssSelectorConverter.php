<?php

/*
 * This file is part of the Symfony package.
 *
 * (c) Fabien Potencier <fabien@symfony.com>
 *
 * For the full copyright and license information, please view the LICENSE
 * file that was distributed with this source code.
 */
namespace OtomaticAi\Vendors\Symfony\Component\CssSelector;

use OtomaticAi\Vendors\Symfony\Component\CssSelector\Parser\Shortcut\ClassParser;
use OtomaticAi\Vendors\Symfony\Component\CssSelector\Parser\Shortcut\ElementParser;
use OtomaticAi\Vendors\Symfony\Component\CssSelector\Parser\Shortcut\EmptyStringParser;
use OtomaticAi\Vendors\Symfony\Component\CssSelector\Parser\Shortcut\HashParser;
use OtomaticAi\Vendors\Symfony\Component\CssSelector\XPath\Extension\HtmlExtension;
use OtomaticAi\Vendors\Symfony\Component\CssSelector\XPath\Translator;
/**
 * CssSelectorConverter is the main entry point of the component and can convert CSS
 * selectors to XPath expressions.
 *
 * @author Christophe Coevoet <stof@notk.org>
 */
class CssSelectorConverter
{
    private $translator;
    private $cache;
    private static $xmlCache = [];
    private static $htmlCache = [];
    /**
     * @param bool $html Whether HTML support should be enabled. Disable it for XML documents
     */
    public function __construct(bool $html = \true)
    {
        $this->translator = new Translator();
        if ($html) {
            $this->translator->registerExtension(new HtmlExtension($this->translator));
            $this->cache =& self::$htmlCache;
        } else {
            $this->cache =& self::$xmlCache;
        }
        $this->translator->registerParserShortcut(new EmptyStringParser())->registerParserShortcut(new ElementParser())->registerParserShortcut(new ClassParser())->registerParserShortcut(new HashParser());
    }
    /**
     * Translates a CSS expression to its XPath equivalent.
     *
     * Optionally, a prefix can be added to the resulting XPath
     * expression with the $prefix parameter.
     *
     * @return string
     */
    public function toXPath(string $cssExpr, string $prefix = 'descendant-or-self::')
    {
        return $this->cache[$prefix][$cssExpr] ?? ($this->cache[$prefix][$cssExpr] = $this->translator->cssToXPath($cssExpr, $prefix));
    }
}
