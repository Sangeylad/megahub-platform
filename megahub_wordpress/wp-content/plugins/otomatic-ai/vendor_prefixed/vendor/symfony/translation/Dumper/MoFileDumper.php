<?php

/*
 * This file is part of the Symfony package.
 *
 * (c) Fabien Potencier <fabien@symfony.com>
 *
 * For the full copyright and license information, please view the LICENSE
 * file that was distributed with this source code.
 */
namespace OtomaticAi\Vendors\Symfony\Component\Translation\Dumper;

use OtomaticAi\Vendors\Symfony\Component\Translation\Loader\MoFileLoader;
use OtomaticAi\Vendors\Symfony\Component\Translation\MessageCatalogue;
/**
 * MoFileDumper generates a gettext formatted string representation of a message catalogue.
 *
 * @author Stealth35
 */
class MoFileDumper extends FileDumper
{
    /**
     * {@inheritdoc}
     */
    public function formatCatalogue(MessageCatalogue $messages, string $domain, array $options = [])
    {
        $sources = $targets = $sourceOffsets = $targetOffsets = '';
        $offsets = [];
        $size = 0;
        foreach ($messages->all($domain) as $source => $target) {
            $offsets[] = \array_map('strlen', [$sources, $source, $targets, $target]);
            $sources .= "\x00" . $source;
            $targets .= "\x00" . $target;
            ++$size;
        }
        $header = ['magicNumber' => MoFileLoader::MO_LITTLE_ENDIAN_MAGIC, 'formatRevision' => 0, 'count' => $size, 'offsetId' => MoFileLoader::MO_HEADER_SIZE, 'offsetTranslated' => MoFileLoader::MO_HEADER_SIZE + 8 * $size, 'sizeHashes' => 0, 'offsetHashes' => MoFileLoader::MO_HEADER_SIZE + 16 * $size];
        $sourcesSize = \strlen($sources);
        $sourcesStart = $header['offsetHashes'] + 1;
        foreach ($offsets as $offset) {
            $sourceOffsets .= $this->writeLong($offset[1]) . $this->writeLong($offset[0] + $sourcesStart);
            $targetOffsets .= $this->writeLong($offset[3]) . $this->writeLong($offset[2] + $sourcesStart + $sourcesSize);
        }
        $output = \implode('', \array_map([$this, 'writeLong'], $header)) . $sourceOffsets . $targetOffsets . $sources . $targets;
        return $output;
    }
    /**
     * {@inheritdoc}
     */
    protected function getExtension()
    {
        return 'mo';
    }
    private function writeLong($str) : string
    {
        return \pack('V*', $str);
    }
}
