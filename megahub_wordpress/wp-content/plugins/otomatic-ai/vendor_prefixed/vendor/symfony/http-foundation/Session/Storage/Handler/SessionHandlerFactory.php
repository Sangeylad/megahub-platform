<?php

/*
 * This file is part of the Symfony package.
 *
 * (c) Fabien Potencier <fabien@symfony.com>
 *
 * For the full copyright and license information, please view the LICENSE
 * file that was distributed with this source code.
 */
namespace OtomaticAi\Vendors\Symfony\Component\HttpFoundation\Session\Storage\Handler;

use OtomaticAi\Vendors\Doctrine\DBAL\Configuration;
use OtomaticAi\Vendors\Doctrine\DBAL\DriverManager;
use OtomaticAi\Vendors\Doctrine\DBAL\Schema\DefaultSchemaManagerFactory;
use OtomaticAi\Vendors\Doctrine\DBAL\Tools\DsnParser;
use OtomaticAi\Vendors\Symfony\Component\Cache\Adapter\AbstractAdapter;
use OtomaticAi\Vendors\Symfony\Component\Cache\Traits\RedisClusterProxy;
use OtomaticAi\Vendors\Symfony\Component\Cache\Traits\RedisProxy;
/**
 * @author Nicolas Grekas <p@tchwork.com>
 */
class SessionHandlerFactory
{
    /**
     * @param \Redis|\RedisArray|\RedisCluster|\Predis\ClientInterface|RedisProxy|RedisClusterProxy|\Memcached|\PDO|string $connection Connection or DSN
     */
    public static function createHandler($connection) : AbstractSessionHandler
    {
        if (!\is_string($connection) && !\is_object($connection)) {
            throw new \TypeError(\sprintf('Argument 1 passed to "%s()" must be a string or a connection object, "%s" given.', __METHOD__, \get_debug_type($connection)));
        }
        if ($options = \is_string($connection) ? \parse_url($connection) : \false) {
            \parse_str($options['query'] ?? '', $options);
        }
        switch (\true) {
            case $connection instanceof \Redis:
            case $connection instanceof \RedisArray:
            case $connection instanceof \RedisCluster:
            case $connection instanceof \OtomaticAi\Vendors\Predis\ClientInterface:
            case $connection instanceof RedisProxy:
            case $connection instanceof RedisClusterProxy:
                return new RedisSessionHandler($connection);
            case $connection instanceof \Memcached:
                return new MemcachedSessionHandler($connection);
            case $connection instanceof \PDO:
                return new PdoSessionHandler($connection);
            case !\is_string($connection):
                throw new \InvalidArgumentException(\sprintf('Unsupported Connection: "%s".', \get_debug_type($connection)));
            case \str_starts_with($connection, 'file://'):
                $savePath = \substr($connection, 7);
                return new StrictSessionHandler(new NativeFileSessionHandler('' === $savePath ? null : $savePath));
            case \str_starts_with($connection, 'redis:'):
            case \str_starts_with($connection, 'rediss:'):
            case \str_starts_with($connection, 'memcached:'):
                if (!\class_exists(AbstractAdapter::class)) {
                    throw new \InvalidArgumentException('Unsupported Redis or Memcached DSN. Try running "composer require symfony/cache".');
                }
                $handlerClass = \str_starts_with($connection, 'memcached:') ? MemcachedSessionHandler::class : RedisSessionHandler::class;
                $connection = AbstractAdapter::createConnection($connection, ['lazy' => \true]);
                return new $handlerClass($connection, \array_intersect_key($options ?: [], ['prefix' => 1, 'ttl' => 1]));
            case \str_starts_with($connection, 'pdo_oci://'):
                if (!\class_exists(DriverManager::class)) {
                    throw new \InvalidArgumentException('Unsupported PDO OCI DSN. Try running "composer require doctrine/dbal".');
                }
                $connection[3] = '-';
                $params = \class_exists(DsnParser::class) ? (new DsnParser())->parse($connection) : ['url' => $connection];
                $config = new Configuration();
                if (\class_exists(DefaultSchemaManagerFactory::class)) {
                    $config->setSchemaManagerFactory(new DefaultSchemaManagerFactory());
                }
                $connection = DriverManager::getConnection($params, $config);
                // The condition should be removed once support for DBAL <3.3 is dropped
                $connection = \method_exists($connection, 'getNativeConnection') ? $connection->getNativeConnection() : $connection->getWrappedConnection();
            // no break;
            case \str_starts_with($connection, 'mssql://'):
            case \str_starts_with($connection, 'mysql://'):
            case \str_starts_with($connection, 'mysql2://'):
            case \str_starts_with($connection, 'pgsql://'):
            case \str_starts_with($connection, 'postgres://'):
            case \str_starts_with($connection, 'postgresql://'):
            case \str_starts_with($connection, 'sqlsrv://'):
            case \str_starts_with($connection, 'sqlite://'):
            case \str_starts_with($connection, 'sqlite3://'):
                return new PdoSessionHandler($connection, $options ?: []);
        }
        throw new \InvalidArgumentException(\sprintf('Unsupported Connection: "%s".', $connection));
    }
}
