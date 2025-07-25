<?php

/*
 * This file is part of the Symfony package.
 *
 * (c) Fabien Potencier <fabien@symfony.com>
 *
 * For the full copyright and license information, please view the LICENSE
 * file that was distributed with this source code.
 */
namespace OtomaticAi\Vendors\Symfony\Component\HttpFoundation\Session;

use OtomaticAi\Vendors\Symfony\Component\HttpFoundation\RequestStack;
use OtomaticAi\Vendors\Symfony\Component\HttpFoundation\Session\Storage\SessionStorageFactoryInterface;
// Help opcache.preload discover always-needed symbols
\class_exists(Session::class);
/**
 * @author Jérémy Derussé <jeremy@derusse.com>
 */
class SessionFactory implements SessionFactoryInterface
{
    private $requestStack;
    private $storageFactory;
    private $usageReporter;
    public function __construct(RequestStack $requestStack, SessionStorageFactoryInterface $storageFactory, ?callable $usageReporter = null)
    {
        $this->requestStack = $requestStack;
        $this->storageFactory = $storageFactory;
        $this->usageReporter = $usageReporter;
    }
    public function createSession() : SessionInterface
    {
        return new Session($this->storageFactory->createStorage($this->requestStack->getMainRequest()), null, null, $this->usageReporter);
    }
}
