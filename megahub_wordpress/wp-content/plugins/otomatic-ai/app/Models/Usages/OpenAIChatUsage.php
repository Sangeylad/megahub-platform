<?php

namespace OtomaticAi\Models\Usages;

use OtomaticAi\Vendors\Carbon\Carbon;
use OtomaticAi\Vendors\Carbon\CarbonPeriod;
use OtomaticAi\Vendors\Illuminate\Database\Capsule\Manager as Database;
use OtomaticAi\Vendors\Illuminate\Support\Arr;

class OpenAIChatUsage extends Usage
{
    static private $prices = [
        [
            'model' => 'gpt-3.5-turbo',
            'prompt' => 0.0005,
            'completion' => 0.0015,
        ],
        [
            'model' => 'gpt-3.5-turbo-0301',
            'prompt' => 0.0015,
            'completion' => 0.002,
        ],
        [
            'model' => 'gpt-3.5-turbo-0613',
            'prompt' => 0.0015,
            'completion' => 0.002,
        ],
        [
            'model' => 'gpt-3.5-turbo-1106',
            'prompt' => 0.0010,
            'completion' => 0.0002,
        ],
        [
            'model' => 'gpt-3.5-turbo-0125',
            'prompt' => 0.0005,
            'completion' => 0.0015,
        ],
        [
            'model' => 'gpt-3.5-turbo-16k',
            'prompt' => 0.0015,
            'completion' => 0.0020,
        ],
        [
            'model' => 'gpt-3.5-turbo-16k-0613',
            'prompt' => 0.0010,
            'completion' => 0.0020,
        ],
        [
            'model' => 'gpt-4',
            'prompt' => 0.03,
            'completion' => 0.06,
        ],
        [
            'model' => 'gpt-4-0314',
            'prompt' => 0.03,
            'completion' => 0.06,
        ],
        [
            'model' => 'gpt-4-0613',
            'prompt' => 0.03,
            'completion' => 0.06,
        ],
        [
            'model' => 'gpt-4-turbo-preview',
            'prompt' => 0.01,
            'completion' => 0.03,
        ],
        [
            'model' => 'gpt-4-1106-preview',
            'prompt' => 0.01,
            'completion' => 0.03,
        ],
        [
            'model' => 'gpt-4-0125-preview',
            'prompt' => 0.01,
            'completion' => 0.03,
        ],
        [
            'model' => 'gpt-4o-2024-05-13',
            'prompt' => 0.005,
            'completion' => 0.015,
        ],
        [
            'model' => 'gpt-4-turbo-2024-04-09',
            'prompt' => 0.01,
            'completion' => 0.03,
        ],
        [
            'model' => 'gpt-4-32k',
            'prompt' => 0.06,
            'completion' => 0.12,
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
            ->where('provider', 'openai_chat');
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

        $amount = $promptTokens / 1000 * $costs['prompt'];
        $amount = $completionTokens / 1000 * $costs['completion'];

        return $amount;
    }
}
