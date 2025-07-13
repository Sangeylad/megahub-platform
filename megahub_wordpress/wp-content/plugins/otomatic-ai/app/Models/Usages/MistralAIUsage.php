<?php

namespace OtomaticAi\Models\Usages;

use OtomaticAi\Vendors\Carbon\Carbon;
use OtomaticAi\Vendors\Carbon\CarbonPeriod;
use OtomaticAi\Vendors\Illuminate\Database\Capsule\Manager as Database;
use OtomaticAi\Vendors\Illuminate\Support\Arr;

class MistralAIUsage extends Usage
{
    static private $prices = [
        [
            'model' => 'mistral-medium-latest',
            'prompt' => 2.7, // per million tokens
            'completion' => 8.1, // per million tokens
        ],
        [
            'model' => 'mistral-large-latest',
            'prompt' => 8, // per million tokens
            'completion' => 24, // per million tokens
        ],
    ];

    /**
     * Get a new query builder for the model's table.
     *
     * @return \Illuminate\Database\Eloquent\Builder
     */
    public function newQuery()
    {
        return $this->registerGlobalScopes($this->newQueryWithoutScopes())
            ->where('provider', 'mistral_ai_chat');
    }

    static public function monthly(int $months = 12, int $diff = 0)
    {
        $start = Carbon::now()->subMonth($months - 1)->startOfMonth();
        $stop = Carbon::now()->subMonth($diff)->endOfMonth();
        $usages = self::query()
            ->select([
                Database::raw("DATE_FORMAT(created_at, '%Y-%m') as 'month_date'"),
                Database::raw("JSON_UNQUOTE(JSON_EXTRACT(payload, '$.model')) as 'model'"),
                Database::raw("SUM(JSON_UNQUOTE(JSON_EXTRACT(payload, '$.prompt_tokens'))) as 'prompt_tokens'"),
                Database::raw("SUM(JSON_UNQUOTE(JSON_EXTRACT(payload, '$.completion_tokens'))) as 'completion_tokens'"),
            ])
            ->groupBy([
                Database::raw("DATE_FORMAT(created_at, '%Y-%m')"),
                'model'
            ])
            ->whereBetween('created_at', [$start, $stop])
            ->get();

        $usages = $usages->groupBy(['month_date', 'model']);

        $output = [];
        $period = CarbonPeriod::since($start)->month()->until($stop);
        foreach ($period as $date) {
            $date = $date->format('Y-m');

            $o = [
                "amount" => 0,
                "details" => [],
            ];

            if ($usages->has($date)) {
                foreach ($usages->get($date) as $model => $usagesForModel) {
                    if (!isset($o["details"][$model])) {
                        $o["details"][$model] = 0;
                    }
                    foreach ($usagesForModel as $usage) {
                        $o["details"][$model] += self::calculateCosts($model, $usage->prompt_tokens, $usage->completion_tokens);
                    }

                    $o["amount"] += $o["details"][$model];
                }
            }

            $output[$date] = $o;
        }

        return $output;
    }

    static private function calculateCosts($model, $promptTokens, $completionTokens)
    {
        $amount = 0;
        $costs = Arr::keyBy(self::$prices, 'model');
        $costs = Arr::get($costs, $model, ['prompt' => 0, 'completion' => 0]);

        $amount = $promptTokens / 1000000 * $costs['prompt'];
        $amount = $completionTokens / 1000000 * $costs['completion'];

        return $amount;
    }
}
