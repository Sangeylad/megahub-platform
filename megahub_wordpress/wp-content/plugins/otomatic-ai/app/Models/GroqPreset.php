<?php

namespace OtomaticAi\Models;

use OtomaticAi\Api\Groq\Client as GroqClient;
use OtomaticAi\Api\Groq\PoolClient as PoolGroqClient;

class GroqPreset extends Preset
{
    /**
     * Create the Groq API payload
     *
     * @param array $params
     * @return array
     */
    public function payload(array $params = []): array
    {
        $model = $this->model;
        $model = str_replace("groq-", '', $model);

        switch ($model) {
            case "llama3-70b":
                $model = "llama3-70b-8192";
                break;
            case "mixtral-8x7b":
                $model = "mixtral-8x7b-32768";
                break;
        }

        $payload = [
            "model" => $model,
            "temperature" => $this->temperature ? intval($this->temperature) : 1,
            "top_p" => $this->top_p ? intval($this->top_p) : 1,
            "stream" => false,
            "messages" => $this->replaceMessagesVariables($params),
        ];

        if ($this->is_json) {
            $payload["response_format"] = [
                "type" => "json_object"
            ];
        };

        return $payload;
    }

    public function process(array $params = [])
    {
        $api = new GroqClient;
        return $api->chat($this->payload($params));
    }

    public function processPool(array $params = [])
    {
        $api = new PoolGroqClient;
        $params = array_map(function ($p) {
            return $this->payload($p);
        }, $params);
        return $api->chat($params);
    }
}
