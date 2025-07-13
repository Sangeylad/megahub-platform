<?php

namespace OtomaticAi\Utils;

use Exception;
use OtomaticAi\Api\OtomaticAi\Client;
use OtomaticAi\Api\OtomaticAi\Exceptions\UnauthorizedException;
use OtomaticAi\Vendors\Carbon\Carbon;
use OtomaticAi\Vendors\Illuminate\Support\Arr;

class Auth
{
    static private $token = null;
    static private $domain = null;
    static private $checked = false;

    const TOKEN_OPTION_NAME = "otomatic_ai_token";
    const DOMAIN_OPTION_NAME = "otomatic_ai_domain";

    static public function token()
    {
        if (self::$token === null && function_exists('get_option')) {
            self::$token = get_option(self::TOKEN_OPTION_NAME, null);

            // verify token
            if (self::$token !== null && !self::$checked) {
                try {
                    $api = new Client;
                    $api->check(defined('OTOMATIC_AI_VERSION') ? OTOMATIC_AI_VERSION : null);
                    self::$checked = true;
                } catch (UnauthorizedException $e) {
                    return self::logout();
                }
            }
        }
        return self::$token;
    }

    static public function check()
    {
        return self::token() !== null;
    }

    static public function login($email, $password)
    {
        $api = new Client;
        $response = $api->login($email, $password, get_site_url());

        $token = Arr::get($response, "token", null);
        if (!empty($token) && function_exists('update_option') && update_option(self::TOKEN_OPTION_NAME, $token, false)) {
            return true;
        }

        throw new Exception("Unable to store the auth token.");
    }

    static public function logout()
    {
        if (function_exists('delete_option')) {
            delete_option(self::DOMAIN_OPTION_NAME);
            if (delete_option(self::TOKEN_OPTION_NAME)) {
                self::$token = null;
                return;
            }
        }

        if (self::check()) {
            throw new Exception("Unable to delete the auth token.");
        }
    }

    static public function domain()
    {
        if (self::$domain === null && function_exists('get_option')) {
            self::$domain = get_option(self::DOMAIN_OPTION_NAME, null);

            // fetch or refresh domain
            if (
                self::$domain === null ||
                Carbon::createFromFormat(
                    "Y-m-d H:i:s",
                    Arr::get(
                        self::$domain,
                        "cached_at",
                        Carbon::now()->subMonth()
                    )
                )
                ->lt(
                    Carbon::now()->subMinutes(1)
                )
            ) {
                try {
                    $api = new Client;
                    $domain = $api->domain();
                    self::$domain = $domain;
                    self::$domain["cached_at"] = Carbon::now()->format("Y-m-d H:i:s");
                    if (function_exists('update_option')) {
                        update_option(self::DOMAIN_OPTION_NAME, self::$domain, false);
                    }
                } catch (Exception $e) {
                    throw $e;
                }
            }
        }

        return self::$domain;
    }

    static public function refreshDomain()
    {
        if (function_exists('delete_option')) {
            if (delete_option(self::DOMAIN_OPTION_NAME)) {
                self::domain();
            }
        }
    }

    static public function isPremium(): bool
    {
        try {
            return Arr::get(self::domain(), "is_premium", false);
        } catch (Exception $e) {
            return false;
        }
    }

    static public function isTrial(): bool
    {
        try {
            return Arr::get(self::domain(), "user.trial.status", "active") && (Arr::get(self::domain(), "user.trial.max_usage", 0) - Arr::get(self::domain(), "user.trial.usage", 0) > 0);
        } catch (Exception $e) {
            return false;
        }
    }
}
