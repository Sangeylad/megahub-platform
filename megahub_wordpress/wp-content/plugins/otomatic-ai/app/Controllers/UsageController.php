<?php

namespace OtomaticAi\Controllers;

use OtomaticAi\Models\Usages\MistralAIUsage;
use OtomaticAi\Models\Usages\OpenAIChatUsage;
use OtomaticAi\Models\Usages\OpenAIImageUsage;
use OtomaticAi\Models\Usages\StabilityAIUsage;
use OtomaticAi\Vendors\Illuminate\Support\Arr;

class UsageController extends Controller
{
    public function __invoke()
    {
        $this->verifyNonce();

        $this->validate([
            "provider" => ["nullable"],
        ]);

        switch ($this->input('provider')) {
            case "openai":
                $usages = [];

                $chatUsages = OpenAIChatUsage::monthly(12);
                $imageUsages = OpenAIImageUsage::monthly(12);

                $keys = array_unique(array_merge(array_keys($chatUsages), array_keys($imageUsages)));
                sort($keys);

                foreach ($keys as $key) {
                    $usages[$key] = [
                        "amount" => Arr::get($chatUsages, $key . '.amount', 0) + Arr::get($imageUsages, $key . '.amount', 0),
                        "details" => array_merge(Arr::get($chatUsages, $key . '.details', []), Arr::get($imageUsages, $key . '.details', []))
                    ];
                }

                return $this->response($usages);
                break;
            case "mistral_ai":
                $usages = MistralAIUsage::monthly(12);

                return $this->response($usages);
                break;
            case "stability_ai":
                $usages = StabilityAIUsage::monthly(12);

                return $this->response($usages);
                break;
            default:
                $usages = [];

                $openAIChatUsages = OpenAIChatUsage::monthly(12);
                $openAIImageUsages = OpenAIImageUsage::monthly(12);
                $mistralAIUsages = MistralAIUsage::monthly(12);
                $stabilityAIUsages = StabilityAIUsage::monthly(12);

                $keys = array_unique(array_merge(array_keys($openAIChatUsages), array_keys($openAIImageUsages), array_keys($stabilityAIUsages)));
                sort($keys);

                foreach ($keys as $key) {
                    $amount = 0;
                    $amount += Arr::get($openAIChatUsages, $key . '.amount', 0);
                    $amount += Arr::get($openAIImageUsages, $key . '.amount', 0);
                    $amount += Arr::get($stabilityAIUsages, $key . '.amount', 0);
                    $amount += Arr::get($mistralAIUsages, $key . '.amount', 0);

                    $details = [];
                    $details = array_merge($details, Arr::get($openAIChatUsages, $key . '.details', []));
                    $details = array_merge($details, Arr::get($openAIImageUsages, $key . '.details', []));
                    $details = array_merge($details, Arr::get($stabilityAIUsages, $key . '.details', []));
                    $details = array_merge($details, Arr::get($mistralAIUsages, $key . '.details', []));
                    $usages[$key] = [
                        "amount" => $amount,
                        "details" => $details
                    ];
                }

                return $this->response($usages);
        }

        $this->response();
    }
}
