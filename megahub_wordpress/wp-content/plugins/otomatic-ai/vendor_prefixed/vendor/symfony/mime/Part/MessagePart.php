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

use OtomaticAi\Vendors\Symfony\Component\Mime\Message;
use OtomaticAi\Vendors\Symfony\Component\Mime\RawMessage;
/**
 * @final
 *
 * @author Fabien Potencier <fabien@symfony.com>
 */
class MessagePart extends DataPart
{
    private $message;
    public function __construct(RawMessage $message)
    {
        if ($message instanceof Message) {
            $name = $message->getHeaders()->getHeaderBody('Subject') . '.eml';
        } else {
            $name = 'email.eml';
        }
        parent::__construct('', $name);
        $this->message = $message;
    }
    public function getMediaType() : string
    {
        return 'message';
    }
    public function getMediaSubtype() : string
    {
        return 'rfc822';
    }
    public function getBody() : string
    {
        return $this->message->toString();
    }
    public function bodyToString() : string
    {
        return $this->getBody();
    }
    public function bodyToIterable() : iterable
    {
        return $this->message->toIterable();
    }
    /**
     * @return array
     */
    public function __sleep()
    {
        return ['message'];
    }
    public function __wakeup()
    {
        $this->__construct($this->message);
    }
}
