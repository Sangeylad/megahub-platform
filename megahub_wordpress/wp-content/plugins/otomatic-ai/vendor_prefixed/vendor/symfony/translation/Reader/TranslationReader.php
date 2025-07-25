<?php

/*
 * This file is part of the Symfony package.
 *
 * (c) Fabien Potencier <fabien@symfony.com>
 *
 * For the full copyright and license information, please view the LICENSE
 * file that was distributed with this source code.
 */
namespace OtomaticAi\Vendors\Symfony\Component\Translation\Reader;

use OtomaticAi\Vendors\Symfony\Component\Finder\Finder;
use OtomaticAi\Vendors\Symfony\Component\Translation\Loader\LoaderInterface;
use OtomaticAi\Vendors\Symfony\Component\Translation\MessageCatalogue;
/**
 * TranslationReader reads translation messages from translation files.
 *
 * @author Michel Salib <michelsalib@hotmail.com>
 */
class TranslationReader implements TranslationReaderInterface
{
    /**
     * Loaders used for import.
     *
     * @var array<string, LoaderInterface>
     */
    private $loaders = [];
    /**
     * Adds a loader to the translation extractor.
     *
     * @param string $format The format of the loader
     */
    public function addLoader(string $format, LoaderInterface $loader)
    {
        $this->loaders[$format] = $loader;
    }
    /**
     * {@inheritdoc}
     */
    public function read(string $directory, MessageCatalogue $catalogue)
    {
        if (!\is_dir($directory)) {
            return;
        }
        foreach ($this->loaders as $format => $loader) {
            // load any existing translation files
            $finder = new Finder();
            $extension = $catalogue->getLocale() . '.' . $format;
            $files = $finder->files()->name('*.' . $extension)->in($directory);
            foreach ($files as $file) {
                $domain = \substr($file->getFilename(), 0, -1 * \strlen($extension) - 1);
                $catalogue->addCatalogue($loader->load($file->getPathname(), $catalogue->getLocale(), $domain));
            }
        }
    }
}
