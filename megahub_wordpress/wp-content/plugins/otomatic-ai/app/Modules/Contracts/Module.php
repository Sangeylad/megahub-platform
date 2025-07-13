<?php

namespace OtomaticAi\Modules\Contracts;

use OtomaticAi\Models\Publication;

interface Module
{
    /**
     * Indicate if the module is runnable
     *
     * @param Publication $publication
     * @return boolean
     */
    static public function isRunnable(Publication $publication): bool;

    /**
     * Indicate if the module is enabled
     *
     * @param Publication $publication
     * @return boolean
     */
    static public function isEnabled(Publication $publication): bool;
}
