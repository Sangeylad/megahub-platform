<?php

/*
 * This file is part of the Symfony package.
 *
 * (c) Fabien Potencier <fabien@symfony.com>
 *
 * For the full copyright and license information, please view the LICENSE
 * file that was distributed with this source code.
 */
namespace OtomaticAi\Vendors\Symfony\Component\Mime\Part;

use OtomaticAi\Vendors\Symfony\Component\Mime\Header\Headers;
/**
 * @author Fabien Potencier <fabien@symfony.com>
 */
abstract class AbstractPart
{
    private $headers;
    public function __construct()
    {
        $this->headers = new Headers();
    }
    public function getHeaders() : Headers
    {
        return $this->headers;
    }
    public function getPreparedHeaders() : Headers
    {
        $headers = clone $this->headers;
        $headers->setHeaderBody('Parameterized', 'Content-Type', $this->getMediaType() . '/' . $this->getMediaSubtype());
        return $headers;
    }
    public function toString() : string
    {
        return $this->getPreparedHeaders()->toString() . "\r\n" . $this->bodyToString();
    }
    public function toIterable() : iterable
    {
        (yield $this->getPreparedHeaders()->toString());
        (yield "\r\n");
        yield from $this->bodyToIterable();
    }
    public function asDebugString() : string
    {
        return $this->getMediaType() . '/' . $this->getMediaSubtype();
    }
    public abstract function bodyToString() : string;
    public abstract function bodyToIterable() : iterable;
    public abstract function getMediaType() : string;
    public abstract function getMediaSubtype() : string;
}
