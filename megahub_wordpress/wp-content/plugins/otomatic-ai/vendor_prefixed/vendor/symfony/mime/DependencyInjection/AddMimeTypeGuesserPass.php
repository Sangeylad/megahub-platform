<?php

/*
 * This file is part of the Symfony package.
 *
 * (c) Fabien Potencier <fabien@symfony.com>
 *
 * For the full copyright and license information, please view the LICENSE
 * file that was distributed with this source code.
 */
namespace OtomaticAi\Vendors\Symfony\Component\Mime\DependencyInjection;

use OtomaticAi\Vendors\Symfony\Component\DependencyInjection\Compiler\CompilerPassInterface;
use OtomaticAi\Vendors\Symfony\Component\DependencyInjection\ContainerBuilder;
use OtomaticAi\Vendors\Symfony\Component\DependencyInjection\Reference;
/**
 * Registers custom mime types guessers.
 *
 * @author Fabien Potencier <fabien@symfony.com>
 */
class AddMimeTypeGuesserPass implements CompilerPassInterface
{
    private $mimeTypesService;
    private $mimeTypeGuesserTag;
    public function __construct(string $mimeTypesService = 'mime_types', string $mimeTypeGuesserTag = 'mime.mime_type_guesser')
    {
        if (0 < \func_num_args()) {
            \OtomaticAi\Vendors\trigger_deprecation('symfony/mime', '5.3', 'Configuring "%s" is deprecated.', __CLASS__);
        }
        $this->mimeTypesService = $mimeTypesService;
        $this->mimeTypeGuesserTag = $mimeTypeGuesserTag;
    }
    /**
     * {@inheritdoc}
     */
    public function process(ContainerBuilder $container)
    {
        if ($container->has($this->mimeTypesService)) {
            $definition = $container->findDefinition($this->mimeTypesService);
            foreach ($container->findTaggedServiceIds($this->mimeTypeGuesserTag, \true) as $id => $attributes) {
                $definition->addMethodCall('registerGuesser', [new Reference($id)]);
            }
        }
    }
}
