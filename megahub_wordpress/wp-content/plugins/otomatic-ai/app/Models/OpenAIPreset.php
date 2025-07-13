<?php

namespace OtomaticAi\Models;

use OtomaticAi\Api\OpenAi\Client as OpenAiClient;
use OtomaticAi\Api\OpenAi\PoolClient as PoolOpenAiClient;

class OpenAIPreset extends Preset
{
    /**
     * Create the OpenAI API payload
     *
     * @param array $params
     * @return array
     */
    public function payload(array $params = []): array
    {
        $model = $this->model;
        $payload = [
            "model" => $model,
            "temperature" => $this->temperature ? intval($this->temperature) : 1,
            "top_p" => $this->top_p ? intval($this->top_p) : 1,
            "presence_penalty" => $this->presence_penalty ? round($this->presence_penalty, 2) : 0,
            "frequency_penalty" => $this->frequency_penalty ? round($this->frequency_penalty, 2) : 0,
            "n" => 1,
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
        $api = new OpenAiClient;
        return $api->chat($this->payload($params));
    }

    public function processPool(array $params = [])
    {
        $api = new PoolOpenAiClient;
        $params = array_map(function ($p) {
            return $this->payload($p);
        }, $params);

        return $api->chat($params);
    }
}
