<?php

namespace OtomaticAi\Vendors\Illuminate\Support\Traits;

trait Tappable
{
    /**
     * Call the given Closure with this instance then return the instance.
     *
     * @param  callable|null  $callback
     * @return $this|\Illuminate\Support\HigherOrderTapProxy
     */
    public function tap($callback = null)
    {
        return \OtomaticAi\Vendors\tap($this, $callback);
    }
}
