<?php

/*
 * This file is part of the Symfony package.
 *
 * (c) Fabien Potencier <fabien@symfony.com>
 *
 * For the full copyright and license information, please view the LICENSE
 * file that was distributed with this source code.
 */
namespace OtomaticAi\Vendors\Symfony\Component\Translation;

use OtomaticAi\Vendors\Symfony\Component\Config\Resource\ResourceInterface;
/**
 * MessageCatalogueInterface.
 *
 * @author Fabien Potencier <fabien@symfony.com>
 */
interface MessageCatalogueInterface
{
    public const INTL_DOMAIN_SUFFIX = '+intl-icu';
    /**
     * Gets the catalogue locale.
     *
     * @return string
     */
    public function getLocale();
    /**
     * Gets the domains.
     *
     * @return array
     */
    public function getDomains();
    /**
     * Gets the messages within a given domain.
     *
     * If $domain is null, it returns all messages.
     *
     * @param string|null $domain The domain name
     *
     * @return array
     */
    public function all(?string $domain = null);
    /**
     * Sets a message translation.
     *
     * @param string $id          The message id
     * @param string $translation The messages translation
     * @param string $domain      The domain name
     */
    public function set(string $id, string $translation, string $domain = 'messages');
    /**
     * Checks if a message has a translation.
     *
     * @param string $id     The message id
     * @param string $domain The domain name
     *
     * @return bool
     */
    public function has(string $id, string $domain = 'messages');
    /**
     * Checks if a message has a translation (it does not take into account the fallback mechanism).
     *
     * @param string $id     The message id
     * @param string $domain The domain name
     *
     * @return bool
     */
    public function defines(string $id, string $domain = 'messages');
    /**
     * Gets a message translation.
     *
     * @param string $id     The message id
     * @param string $domain The domain name
     *
     * @return string
     */
    public function get(string $id, string $domain = 'messages');
    /**
     * Sets translations for a given domain.
     *
     * @param array  $messages An array of translations
     * @param string $domain   The domain name
     */
    public function replace(array $messages, string $domain = 'messages');
    /**
     * Adds translations for a given domain.
     *
     * @param array  $messages An array of translations
     * @param string $domain   The domain name
     */
    public function add(array $messages, string $domain = 'messages');
    /**
     * Merges translations from the given Catalogue into the current one.
     *
     * The two catalogues must have the same locale.
     */
    public function addCatalogue(self $catalogue);
    /**
     * Merges translations from the given Catalogue into the current one
     * only when the translation does not exist.
     *
     * This is used to provide default translations when they do not exist for the current locale.
     */
    public function addFallbackCatalogue(self $catalogue);
    /**
     * Gets the fallback catalogue.
     *
     * @return self|null
     */
    public function getFallbackCatalogue();
    /**
     * Returns an array of resources loaded to build this collection.
     *
     * @return ResourceInterface[]
     */
    public function getResources();
    /**
     * Adds a resource for this collection.
     */
    public function addResource(ResourceInterface $resource);
}
