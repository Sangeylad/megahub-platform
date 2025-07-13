<?php

namespace OtomaticAi\Models;

use OtomaticAi\Api\OtomaticAi\Client;
use OtomaticAi\Vendors\Illuminate\Database\Eloquent\Model;
use OtomaticAi\Vendors\Illuminate\Support\Arr;
use OtomaticAi\Vendors\Illuminate\Support\Str;

class Preset extends Model
{
    protected $fillable = ["model", "name", "messages", "temperature", "top_p", "presence_penalty", "frequency_penalty", "is_json"];

    protected $casts = [
        'is_json' => 'boolean',
        'messages' => 'array',
    ];

    /**
     * Create a new Eloquent model instance.
     *
     * @param  array  $attributes
     * @return void
     */
    public function __construct(array $attributes = [])
    {
        global $wpdb;

        $this->table = $wpdb->prefix . 'otomatic_ai_presets';
        parent::__construct($attributes);
    }

    static function findFromAPI(string $role)
    {
        $client = new Client;

        return self::make($client->findOpenAIPreset($role));
    }

    static function make($params)
    {
        if (Str::startsWith($params["model"], ["groq-"])) {
            return new GroqPreset($params);
        }

        if (Str::startsWith($params["model"], "mistral-")) {
            return new MistralAIPreset($params);
        }

        return new OpenAIPreset($params);
    }

    protected function replaceMessagesVariables($params)
    {
        $messages = [];

        foreach ($this->messages as $message) {

            foreach ($params as $key => $value) {
                if (empty($value)) {
                    $value = "";
                }

                $key = strtoupper($key);

                $message["content"] = str_replace("[" . $key . "]", $value, $message["content"]);

                $message["content"] = preg_replace_callback("/\[IF;" . $key . "\](.*?)(?:\[ELSE\](.*?))?\[ENDIF\]/s", function ($matches) use ($key, $value) {
                    $trueValue = Arr::get($matches, 1);
                    $falseValue = Arr::get($matches, 2);
                    if (boolval($value)) {
                        if (!empty($trueValue)) {
                            return $trueValue;
                        }
                    } else {
                        if (!empty($falseValue)) {
                            return $falseValue;
                        }
                    }
                    return "";
                }, $message["content"]);
            }

            $messages[] = $message;
        }

        return $messages;
    }
}
