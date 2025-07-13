<?php

namespace OtomaticAi\Utils;

class Footprint
{
    static function clear($string)
    {
        $string = preg_replace(
            [
                '/^introduction\s*:?$/i',
                '/^conclusion\s*:?$/i'
            ],
            "",
            $string
        );
        return trim($string);
    }
}
