<?php

namespace OtomaticAi\Content\Contracts;

interface ShouldDisplay
{
    public function display();

    public function toArray();

    public function toText();

    static public function fromArray($array);
}
