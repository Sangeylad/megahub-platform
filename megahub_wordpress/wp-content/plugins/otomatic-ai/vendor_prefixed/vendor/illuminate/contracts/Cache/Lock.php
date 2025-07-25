<?php

namespace OtomaticAi\Vendors\Illuminate\Contracts\Cache;

interface Lock
{
    /**
     * Attempt to acquire the lock.
     *
     * @param  callable|null  $callback
     * @return mixed
     */
    public function get($callback = null);
    /**
     * Attempt to acquire the lock for the given number of seconds.
     *
     * @param  int  $seconds
     * @param  callable|null  $callback
     * @return mixed
     */
    public function block($seconds, $callback = null);
    /**
     * Release the lock.
     *
     * @return bool
     */
    public function release();
    /**
     * Returns the current owner of the lock.
     *
     * @return string
     */
    public function owner();
    /**
     * Releases this lock in disregard of ownership.
     *
     * @return void
     */
    public function forceRelease();
}
