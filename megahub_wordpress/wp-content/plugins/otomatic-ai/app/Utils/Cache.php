<?php

namespace OtomaticAi\Utils;

use OtomaticAi\Vendors\Illuminate\Support\Collection;

class Cache
{
    public $items;
    static private $instance;

    public function __construct()
    {
        $this->items = new Collection;
    }

    static public function has($key)
    {
        return self::instance()->items->has($key);
    }

    static public function set($key, $value)
    {
        self::instance()->items->put($key, $value);
    }

    static public function get($key, $default = null)
    {
        return self::instance()->items->get($key, $default);
    }

    static public function forget($key)
    {
        self::instance()->items->forget($key);
    }

    static public function instance()
    {
        if (self::$instance === null) {
            self::$instance = new self();
        }

        return self::$instance;
    }
}
