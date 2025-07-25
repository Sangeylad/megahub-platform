<?php

/*
 * This file is part of the Symfony package.
 *
 * (c) Fabien Potencier <fabien@symfony.com>
 *
 * For the full copyright and license information, please view the LICENSE
 * file that was distributed with this source code.
 */
namespace OtomaticAi\Vendors\Symfony\Component\DomCrawler\Test\Constraint;

use OtomaticAi\Vendors\PHPUnit\Framework\Constraint\Constraint;
use OtomaticAi\Vendors\Symfony\Component\DomCrawler\Crawler;
final class CrawlerSelectorTextContains extends Constraint
{
    private $selector;
    private $expectedText;
    private $hasNode = \false;
    private $nodeText;
    public function __construct(string $selector, string $expectedText)
    {
        $this->selector = $selector;
        $this->expectedText = $expectedText;
    }
    /**
     * {@inheritdoc}
     */
    public function toString() : string
    {
        if ($this->hasNode) {
            return \sprintf('the text "%s" of the node matching selector "%s" contains "%s"', $this->nodeText, $this->selector, $this->expectedText);
        }
        return \sprintf('the Crawler has a node matching selector "%s"', $this->selector);
    }
    /**
     * @param Crawler $crawler
     *
     * {@inheritdoc}
     */
    protected function matches($crawler) : bool
    {
        $crawler = $crawler->filter($this->selector);
        if (!\count($crawler)) {
            $this->hasNode = \false;
            return \false;
        }
        $this->hasNode = \true;
        $this->nodeText = $crawler->text(null, \true);
        return \false !== \mb_strpos($this->nodeText, $this->expectedText);
    }
    /**
     * @param Crawler $crawler
     *
     * {@inheritdoc}
     */
    protected function failureDescription($crawler) : string
    {
        return $this->toString();
    }
}
