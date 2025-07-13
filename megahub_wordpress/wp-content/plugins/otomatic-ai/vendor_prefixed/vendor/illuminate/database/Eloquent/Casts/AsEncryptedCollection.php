<?php

namespace OtomaticAi\Vendors\Illuminate\Database\Eloquent\Casts;

use OtomaticAi\Vendors\Illuminate\Contracts\Database\Eloquent\Castable;
use OtomaticAi\Vendors\Illuminate\Contracts\Database\Eloquent\CastsAttributes;
use OtomaticAi\Vendors\Illuminate\Support\Collection;
use OtomaticAi\Vendors\Illuminate\Support\Facades\Crypt;
class AsEncryptedCollection implements Castable
{
    /**
     * Get the caster class to use when casting from / to this cast target.
     *
     * @param  array  $arguments
     * @return object|string
     */
    public static function castUsing(array $arguments)
    {
        return new class implements CastsAttributes
        {
            public function get($model, $key, $value, $attributes)
            {
                if (isset($attributes[$key])) {
                    return new Collection(\json_decode(Crypt::decryptString($attributes[$key]), \true));
                }
                return null;
            }
            public function set($model, $key, $value, $attributes)
            {
                if (!\is_null($value)) {
                    return [$key => Crypt::encryptString(\json_encode($value))];
                }
                return null;
            }
        };
    }
}
