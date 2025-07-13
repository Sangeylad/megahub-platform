<?php

namespace OtomaticAi\Models\Usages;

use OtomaticAi\Vendors\Carbon\Carbon;
use OtomaticAi\Vendors\Carbon\CarbonPeriod;
use OtomaticAi\Vendors\Illuminate\Database\Capsule\Manager as Database;
use OtomaticAi\Vendors\Illuminate\Support\Arr;

class StabilityAIUsage extends Usage
{
    static private $creditPrice = 0.01;
    static private $prices = [
        [
            'engine' =>  'stable-diffusion-xl-1024-v0-9',
            'steps' => [
                10 => 1.35,
                20 => 1.50,
                30 => 1.60,
                40 => 1.80,
                50 => 2,
                60 => 2.21,
                70 => 2.41,
                80 => 2.63,
                90 => 2.87,
                100 => 3.11,
                110 => 3.37,
                120 => 3.64,
                130 => 3.92,
                140 => 4.22,
                150 => 4.53,
            ]
        ],
        [
            'engine' =>  'stable-diffusion-xl-1024-v1-0',
            'steps' => [
                10 => 1.35,
                20 => 1.50,
                30 => 1.60,
                40 => 1.80,
                50 => 2,
                60 => 2.21,
                70 => 2.41,
                80 => 2.63,
                90 => 2.87,
                100 => 3.11,
                110 => 3.37,
                120 => 3.64,
                130 => 3.92,
                140 => 4.22,
                150 => 4.53,
            ]
        ],
        [
            'engine' => 'stable-diffusion-xl-beta-v2-2-2',
            'steps' => [
                10 => 0.17,
                20 => 0.33,
                30 => 0.50,
                40 => 0.67,
                50 => 0.83,
                60 => 1,
                70 => 1.17,
                80 => 1.33,
                90 => 1.50,
                100 => 1.67,
                110 => 1.83,
                120 => 2.00,
                130 => 2.17,
                140 => 2.33,
                150 => 2.50,
            ],
        ],
        [
            'engine' => 'stable_image_core',
            'steps' => [
                0 => 3,
            ],
        ],
        [
            'engine' => 'stable_image_sd3',
            'steps' => [
                0 => 6.5,
            ],
        ],
        [
            'engine' => 'stable_image_sd3_turbo',
            'steps' => [
                0 => 4,
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
            ->where('provider', 'stability_ai');
    }

    static public function monthly(int $months = 12, int $diff = 0)
    {
        $start = Carbon::now()->subMonth($months - 1)->startOfMonth();
        $stop = Carbon::now()->subMonth($diff)->endOfMonth();
        $usages = self::query()
            ->select([
                Database::raw("DATE_FORMAT(created_at, '%Y-%m') as 'month_date'"),
                Database::raw("JSON_UNQUOTE(JSON_EXTRACT(payload, '$.engine')) as 'engine'"),
                Database::raw("JSON_UNQUOTE(JSON_EXTRACT(payload, '$.steps')) as 'steps'"),
                Database::raw("SUM(JSON_UNQUOTE(JSON_EXTRACT(payload, '$.artifacts'))) as 'artifacts'"),
            ])
            ->groupBy([
                Database::raw("DATE_FORMAT(created_at, '%Y-%m')"),
                'engine',
                'steps'
            ])
            ->whereBetween('created_at', [$start, $stop])
            ->get();

        $usages = $usages->groupBy(['month_date', 'engine', 'steps']);

        $output = [];
        $period = CarbonPeriod::since($start)->month()->until($stop);
        foreach ($period as $date) {
            $date = $date->format('Y-m');

            $o = [
                "amount" => 0,
                "details" => [],
            ];

            if ($usages->has($date)) {
                foreach ($usages->get($date) as $engine => $usagesForEngine) {
                    if (!isset($o["details"][$engine])) {
                        $o["details"][$engine] = 0;
                    }
                    foreach ($usagesForEngine as $steps => $usageForStep) {
                        foreach ($usageForStep as $usage) {
                            $o["details"][$engine] += self::calculateCosts($engine, $steps, $usage->artifacts);
                        }
                    }
                    $o["amount"] += $o["details"][$engine];
                }
            }

            $output[$date] = $o;
        }

        return $output;
    }

    static private function calculateCosts($engine, $steps, $artifacts)
    {
        if (empty($steps)) {
            $steps = 10;
        }

        $costs = Arr::keyBy(self::$prices, 'engine');
        $costs = Arr::get($costs, $engine, ['steps' => [0 => 0]]);

        $steps = self::getClosestSteps($steps, array_keys(Arr::get($costs, "steps", [])));
        $creditsPerArtifact = Arr::get($costs, 'steps.' . $steps, 0);
        $credits = $artifacts * $creditsPerArtifact;

        $amount = $credits * self::$creditPrice;

        return $amount;
    }

    static private function getClosestSteps($search, $stepsList)
    {
        $closest = null;
        foreach ($stepsList as $item) {
            if ($closest === null || abs($search - $closest) > abs($item - $search)) {
                $closest = $item;
            }
        }
        return $closest;
    }
}
