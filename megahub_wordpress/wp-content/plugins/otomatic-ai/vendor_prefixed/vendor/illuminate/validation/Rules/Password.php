<?php

namespace OtomaticAi\Vendors\Illuminate\Validation\Rules;

use OtomaticAi\Vendors\Illuminate\Container\Container;
use OtomaticAi\Vendors\Illuminate\Contracts\Validation\DataAwareRule;
use OtomaticAi\Vendors\Illuminate\Contracts\Validation\Rule;
use OtomaticAi\Vendors\Illuminate\Contracts\Validation\UncompromisedVerifier;
use OtomaticAi\Vendors\Illuminate\Contracts\Validation\ValidatorAwareRule;
use OtomaticAi\Vendors\Illuminate\Support\Arr;
use OtomaticAi\Vendors\Illuminate\Support\Facades\Validator;
use OtomaticAi\Vendors\Illuminate\Support\Traits\Conditionable;
use InvalidArgumentException;
class Password implements Rule, DataAwareRule, ValidatorAwareRule
{
    use Conditionable;
    /**
     * The validator performing the validation.
     *
     * @var \Illuminate\Contracts\Validation\Validator
     */
    protected $validator;
    /**
     * The data under validation.
     *
     * @var array
     */
    protected $data;
    /**
     * The minimum size of the password.
     *
     * @var int
     */
    protected $min = 8;
    /**
     * If the password requires at least one uppercase and one lowercase letter.
     *
     * @var bool
     */
    protected $mixedCase = \false;
    /**
     * If the password requires at least one letter.
     *
     * @var bool
     */
    protected $letters = \false;
    /**
     * If the password requires at least one number.
     *
     * @var bool
     */
    protected $numbers = \false;
    /**
     * If the password requires at least one symbol.
     *
     * @var bool
     */
    protected $symbols = \false;
    /**
     * If the password should has not been compromised in data leaks.
     *
     * @var bool
     */
    protected $uncompromised = \false;
    /**
     * The number of times a password can appear in data leaks before being consider compromised.
     *
     * @var int
     */
    protected $compromisedThreshold = 0;
    /**
     * Additional validation rules that should be merged into the default rules during validation.
     *
     * @var array
     */
    protected $customRules = [];
    /**
     * The failure messages, if any.
     *
     * @var array
     */
    protected $messages = [];
    /**
     * The callback that will generate the "default" version of the password rule.
     *
     * @var string|array|callable|null
     */
    public static $defaultCallback;
    /**
     * Create a new rule instance.
     *
     * @param  int  $min
     * @return void
     */
    public function __construct($min)
    {
        $this->min = \max((int) $min, 1);
    }
    /**
     * Set the default callback to be used for determining a password's default rules.
     *
     * If no arguments are passed, the default password rule configuration will be returned.
     *
     * @param  static|callable|null  $callback
     * @return static|null
     */
    public static function defaults($callback = null)
    {
        if (\is_null($callback)) {
            return static::default();
        }
        if (!\is_callable($callback) && !$callback instanceof static) {
            throw new InvalidArgumentException('The given callback should be callable or an instance of ' . static::class);
        }
        static::$defaultCallback = $callback;
    }
    /**
     * Get the default configuration of the password rule.
     *
     * @return static
     */
    public static function default()
    {
        $password = \is_callable(static::$defaultCallback) ? \call_user_func(static::$defaultCallback) : static::$defaultCallback;
        return $password instanceof Rule ? $password : static::min(8);
    }
    /**
     * Get the default configuration of the password rule and mark the field as required.
     *
     * @return array
     */
    public static function required()
    {
        return ['required', static::default()];
    }
    /**
     * Get the default configuration of the password rule and mark the field as sometimes being required.
     *
     * @return array
     */
    public static function sometimes()
    {
        return ['sometimes', static::default()];
    }
    /**
     * Set the performing validator.
     *
     * @param  \Illuminate\Contracts\Validation\Validator  $validator
     * @return $this
     */
    public function setValidator($validator)
    {
        $this->validator = $validator;
        return $this;
    }
    /**
     * Set the data under validation.
     *
     * @param  array  $data
     * @return $this
     */
    public function setData($data)
    {
        $this->data = $data;
        return $this;
    }
    /**
     * Sets the minimum size of the password.
     *
     * @param  int  $size
     * @return $this
     */
    public static function min($size)
    {
        return new static($size);
    }
    /**
     * Ensures the password has not been compromised in data leaks.
     *
     * @param  int  $threshold
     * @return $this
     */
    public function uncompromised($threshold = 0)
    {
        $this->uncompromised = \true;
        $this->compromisedThreshold = $threshold;
        return $this;
    }
    /**
     * Makes the password require at least one uppercase and one lowercase letter.
     *
     * @return $this
     */
    public function mixedCase()
    {
        $this->mixedCase = \true;
        return $this;
    }
    /**
     * Makes the password require at least one letter.
     *
     * @return $this
     */
    public function letters()
    {
        $this->letters = \true;
        return $this;
    }
    /**
     * Makes the password require at least one number.
     *
     * @return $this
     */
    public function numbers()
    {
        $this->numbers = \true;
        return $this;
    }
    /**
     * Makes the password require at least one symbol.
     *
     * @return $this
     */
    public function symbols()
    {
        $this->symbols = \true;
        return $this;
    }
    /**
     * Specify additional validation rules that should be merged with the default rules during validation.
     *
     * @param  string|array  $rules
     * @return $this
     */
    public function rules($rules)
    {
        $this->customRules = Arr::wrap($rules);
        return $this;
    }
    /**
     * Determine if the validation rule passes.
     *
     * @param  string  $attribute
     * @param  mixed  $value
     * @return bool
     */
    public function passes($attribute, $value)
    {
        $this->messages = [];
        $validator = Validator::make($this->data, [$attribute => \array_merge(['string', 'min:' . $this->min], $this->customRules)], $this->validator->customMessages, $this->validator->customAttributes)->after(function ($validator) use($attribute, $value) {
            if (!\is_string($value)) {
                return;
            }
            $value = (string) $value;
            if ($this->mixedCase && !\preg_match('/(\\p{Ll}+.*\\p{Lu})|(\\p{Lu}+.*\\p{Ll})/u', $value)) {
                $validator->errors()->add($attribute, 'The :attribute must contain at least one uppercase and one lowercase letter.');
            }
            if ($this->letters && !\preg_match('/\\pL/u', $value)) {
                $validator->errors()->add($attribute, 'The :attribute must contain at least one letter.');
            }
            if ($this->symbols && !\preg_match('/\\p{Z}|\\p{S}|\\p{P}/u', $value)) {
                $validator->errors()->add($attribute, 'The :attribute must contain at least one symbol.');
            }
            if ($this->numbers && !\preg_match('/\\pN/u', $value)) {
                $validator->errors()->add($attribute, 'The :attribute must contain at least one number.');
            }
        });
        if ($validator->fails()) {
            return $this->fail($validator->messages()->all());
        }
        if ($this->uncompromised && !Container::getInstance()->make(UncompromisedVerifier::class)->verify(['value' => $value, 'threshold' => $this->compromisedThreshold])) {
            return $this->fail('The given :attribute has appeared in a data leak. Please choose a different :attribute.');
        }
        return \true;
    }
    /**
     * Get the validation error message.
     *
     * @return array
     */
    public function message()
    {
        return $this->messages;
    }
    /**
     * Adds the given failures, and return false.
     *
     * @param  array|string  $messages
     * @return bool
     */
    protected function fail($messages)
    {
        $messages = \OtomaticAi\Vendors\collect(Arr::wrap($messages))->map(function ($message) {
            return $this->validator->getTranslator()->get($message);
        })->all();
        $this->messages = \array_merge($this->messages, $messages);
        return \false;
    }
}
