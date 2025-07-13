<?php

namespace OtomaticAi\Vendors\Illuminate\Support;

use OtomaticAi\Vendors\Carbon\Carbon as BaseCarbon;
use OtomaticAi\Vendors\Carbon\CarbonImmutable as BaseCarbonImmutable;
class Carbon extends BaseCarbon
{
    /**
     * {@inheritdoc}
     */
    public static function setTestNow($testNow = null)
    {
        BaseCarbon::setTestNow($testNow);
        BaseCarbonImmutable::setTestNow($testNow);
    }
}
