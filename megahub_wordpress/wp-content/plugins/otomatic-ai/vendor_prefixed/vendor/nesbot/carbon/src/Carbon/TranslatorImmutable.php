<?php

/**
 * This file is part of the Carbon package.
 *
 * (c) Brian Nesbitt <brian@nesbot.com>
 *
 * For the full copyright and license information, please view the LICENSE
 * file that was distributed with this source code.
 */
namespace OtomaticAi\Vendors\Carbon;

use OtomaticAi\Vendors\Carbon\Exceptions\ImmutableException;
use OtomaticAi\Vendors\Symfony\Component\Config\ConfigCacheFactoryInterface;
use OtomaticAi\Vendors\Symfony\Component\Translation\Formatter\MessageFormatterInterface;
class TranslatorImmutable extends Translator
{
    /** @var bool */
    private $constructed = \false;
    public function __construct($locale, MessageFormatterInterface $formatter = null, $cacheDir = null, $debug = \false)
    {
        parent::__construct($locale, $formatter, $cacheDir, $debug);
        $this->constructed = \true;
    }
    /**
     * @codeCoverageIgnore
     */
    public function setDirectories(array $directories)
    {
        $this->disallowMutation(__METHOD__);
        return parent::setDirectories($directories);
    }
    public function setLocale($locale)
    {
        $this->disallowMutation(__METHOD__);
        return parent::setLocale($locale);
    }
    /**
     * @codeCoverageIgnore
     */
    public function setMessages($locale, $messages)
    {
        $this->disallowMutation(__METHOD__);
        return parent::setMessages($locale, $messages);
    }
    /**
     * @codeCoverageIgnore
     */
    public function setTranslations($messages)
    {
        $this->disallowMutation(__METHOD__);
        return parent::setTranslations($messages);
    }
    /**
     * @codeCoverageIgnore
     */
    public function setConfigCacheFactory(ConfigCacheFactoryInterface $configCacheFactory) : void
    {
        $this->disallowMutation(__METHOD__);
        parent::setConfigCacheFactory($configCacheFactory);
    }
    public function resetMessages($locale = null)
    {
        $this->disallowMutation(__METHOD__);
        return parent::resetMessages($locale);
    }
    /**
     * @codeCoverageIgnore
     */
    public function setFallbackLocales(array $locales)
    {
        $this->disallowMutation(__METHOD__);
        parent::setFallbackLocales($locales);
    }
    private function disallowMutation($method)
    {
        if ($this->constructed) {
            throw new ImmutableException($method . ' not allowed on ' . static::class);
        }
    }
}
