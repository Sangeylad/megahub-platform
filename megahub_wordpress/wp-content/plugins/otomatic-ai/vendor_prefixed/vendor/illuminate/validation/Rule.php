<?php

namespace OtomaticAi\Vendors\Illuminate\Validation;

use OtomaticAi\Vendors\Illuminate\Contracts\Support\Arrayable;
use OtomaticAi\Vendors\Illuminate\Support\Traits\Macroable;
use OtomaticAi\Vendors\Illuminate\Validation\Rules\Dimensions;
use OtomaticAi\Vendors\Illuminate\Validation\Rules\Exists;
use OtomaticAi\Vendors\Illuminate\Validation\Rules\In;
use OtomaticAi\Vendors\Illuminate\Validation\Rules\NotIn;
use OtomaticAi\Vendors\Illuminate\Validation\Rules\RequiredIf;
use OtomaticAi\Vendors\Illuminate\Validation\Rules\Unique;
class Rule
{
    use Macroable;
    /**
     * Create a new conditional rule set.
     *
     * @param  callable|bool  $condition
     * @param  array|string  $rules
     * @param  array|string  $defaultRules
     * @return \Illuminate\Validation\ConditionalRules
     */
    public static function when($condition, $rules, $defaultRules = [])
    {
        return new ConditionalRules($condition, $rules, $defaultRules);
    }
    /**
     * Get a dimensions constraint builder instance.
     *
     * @param  array  $constraints
     * @return \Illuminate\Validation\Rules\Dimensions
     */
    public static function dimensions(array $constraints = [])
    {
        return new Dimensions($constraints);
    }
    /**
     * Get an exists constraint builder instance.
     *
     * @param  string  $table
     * @param  string  $column
     * @return \Illuminate\Validation\Rules\Exists
     */
    public static function exists($table, $column = 'NULL')
    {
        return new Exists($table, $column);
    }
    /**
     * Get an in constraint builder instance.
     *
     * @param  \Illuminate\Contracts\Support\Arrayable|array|string  $values
     * @return \Illuminate\Validation\Rules\In
     */
    public static function in($values)
    {
        if ($values instanceof Arrayable) {
            $values = $values->toArray();
        }
        return new In(\is_array($values) ? $values : \func_get_args());
    }
    /**
     * Get a not_in constraint builder instance.
     *
     * @param  \Illuminate\Contracts\Support\Arrayable|array|string  $values
     * @return \Illuminate\Validation\Rules\NotIn
     */
    public static function notIn($values)
    {
        if ($values instanceof Arrayable) {
            $values = $values->toArray();
        }
        return new NotIn(\is_array($values) ? $values : \func_get_args());
    }
    /**
     * Get a required_if constraint builder instance.
     *
     * @param  callable|bool  $callback
     * @return \Illuminate\Validation\Rules\RequiredIf
     */
    public static function requiredIf($callback)
    {
        return new RequiredIf($callback);
    }
    /**
     * Get a unique constraint builder instance.
     *
     * @param  string  $table
     * @param  string  $column
     * @return \Illuminate\Validation\Rules\Unique
     */
    public static function unique($table, $column = 'NULL')
    {
        return new Unique($table, $column);
    }
}
