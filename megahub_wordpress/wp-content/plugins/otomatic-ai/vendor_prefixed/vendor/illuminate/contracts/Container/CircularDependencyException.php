<?php

namespace OtomaticAi\Vendors\Illuminate\Contracts\Container;

use Exception;
use OtomaticAi\Vendors\Psr\Container\ContainerExceptionInterface;
class CircularDependencyException extends Exception implements ContainerExceptionInterface
{
    //
}
