<?php

namespace OtomaticAi\Utils\Linking\Templates\Contracts;

interface ShouldDisplay
{
    public function display(bool $echo = false): string;
}
