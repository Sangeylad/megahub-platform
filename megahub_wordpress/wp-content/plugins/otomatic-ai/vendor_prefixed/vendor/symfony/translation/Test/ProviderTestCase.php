<?php

/*
 * This file is part of the Symfony package.
 *
 * (c) Fabien Potencier <fabien@symfony.com>
 *
 * For the full copyright and license information, please view the LICENSE
 * file that was distributed with this source code.
 */
namespace OtomaticAi\Vendors\Symfony\Component\Translation\Test;

use OtomaticAi\Vendors\PHPUnit\Framework\TestCase;
use OtomaticAi\Vendors\Psr\Log\LoggerInterface;
use OtomaticAi\Vendors\Symfony\Component\HttpClient\MockHttpClient;
use OtomaticAi\Vendors\Symfony\Component\Translation\Dumper\XliffFileDumper;
use OtomaticAi\Vendors\Symfony\Component\Translation\Loader\LoaderInterface;
use OtomaticAi\Vendors\Symfony\Component\Translation\Provider\ProviderInterface;
use OtomaticAi\Vendors\Symfony\Contracts\HttpClient\HttpClientInterface;
/**
 * A test case to ease testing a translation provider.
 *
 * @author Mathieu Santostefano <msantostefano@protonmail.com>
 *
 * @internal
 */
abstract class ProviderTestCase extends TestCase
{
    protected $client;
    protected $logger;
    protected $defaultLocale;
    protected $loader;
    protected $xliffFileDumper;
    public static abstract function createProvider(HttpClientInterface $client, LoaderInterface $loader, LoggerInterface $logger, string $defaultLocale, string $endpoint) : ProviderInterface;
    /**
     * @return iterable<array{0: ProviderInterface, 1: string}>
     */
    public static abstract function toStringProvider() : iterable;
    /**
     * @dataProvider toStringProvider
     */
    public function testToString(ProviderInterface $provider, string $expected)
    {
        $this->assertSame($expected, (string) $provider);
    }
    protected function getClient() : MockHttpClient
    {
        return $this->client ?? ($this->client = new MockHttpClient());
    }
    protected function getLoader() : LoaderInterface
    {
        return $this->loader ?? ($this->loader = $this->createMock(LoaderInterface::class));
    }
    protected function getLogger() : LoggerInterface
    {
        return $this->logger ?? ($this->logger = $this->createMock(LoggerInterface::class));
    }
    protected function getDefaultLocale() : string
    {
        return $this->defaultLocale ?? ($this->defaultLocale = 'en');
    }
    protected function getXliffFileDumper() : XliffFileDumper
    {
        return $this->xliffFileDumper ?? ($this->xliffFileDumper = $this->createMock(XliffFileDumper::class));
    }
}
