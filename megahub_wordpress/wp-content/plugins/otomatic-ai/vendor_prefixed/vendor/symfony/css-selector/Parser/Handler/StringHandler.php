<?php

/*
 * This file is part of the Symfony package.
 *
 * (c) Fabien Potencier <fabien@symfony.com>
 *
 * For the full copyright and license information, please view the LICENSE
 * file that was distributed with this source code.
 */
namespace OtomaticAi\Vendors\Symfony\Component\CssSelector\Parser\Handler;

use OtomaticAi\Vendors\Symfony\Component\CssSelector\Exception\InternalErrorException;
use OtomaticAi\Vendors\Symfony\Component\CssSelector\Exception\SyntaxErrorException;
use OtomaticAi\Vendors\Symfony\Component\CssSelector\Parser\Reader;
use OtomaticAi\Vendors\Symfony\Component\CssSelector\Parser\Token;
use OtomaticAi\Vendors\Symfony\Component\CssSelector\Parser\Tokenizer\TokenizerEscaping;
use OtomaticAi\Vendors\Symfony\Component\CssSelector\Parser\Tokenizer\TokenizerPatterns;
use OtomaticAi\Vendors\Symfony\Component\CssSelector\Parser\TokenStream;
/**
 * CSS selector comment handler.
 *
 * This component is a port of the Python cssselect library,
 * which is copyright Ian Bicking, @see https://github.com/SimonSapin/cssselect.
 *
 * @author Jean-François Simon <jeanfrancois.simon@sensiolabs.com>
 *
 * @internal
 */
class StringHandler implements HandlerInterface
{
    private $patterns;
    private $escaping;
    public function __construct(TokenizerPatterns $patterns, TokenizerEscaping $escaping)
    {
        $this->patterns = $patterns;
        $this->escaping = $escaping;
    }
    /**
     * {@inheritdoc}
     */
    public function handle(Reader $reader, TokenStream $stream) : bool
    {
        $quote = $reader->getSubstring(1);
        if (!\in_array($quote, ["'", '"'])) {
            return \false;
        }
        $reader->moveForward(1);
        $match = $reader->findPattern($this->patterns->getQuotedStringPattern($quote));
        if (!$match) {
            throw new InternalErrorException(\sprintf('Should have found at least an empty match at %d.', $reader->getPosition()));
        }
        // check unclosed strings
        if (\strlen($match[0]) === $reader->getRemainingLength()) {
            throw SyntaxErrorException::unclosedString($reader->getPosition() - 1);
        }
        // check quotes pairs validity
        if ($quote !== $reader->getSubstring(1, \strlen($match[0]))) {
            throw SyntaxErrorException::unclosedString($reader->getPosition() - 1);
        }
        $string = $this->escaping->escapeUnicodeAndNewLine($match[0]);
        $stream->push(new Token(Token::TYPE_STRING, $string, $reader->getPosition()));
        $reader->moveForward(\strlen($match[0]) + 1);
        return \true;
    }
}
