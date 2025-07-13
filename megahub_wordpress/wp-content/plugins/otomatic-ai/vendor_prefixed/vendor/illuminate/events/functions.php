<?php

namespace OtomaticAi\Vendors\Illuminate\Events;

use Closure;
if (!\function_exists('OtomaticAi\\Vendors\\Illuminate\\Events\\queueable')) {
    /**
     * Create a new queued Closure event listener.
     *
     * @param  \Closure  $closure
     * @return \Illuminate\Events\QueuedClosure
     */
    function queueable(Closure $closure)
    {
        return new QueuedClosure($closure);
    }
}
