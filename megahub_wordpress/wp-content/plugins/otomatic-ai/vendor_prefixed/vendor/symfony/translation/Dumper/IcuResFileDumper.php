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

use OtomaticAi\Vendors\Symfony\Component\Translation\MessageCatalogue;
/**
 * IcuResDumper generates an ICU ResourceBundle formatted string representation of a message catalogue.
 *
 * @author Stealth35
 */
class IcuResFileDumper extends FileDumper
{
    /**
     * {@inheritdoc}
     */
    protected $relativePathTemplate = '%domain%/%locale%.%extension%';
    /**
     * {@inheritdoc}
     */
    public function formatCatalogue(MessageCatalogue $messages, string $domain, array $options = [])
    {
        $data = $indexes = $resources = '';
        foreach ($messages->all($domain) as $source => $target) {
            $indexes .= \pack('v', \strlen($data) + 28);
            $data .= $source . "\x00";
        }
        $data .= $this->writePadding($data);
        $keyTop = $this->getPosition($data);
        foreach ($messages->all($domain) as $source => $target) {
            $resources .= \pack('V', $this->getPosition($data));
            $data .= \pack('V', \strlen($target)) . \mb_convert_encoding($target . "\x00", 'UTF-16LE', 'UTF-8') . $this->writePadding($data);
        }
        $resOffset = $this->getPosition($data);
        $data .= \pack('v', \count($messages->all($domain))) . $indexes . $this->writePadding($data) . $resources;
        $bundleTop = $this->getPosition($data);
        $root = \pack(
            'V7',
            $resOffset + (2 << 28),
            // Resource Offset + Resource Type
            6,
            // Index length
            $keyTop,
            // Index keys top
            $bundleTop,
            // Index resources top
            $bundleTop,
            // Index bundle top
            \count($messages->all($domain)),
            // Index max table length
            0
        );
        $header = \pack(
            'vC2v4C12@32',
            32,
            // Header size
            0xda,
            0x27,
            // Magic number 1 and 2
            20,
            0,
            0,
            2,
            // Rest of the header, ..., Size of a char
            0x52,
            0x65,
            0x73,
            0x42,
            // Data format identifier
            1,
            2,
            0,
            0,
            // Data version
            1,
            4,
            0,
            0
        );
        return $header . $root . $data;
    }
    private function writePadding(string $data) : ?string
    {
        $padding = \strlen($data) % 4;
        return $padding ? \str_repeat("\xaa", 4 - $padding) : null;
    }
    private function getPosition(string $data)
    {
        return (\strlen($data) + 28) / 4;
    }
    /**
     * {@inheritdoc}
     */
    protected function getExtension()
    {
        return 'res';
    }
}
