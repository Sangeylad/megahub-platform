<?php

/*
 * This file is part of the Symfony package.
 *
 * (c) Fabien Potencier <fabien@symfony.com>
 *
 * For the full copyright and license information, please view the LICENSE
 * file that was distributed with this source code.
 */
namespace OtomaticAi\Vendors\Symfony\Component\Translation\Writer;

use OtomaticAi\Vendors\Symfony\Component\Translation\Dumper\DumperInterface;
use OtomaticAi\Vendors\Symfony\Component\Translation\Exception\InvalidArgumentException;
use OtomaticAi\Vendors\Symfony\Component\Translation\Exception\RuntimeException;
use OtomaticAi\Vendors\Symfony\Component\Translation\MessageCatalogue;
/**
 * TranslationWriter writes translation messages.
 *
 * @author Michel Salib <michelsalib@hotmail.com>
 */
class TranslationWriter implements TranslationWriterInterface
{
    /**
     * @var array<string, DumperInterface>
     */
    private $dumpers = [];
    /**
     * Adds a dumper to the writer.
     */
    public function addDumper(string $format, DumperInterface $dumper)
    {
        $this->dumpers[$format] = $dumper;
    }
    /**
     * Obtains the list of supported formats.
     *
     * @return array
     */
    public function getFormats()
    {
        return \array_keys($this->dumpers);
    }
    /**
     * Writes translation from the catalogue according to the selected format.
     *
     * @param string $format  The format to use to dump the messages
     * @param array  $options Options that are passed to the dumper
     *
     * @throws InvalidArgumentException
     */
    public function write(MessageCatalogue $catalogue, string $format, array $options = [])
    {
        if (!isset($this->dumpers[$format])) {
            throw new InvalidArgumentException(\sprintf('There is no dumper associated with format "%s".', $format));
        }
        // get the right dumper
        $dumper = $this->dumpers[$format];
        if (isset($options['path']) && !\is_dir($options['path']) && !@\mkdir($options['path'], 0777, \true) && !\is_dir($options['path'])) {
            throw new RuntimeException(\sprintf('Translation Writer was not able to create directory "%s".', $options['path']));
        }
        // save
        $dumper->dump($catalogue, $options);
    }
}
