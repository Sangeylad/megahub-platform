<?php

namespace OtomaticAi\Casts;

use OtomaticAi\Utils\Language as UtilsLanguage;
use OtomaticAi\Vendors\Illuminate\Contracts\Database\Eloquent\CastsAttributes;

class Language implements CastsAttributes
{
    /**
     * Cast the given value.
     *
     * @param  \Illuminate\Database\Eloquent\Model  $model
     * @param  string  $key
     * @param  mixed  $value
     * @param  array  $attributes
     * @return array
     */
    public function get($model, $key, $value, $attributes)
    {
        return UtilsLanguage::find($value);
    }

    /**
     * Prepare the given value for storage.
     *
     * @param  \Illuminate\Database\Eloquent\Model  $model
     * @param  string  $key
     * @param  array  $value
     * @param  array  $attributes
     * @return string
     */
    public function set($model, $key, $value, $attributes)
    {
        if ($value instanceof UtilsLanguage) {
            return $value->key;
        }

        return $value;
    }
}
