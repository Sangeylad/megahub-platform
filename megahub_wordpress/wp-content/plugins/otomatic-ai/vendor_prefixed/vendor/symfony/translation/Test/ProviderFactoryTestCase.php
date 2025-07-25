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
use OtomaticAi\Vendors\Symfony\Component\Translation\Exception\IncompleteDsnException;
use OtomaticAi\Vendors\Symfony\Component\Translation\Exception\UnsupportedSchemeException;
use OtomaticAi\Vendors\Symfony\Component\Translation\Loader\LoaderInterface;
use OtomaticAi\Vendors\Symfony\Component\Translation\Provider\Dsn;
use OtomaticAi\Vendors\Symfony\Component\Translation\Provider\ProviderFactoryInterface;
use OtomaticAi\Vendors\Symfony\Contracts\HttpClient\HttpClientInterface;
/**
 * A test case to ease testing a translation provider factory.
 *
 * @author Mathieu Santostefano <msantostefano@protonmail.com>
 *
 * @internal
 */
abstract class ProviderFactoryTestCase extends TestCase
{
    protected $client;
    protected $logger;
    protected $defaultLocale;
    protected $loader;
    protected $xliffFileDumper;
    public abstract function createFactory() : ProviderFactoryInterface;
    /**
     * @return iterable<array{0: bool, 1: string}>
     */
    public static abstract function supportsProvider() : iterable;
    /**
     * @return iterable<array{0: string, 1: string}>
     */
    public static abstract function createProvider() : iterable;
    /**
     * @return iterable<array{0: string, 1: string|null}>
     */
    public static function unsupportedSchemeProvider() : iterable
    {
        return [];
    }
    /**
     * @return iterable<array{0: string, 1: string|null}>
     */
    public static function incompleteDsnProvider() : iterable
    {
        return [];
    }
    /**
     * @dataProvider supportsProvider
     */
    public function testSupports(bool $expected, string $dsn)
    {
        $factory = $this->createFactory();
        $this->assertSame($expected, $factory->supports(new Dsn($dsn)));
    }
    /**
     * @dataProvider createProvider
     */
    public function testCreate(string $expected, string $dsn)
    {
        $factory = $this->createFactory();
        $provider = $factory->create(new Dsn($dsn));
        $this->assertSame($expected, (string) $provider);
    }
    /**
     * @dataProvider unsupportedSchemeProvider
     */
    public function testUnsupportedSchemeException(string $dsn, ?string $message = null)
    {
        $factory = $this->createFactory();
        $dsn = new Dsn($dsn);
        $this->expectException(UnsupportedSchemeException::class);
        if (null !== $message) {
            $this->expectExceptionMessage($message);
        }
        $factory->create($dsn);
    }
    /**
     * @dataProvider incompleteDsnProvider
     */
    public function testIncompleteDsnException(string $dsn, ?string $message = null)
    {
        $factory = $this->createFactory();
        $dsn = new Dsn($dsn);
        $this->expectException(IncompleteDsnException::class);
        if (null !== $message) {
            $this->expectExceptionMessage($message);
        }
        $factory->create($dsn);
    }
    protected function getClient() : HttpClientInterface
    {
        return $this->client ?? ($this->client = new MockHttpClient());
    }
    protected function getLogger() : LoggerInterface
    {
        return $this->logger ?? ($this->logger = $this->createMock(LoggerInterface::class));
    }
    protected function getDefaultLocale() : string
    {
        return $this->defaultLocale ?? ($this->defaultLocale = 'en');
    }
    protected function getLoader() : LoaderInterface
    {
        return $this->loader ?? ($this->loader = $this->createMock(LoaderInterface::class));
    }
    protected function getXliffFileDumper() : XliffFileDumper
    {
        return $this->xliffFileDumper ?? ($this->xliffFileDumper = $this->createMock(XliffFileDumper::class));
    }
}
