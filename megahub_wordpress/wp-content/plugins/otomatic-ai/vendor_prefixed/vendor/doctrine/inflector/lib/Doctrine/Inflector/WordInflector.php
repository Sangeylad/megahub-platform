<?php

declare (strict_types=1);
namespace OtomaticAi\Vendors\Doctrine\Inflector;

interface WordInflector
{
    public function inflect(string $word) : string;
}
