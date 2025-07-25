<?php

namespace OtomaticAi\Vendors\Illuminate\Database\Console\Factories;

use OtomaticAi\Vendors\Illuminate\Console\GeneratorCommand;
use OtomaticAi\Vendors\Illuminate\Support\Str;
use OtomaticAi\Vendors\Symfony\Component\Console\Input\InputOption;
class FactoryMakeCommand extends GeneratorCommand
{
    /**
     * The console command name.
     *
     * @var string
     */
    protected $name = 'make:factory';
    /**
     * The console command description.
     *
     * @var string
     */
    protected $description = 'Create a new model factory';
    /**
     * The type of class being generated.
     *
     * @var string
     */
    protected $type = 'Factory';
    /**
     * Get the stub file for the generator.
     *
     * @return string
     */
    protected function getStub()
    {
        return $this->resolveStubPath('/stubs/factory.stub');
    }
    /**
     * Resolve the fully-qualified path to the stub.
     *
     * @param  string  $stub
     * @return string
     */
    protected function resolveStubPath($stub)
    {
        return \file_exists($customPath = $this->laravel->basePath(\trim($stub, '/'))) ? $customPath : __DIR__ . $stub;
    }
    /**
     * Build the class with the given name.
     *
     * @param  string  $name
     * @return string
     */
    protected function buildClass($name)
    {
        $factory = \OtomaticAi\Vendors\class_basename(Str::ucfirst(\str_replace('Factory', '', $name)));
        $namespaceModel = $this->option('model') ? $this->qualifyModel($this->option('model')) : $this->qualifyModel($this->guessModelName($name));
        $model = \OtomaticAi\Vendors\class_basename($namespaceModel);
        if (Str::startsWith($namespaceModel, $this->rootNamespace() . 'Models')) {
            $namespace = Str::beforeLast('Database\\Factories\\' . Str::after($namespaceModel, $this->rootNamespace() . 'Models\\'), '\\');
        } else {
            $namespace = 'OtomaticAi\\Vendors\\Database\\Factories';
        }
        $replace = ['{{ factoryNamespace }}' => $namespace, 'NamespacedDummyModel' => $namespaceModel, '{{ namespacedModel }}' => $namespaceModel, '{{namespacedModel}}' => $namespaceModel, 'DummyModel' => $model, '{{ model }}' => $model, '{{model}}' => $model, '{{ factory }}' => $factory, '{{factory}}' => $factory];
        return \str_replace(\array_keys($replace), \array_values($replace), parent::buildClass($name));
    }
    /**
     * Get the destination class path.
     *
     * @param  string  $name
     * @return string
     */
    protected function getPath($name)
    {
        $name = (string) Str::of($name)->replaceFirst($this->rootNamespace(), '')->finish('Factory');
        return $this->laravel->databasePath() . '/factories/' . \str_replace('\\', '/', $name) . '.php';
    }
    /**
     * Guess the model name from the Factory name or return a default model name.
     *
     * @param  string  $name
     * @return string
     */
    protected function guessModelName($name)
    {
        if (Str::endsWith($name, 'Factory')) {
            $name = \substr($name, 0, -7);
        }
        $modelName = $this->qualifyModel(Str::after($name, $this->rootNamespace()));
        if (\class_exists($modelName)) {
            return $modelName;
        }
        if (\is_dir(app_path('Models/'))) {
            return $this->rootNamespace() . 'Models\\Model';
        }
        return $this->rootNamespace() . 'Model';
    }
    /**
     * Get the console command options.
     *
     * @return array
     */
    protected function getOptions()
    {
        return [['model', 'm', InputOption::VALUE_OPTIONAL, 'The name of the model']];
    }
}
