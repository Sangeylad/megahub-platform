<?php

/*
 * This file is part of the Symfony package.
 *
 * (c) Fabien Potencier <fabien@symfony.com>
 *
 * For the full copyright and license information, please view the LICENSE
 * file that was distributed with this source code.
 */
namespace OtomaticAi\Vendors\Symfony\Component\Translation\Provider;

use OtomaticAi\Vendors\Symfony\Component\Translation\Exception\InvalidArgumentException;
use OtomaticAi\Vendors\Symfony\Component\Translation\Exception\MissingRequiredOptionException;
/**
 * @author Fabien Potencier <fabien@symfony.com>
 * @author Oskar Stark <oskarstark@googlemail.com>
 */
final class Dsn
{
    private $scheme;
    private $host;
    private $user;
    private $password;
    private $port;
    private $path;
    private $options;
    private $originalDsn;
    public function __construct(string $dsn)
    {
        $this->originalDsn = $dsn;
        if (\false === ($params = \parse_url($dsn))) {
            throw new InvalidArgumentException('The translation provider DSN is invalid.');
        }
        if (!isset($params['scheme'])) {
            throw new InvalidArgumentException('The translation provider DSN must contain a scheme.');
        }
        $this->scheme = $params['scheme'];
        if (!isset($params['host'])) {
            throw new InvalidArgumentException('The translation provider DSN must contain a host (use "default" by default).');
        }
        $this->host = $params['host'];
        $this->user = '' !== ($params['user'] ?? '') ? \rawurldecode($params['user']) : null;
        $this->password = '' !== ($params['pass'] ?? '') ? \rawurldecode($params['pass']) : null;
        $this->port = $params['port'] ?? null;
        $this->path = $params['path'] ?? null;
        \parse_str($params['query'] ?? '', $this->options);
    }
    public function getScheme() : string
    {
        return $this->scheme;
    }
    public function getHost() : string
    {
        return $this->host;
    }
    public function getUser() : ?string
    {
        return $this->user;
    }
    public function getPassword() : ?string
    {
        return $this->password;
    }
    public function getPort(?int $default = null) : ?int
    {
        return $this->port ?? $default;
    }
    public function getOption(string $key, $default = null)
    {
        return $this->options[$key] ?? $default;
    }
    public function getRequiredOption(string $key)
    {
        if (!\array_key_exists($key, $this->options) || '' === \trim($this->options[$key])) {
            throw new MissingRequiredOptionException($key);
        }
        return $this->options[$key];
    }
    public function getOptions() : array
    {
        return $this->options;
    }
    public function getPath() : ?string
    {
        return $this->path;
    }
    public function getOriginalDsn() : string
    {
        return $this->originalDsn;
    }
}
