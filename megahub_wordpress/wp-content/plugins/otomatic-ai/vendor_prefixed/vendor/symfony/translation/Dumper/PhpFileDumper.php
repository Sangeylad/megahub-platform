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
 * PhpFileDumper generates PHP files from a message catalogue.
 *
 * @author Michel Salib <michelsalib@hotmail.com>
 */
class PhpFileDumper extends FileDumper
{
    /**
     * {@inheritdoc}
     */
    public function formatCatalogue(MessageCatalogue $messages, string $domain, array $options = [])
    {
        return "<?php\n\nreturn " . \var_export($messages->all($domain), \true) . ";\n";
    }
    /**
     * {@inheritdoc}
     */
    protected function getExtension()
    {
        return 'php';
    }
}
