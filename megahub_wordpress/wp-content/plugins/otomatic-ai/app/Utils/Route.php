<?php

namespace OtomaticAi\Utils;

abstract class Route
{
    static public function ajax($key, $class, $func = "__invoke")
    {
        add_action("wp_ajax_otomatic_ai_" . $key, function () use ($class, $func) {
            call_user_func([new $class, $func]);
        });
    }
}
