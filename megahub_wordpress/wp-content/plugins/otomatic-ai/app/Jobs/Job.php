<?php

namespace OtomaticAi\Jobs;

use OtomaticAi\Jobs\Contracts\ShouldHandle;
use OtomaticAi\Vendors\Illuminate\Support\Arr;

abstract class Job implements ShouldHandle
{
    const HOOK = "otomatic-ai-job";

    static public function dispatch($attrs)
    {
        as_enqueue_async_action(self::HOOK, [["class" => static::class, "attrs" => $attrs]]);
    }

    static public function register()
    {
        add_action(self::HOOK, function ($args) {
            $class = Arr::get($args, "class");
            $attrs = Arr::get($args, "attrs", []);
            if ($class && class_exists($class)) {
                $job = new $class($attrs);
                $job->handle();
            }
        });
    }
}
