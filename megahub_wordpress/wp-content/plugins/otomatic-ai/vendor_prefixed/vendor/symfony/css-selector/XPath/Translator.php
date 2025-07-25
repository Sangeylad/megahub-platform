<?php

/*
 * This file is part of the Symfony package.
 *
 * (c) Fabien Potencier <fabien@symfony.com>
 *
 * For the full copyright and license information, please view the LICENSE
 * file that was distributed with this source code.
 */
namespace OtomaticAi\Vendors\Symfony\Component\CssSelector\XPath;

use OtomaticAi\Vendors\Symfony\Component\CssSelector\Exception\ExpressionErrorException;
use OtomaticAi\Vendors\Symfony\Component\CssSelector\Node\FunctionNode;
use OtomaticAi\Vendors\Symfony\Component\CssSelector\Node\NodeInterface;
use OtomaticAi\Vendors\Symfony\Component\CssSelector\Node\SelectorNode;
use OtomaticAi\Vendors\Symfony\Component\CssSelector\Parser\Parser;
use OtomaticAi\Vendors\Symfony\Component\CssSelector\Parser\ParserInterface;
/**
 * XPath expression translator interface.
 *
 * This component is a port of the Python cssselect library,
 * which is copyright Ian Bicking, @see https://github.com/SimonSapin/cssselect.
 *
 * @author Jean-François Simon <jeanfrancois.simon@sensiolabs.com>
 *
 * @internal
 */
class Translator implements TranslatorInterface
{
    private $mainParser;
    /**
     * @var ParserInterface[]
     */
    private $shortcutParsers = [];
    /**
     * @var Extension\ExtensionInterface[]
     */
    private $extensions = [];
    private $nodeTranslators = [];
    private $combinationTranslators = [];
    private $functionTranslators = [];
    private $pseudoClassTranslators = [];
    private $attributeMatchingTranslators = [];
    public function __construct(?ParserInterface $parser = null)
    {
        $this->mainParser = $parser ?? new Parser();
        $this->registerExtension(new Extension\NodeExtension())->registerExtension(new Extension\CombinationExtension())->registerExtension(new Extension\FunctionExtension())->registerExtension(new Extension\PseudoClassExtension())->registerExtension(new Extension\AttributeMatchingExtension());
    }
    public static function getXpathLiteral(string $element) : string
    {
        if (!\str_contains($element, "'")) {
            return "'" . $element . "'";
        }
        if (!\str_contains($element, '"')) {
            return '"' . $element . '"';
        }
        $string = $element;
        $parts = [];
        while (\true) {
            if (\false !== ($pos = \strpos($string, "'"))) {
                $parts[] = \sprintf("'%s'", \substr($string, 0, $pos));
                $parts[] = "\"'\"";
                $string = \substr($string, $pos + 1);
            } else {
                $parts[] = "'{$string}'";
                break;
            }
        }
        return \sprintf('concat(%s)', \implode(', ', $parts));
    }
    /**
     * {@inheritdoc}
     */
    public function cssToXPath(string $cssExpr, string $prefix = 'descendant-or-self::') : string
    {
        $selectors = $this->parseSelectors($cssExpr);
        /** @var SelectorNode $selector */
        foreach ($selectors as $index => $selector) {
            if (null !== $selector->getPseudoElement()) {
                throw new ExpressionErrorException('Pseudo-elements are not supported.');
            }
            $selectors[$index] = $this->selectorToXPath($selector, $prefix);
        }
        return \implode(' | ', $selectors);
    }
    /**
     * {@inheritdoc}
     */
    public function selectorToXPath(SelectorNode $selector, string $prefix = 'descendant-or-self::') : string
    {
        return ($prefix ?: '') . $this->nodeToXPath($selector);
    }
    /**
     * @return $this
     */
    public function registerExtension(Extension\ExtensionInterface $extension) : self
    {
        $this->extensions[$extension->getName()] = $extension;
        $this->nodeTranslators = \array_merge($this->nodeTranslators, $extension->getNodeTranslators());
        $this->combinationTranslators = \array_merge($this->combinationTranslators, $extension->getCombinationTranslators());
        $this->functionTranslators = \array_merge($this->functionTranslators, $extension->getFunctionTranslators());
        $this->pseudoClassTranslators = \array_merge($this->pseudoClassTranslators, $extension->getPseudoClassTranslators());
        $this->attributeMatchingTranslators = \array_merge($this->attributeMatchingTranslators, $extension->getAttributeMatchingTranslators());
        return $this;
    }
    /**
     * @throws ExpressionErrorException
     */
    public function getExtension(string $name) : Extension\ExtensionInterface
    {
        if (!isset($this->extensions[$name])) {
            throw new ExpressionErrorException(\sprintf('Extension "%s" not registered.', $name));
        }
        return $this->extensions[$name];
    }
    /**
     * @return $this
     */
    public function registerParserShortcut(ParserInterface $shortcut) : self
    {
        $this->shortcutParsers[] = $shortcut;
        return $this;
    }
    /**
     * @throws ExpressionErrorException
     */
    public function nodeToXPath(NodeInterface $node) : XPathExpr
    {
        if (!isset($this->nodeTranslators[$node->getNodeName()])) {
            throw new ExpressionErrorException(\sprintf('Node "%s" not supported.', $node->getNodeName()));
        }
        return $this->nodeTranslators[$node->getNodeName()]($node, $this);
    }
    /**
     * @throws ExpressionErrorException
     */
    public function addCombination(string $combiner, NodeInterface $xpath, NodeInterface $combinedXpath) : XPathExpr
    {
        if (!isset($this->combinationTranslators[$combiner])) {
            throw new ExpressionErrorException(\sprintf('Combiner "%s" not supported.', $combiner));
        }
        return $this->combinationTranslators[$combiner]($this->nodeToXPath($xpath), $this->nodeToXPath($combinedXpath));
    }
    /**
     * @throws ExpressionErrorException
     */
    public function addFunction(XPathExpr $xpath, FunctionNode $function) : XPathExpr
    {
        if (!isset($this->functionTranslators[$function->getName()])) {
            throw new ExpressionErrorException(\sprintf('Function "%s" not supported.', $function->getName()));
        }
        return $this->functionTranslators[$function->getName()]($xpath, $function);
    }
    /**
     * @throws ExpressionErrorException
     */
    public function addPseudoClass(XPathExpr $xpath, string $pseudoClass) : XPathExpr
    {
        if (!isset($this->pseudoClassTranslators[$pseudoClass])) {
            throw new ExpressionErrorException(\sprintf('Pseudo-class "%s" not supported.', $pseudoClass));
        }
        return $this->pseudoClassTranslators[$pseudoClass]($xpath);
    }
    /**
     * @throws ExpressionErrorException
     */
    public function addAttributeMatching(XPathExpr $xpath, string $operator, string $attribute, ?string $value) : XPathExpr
    {
        if (!isset($this->attributeMatchingTranslators[$operator])) {
            throw new ExpressionErrorException(\sprintf('Attribute matcher operator "%s" not supported.', $operator));
        }
        return $this->attributeMatchingTranslators[$operator]($xpath, $attribute, $value);
    }
    /**
     * @return SelectorNode[]
     */
    private function parseSelectors(string $css) : array
    {
        foreach ($this->shortcutParsers as $shortcut) {
            $tokens = $shortcut->parse($css);
            if (!empty($tokens)) {
                return $tokens;
            }
        }
        return $this->mainParser->parse($css);
    }
}
