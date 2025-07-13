<?php

namespace OtomaticAi\Controllers;

use Exception;
use OtomaticAi\Api\OtomaticAi\Client;
use OtomaticAi\Vendors\Carbon\Carbon;
use OtomaticAi\Vendors\Illuminate\Support\Arr;

class PricingPlanController extends Controller
{
    const CACHE_OPTION_NAME = "otomatic_ai_pricing_plans_cache";

    public function __invoke()
    {
        $this->verifyNonce();

        $output = [];

        if (function_exists('get_option')) {
            $cache = get_option(self::CACHE_OPTION_NAME, null);

            // fetch or refresh cache
            if (
                empty($cache) ||
                Carbon::createFromFormat(
                    "Y-m-d H:i:s",
                    Arr::get(
                        $cache,
                        "cached_at",
                        Carbon::now()->subMonth()
                    )
                )
                ->lt(
                    Carbon::now()->subMinutes(5)
                )
            ) {
                try {
                    $api = new Client;
                    $output = $api->pricingPlans();

                    $cache = [
                        "data" => $output,
                        "cached_at" => Carbon::now()->format("Y-m-d H:i:s"),
                    ];

                    if (function_exists('update_option')) {
                        update_option(self::CACHE_OPTION_NAME, $cache, false);
                    }
                } catch (Exception $e) {
                }
            } else {
                $output = Arr::get($cache, "data", $output);
            }
        }

        $this->response($output);
    }
}
