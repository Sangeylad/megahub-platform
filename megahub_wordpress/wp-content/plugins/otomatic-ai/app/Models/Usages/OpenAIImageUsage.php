<?php

namespace OtomaticAi\Models\Usages;

use OtomaticAi\Vendors\Carbon\Carbon;
use OtomaticAi\Vendors\Carbon\CarbonPeriod;
use OtomaticAi\Vendors\Illuminate\Database\Capsule\Manager as Database;
use OtomaticAi\Vendors\Illuminate\Support\Arr;

class OpenAIImageUsage extends Usage
{
    static private $prices = [
        [
            'model' => 'dall-e-2',
            'sizes' => [
                "standard" => [
                    '256x256' => 0.016,
                    '512x512' => 0.018,
                    '1024x1024' => 0.020,
                ]
            ]
        ],
        [
            'model' => 'dall-e-3',
            'sizes' => [
                "standard" => [
                    '1024x1024' => 0.040,
                    '1024x1792' => 0.080,
                    '1792x1024' => 0.080,
                ],
                "hd" => [
                    '1024x1024' => 0.080,
                    '1024x1792' => 0.120,
                    '1792x1024' => 0.120,
                ]
            ],
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
            ->where('provider', 'openai_image');
    }

    static public function monthly(int $months = 12, int $diff = 0)
    {
        $start = Carbon::now()->subMonth($months - 1)->startOfMonth();
        $stop = Carbon::now()->subMonth($diff)->endOfMonth();
        $usages = self::query()
            ->select([
                Database::raw("DATE_FORMAT(created_at, '%Y-%m') as 'month_date'"),
                Database::raw("JSON_UNQUOTE(JSON_EXTRACT(payload, '$.model')) as 'model'"),
                Database::raw("JSON_UNQUOTE(JSON_EXTRACT(payload, '$.quality')) as 'quality'"),
                Database::raw("JSON_UNQUOTE(JSON_EXTRACT(payload, '$.size')) as 'size'"),
                Database::raw("SUM(JSON_UNQUOTE(JSON_EXTRACT(payload, '$.n'))) as 'n'"),
            ])
            ->groupBy([
                Database::raw("DATE_FORMAT(created_at, '%Y-%m')"),
                'model',
                'quality',
                'size'
            ])
            ->whereBetween('created_at', [$start, $stop])
            ->get();

        $usages = $usages->groupBy(['month_date', 'model', 'quality', 'size']);

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
                    foreach ($usagesForModel as $quality => $usageForQuality) {
                        foreach ($usageForQuality as $size => $usageForSize) {
                            foreach ($usageForSize as $usage) {
                                $o["details"][$model] += self::calculateCosts($model, $quality, $size, $usage->n);
                            }
                        }
                    }

                    $o["amount"] += $o["details"][$model];
                }
            }

            $output[$date] = $o;
        }

        return $output;
    }

    static private function calculateCosts($model, $quality, $size, $n)
    {
        $costs = Arr::keyBy(self::$prices, 'model');
        $costs = Arr::get($costs, $model, []);
        $price = Arr::get($costs, 'sizes.' . $quality . '.' . $size, 0);

        return $n * $price;
    }
}
