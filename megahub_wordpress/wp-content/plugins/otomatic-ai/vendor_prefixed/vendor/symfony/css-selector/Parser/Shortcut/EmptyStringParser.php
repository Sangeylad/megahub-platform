<?php

/*
 * This file is part of the Symfony package.
 *
 * (c) Fabien Potencier <fabien@symfony.com>
 *
 * For the full copyright and license information, please view the LICENSE
 * file that was distributed with this source code.
 */
namespace OtomaticAi\Vendors\Symfony\Component\CssSelector\Parser\Shortcut;

use OtomaticAi\Vendors\Symfony\Component\CssSelector\Node\ElementNode;
use OtomaticAi\Vendors\Symfony\Component\CssSelector\Node\SelectorNode;
use OtomaticAi\Vendors\Symfony\Component\CssSelector\Parser\ParserInterface;
/**
 * CSS selector class parser shortcut.
 *
 * This shortcut ensure compatibility with previous version.
 * - The parser fails to parse an empty string.
 * - In the previous version, an empty string matches each tags.
 *
 * This component is a port of the Python cssselect library,
 * which is copyright Ian Bicking, @see https://github.com/SimonSapin/cssselect.
 *
 * @author Jean-François Simon <jeanfrancois.simon@sensiolabs.com>
 *
 * @internal
 */
class EmptyStringParser implements ParserInterface
{
    /**
     * {@inheritdoc}
     */
    public function parse(string $source) : array
    {
        // Matches an empty string
        if ('' == $source) {
            return [new SelectorNode(new ElementNode(null, '*'))];
        }
        return [];
    }
}
