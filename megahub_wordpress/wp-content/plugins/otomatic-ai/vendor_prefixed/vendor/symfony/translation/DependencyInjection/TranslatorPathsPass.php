<?php

/*
 * This file is part of the Symfony package.
 *
 * (c) Fabien Potencier <fabien@symfony.com>
 *
 * For the full copyright and license information, please view the LICENSE
 * file that was distributed with this source code.
 */
namespace OtomaticAi\Vendors\Symfony\Component\Translation\DependencyInjection;

use OtomaticAi\Vendors\Symfony\Component\DependencyInjection\Compiler\AbstractRecursivePass;
use OtomaticAi\Vendors\Symfony\Component\DependencyInjection\ContainerBuilder;
use OtomaticAi\Vendors\Symfony\Component\DependencyInjection\Definition;
use OtomaticAi\Vendors\Symfony\Component\DependencyInjection\Reference;
use OtomaticAi\Vendors\Symfony\Component\DependencyInjection\ServiceLocator;
use OtomaticAi\Vendors\Symfony\Component\HttpKernel\Controller\ArgumentResolver\TraceableValueResolver;
/**
 * @author Yonel Ceruto <yonelceruto@gmail.com>
 */
class TranslatorPathsPass extends AbstractRecursivePass
{
    private $translatorServiceId;
    private $debugCommandServiceId;
    private $updateCommandServiceId;
    private $resolverServiceId;
    private $level = 0;
    /**
     * @var array<string, bool>
     */
    private $paths = [];
    /**
     * @var array<int, Definition>
     */
    private $definitions = [];
    /**
     * @var array<string, array<string, bool>>
     */
    private $controllers = [];
    public function __construct(string $translatorServiceId = 'translator', string $debugCommandServiceId = 'console.command.translation_debug', string $updateCommandServiceId = 'console.command.translation_extract', string $resolverServiceId = 'argument_resolver.service')
    {
        if (0 < \func_num_args()) {
            \OtomaticAi\Vendors\trigger_deprecation('symfony/translation', '5.3', 'Configuring "%s" is deprecated.', __CLASS__);
        }
        $this->translatorServiceId = $translatorServiceId;
        $this->debugCommandServiceId = $debugCommandServiceId;
        $this->updateCommandServiceId = $updateCommandServiceId;
        $this->resolverServiceId = $resolverServiceId;
    }
    public function process(ContainerBuilder $container)
    {
        if (!$container->hasDefinition($this->translatorServiceId)) {
            return;
        }
        foreach ($this->findControllerArguments($container) as $controller => $argument) {
            $id = \substr($controller, 0, \strpos($controller, ':') ?: \strlen($controller));
            if ($container->hasDefinition($id)) {
                [$locatorRef] = $argument->getValues();
                $this->controllers[(string) $locatorRef][$container->getDefinition($id)->getClass()] = \true;
            }
        }
        try {
            parent::process($container);
            $paths = [];
            foreach ($this->paths as $class => $_) {
                if (($r = $container->getReflectionClass($class)) && !$r->isInterface()) {
                    $paths[] = $r->getFileName();
                    foreach ($r->getTraits() as $trait) {
                        $paths[] = $trait->getFileName();
                    }
                }
            }
            if ($paths) {
                if ($container->hasDefinition($this->debugCommandServiceId)) {
                    $definition = $container->getDefinition($this->debugCommandServiceId);
                    $definition->replaceArgument(6, \array_merge($definition->getArgument(6), $paths));
                }
                if ($container->hasDefinition($this->updateCommandServiceId)) {
                    $definition = $container->getDefinition($this->updateCommandServiceId);
                    $definition->replaceArgument(7, \array_merge($definition->getArgument(7), $paths));
                }
            }
        } finally {
            $this->level = 0;
            $this->paths = [];
            $this->definitions = [];
        }
    }
    protected function processValue($value, bool $isRoot = \false)
    {
        if ($value instanceof Reference) {
            if ((string) $value === $this->translatorServiceId) {
                for ($i = $this->level - 1; $i >= 0; --$i) {
                    $class = $this->definitions[$i]->getClass();
                    if (ServiceLocator::class === $class) {
                        if (!isset($this->controllers[$this->currentId])) {
                            continue;
                        }
                        foreach ($this->controllers[$this->currentId] as $class => $_) {
                            $this->paths[$class] = \true;
                        }
                    } else {
                        $this->paths[$class] = \true;
                    }
                    break;
                }
            }
            return $value;
        }
        if ($value instanceof Definition) {
            $this->definitions[$this->level++] = $value;
            $value = parent::processValue($value, $isRoot);
            unset($this->definitions[--$this->level]);
            return $value;
        }
        return parent::processValue($value, $isRoot);
    }
    private function findControllerArguments(ContainerBuilder $container) : array
    {
        if (!$container->has($this->resolverServiceId)) {
            return [];
        }
        $resolverDef = $container->findDefinition($this->resolverServiceId);
        if (TraceableValueResolver::class === $resolverDef->getClass()) {
            $resolverDef = $container->getDefinition($resolverDef->getArgument(0));
        }
        $argument = $resolverDef->getArgument(0);
        if ($argument instanceof Reference) {
            $argument = $container->getDefinition($argument);
        }
        return $argument->getArgument(0);
    }
}
