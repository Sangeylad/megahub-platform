<?php

namespace OtomaticAi\Models;

use OtomaticAi\Api\MistralAi\Client as MistralAiClient;
use OtomaticAi\Api\MistralAi\PoolClient as PoolMistralAiClient;

class MistralAIPreset extends Preset
{
    /**
     * Create the Mistral AI API payload
     *
     * @param array $params
     * @return array
     */
    public function payload(array $params = []): array
    {
        $model = $this->model;
        if ($model === "mistral-small") {
            $model = "mistral-small-latest";
        } else if ($model === "mistral-medium") {
            $model = "mistral-medium-latest";
        } else if ($model === "mistral-large") {
            $model = "mistral-large-latest";
        }

        $payload = [
            "model" => $model,
            "temperature" => $this->temperature ? intval($this->temperature) : 1,
            "top_p" => $this->top_p ? intval($this->top_p) : 1,
            "stream" => false,
            "messages" => $this->replaceMessagesVariables($params),
        ];

        return $payload;
    }

    public function process(array $params = [])
    {
        $api = new MistralAiClient;
        return $api->chat($this->payload($params));
    }

    public function processPool(array $params = [])
    {
        $api = new PoolMistralAiClient;
        $params = array_map(function ($p) {
            return $this->payload($p);
        }, $params);
        return $api->chat($params);
    }
}
