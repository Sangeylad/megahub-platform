<?php

namespace OtomaticAi\Utils;

abstract class Scheduler
{
    const EVERY_MINUTES = "* * * * *";
    const EVERY_TWO_MINUTES = "*/2 * * * *";
    const EVERY_THREE_MINUTES = "*/3 * * * *";
    const EVERY_FIVE_MINUTES = "*/5 * * * *";
    const EVERY_TEN_MINUTES = "*/10 * * * *";
    const EVERY_FIFTEEN_MINUTES = "*/15 * * * *";
    const EVERY_THIRTY_MINUTES = "*/30 * * * *";
    const EVERY_HOURS = "0 * * * *";
    const EVERY_DAYS = "0 0 * * *";
    const EVERY_WEEKS = "0 0 * * 0";
    const EVERY_MONTHS = "0 0  * *";
    const EVERY_YEARS = "* * 1 1 *";

    /**
     * Initialise the Scheduler
     *
     * @return void
     */
    static public function init()
    {
        add_filter('action_scheduler_queue_runner_time_limit', function ($timeLimit) {
            return 60;
        });
    }

    /**
     * Register a new schedule hook
     *
     * @param string $hook
     * @param callable $callback
     * @param int $args
     * @return void
     */
    static public function register($hook, $callback, $args = 1)
    {
        add_action($hook, $callback, 10, $args);
    }

    /**
     * Schedule an action that recurs on a cron-like schedule.
     *
     * @param string $hook
     * @param string $schedule
     * @param array $args
     * @return void
     */
    static public function schedule($hook, $schedule = Scheduler::EVERY_HOURS, $args = [])
    {
        $func = function () use ($hook, $schedule, $args) {

            if (false === as_has_scheduled_action($hook)) {
                as_schedule_cron_action(strtotime("now"), $schedule, $hook, $args, OTOMATIC_AI_NAME);
            }
        };

        if (did_action("action_scheduler_init")) {
            $func();
        } else {
            add_action("action_scheduler_init", $func);
        }
    }

    /**
     * Schedule an action that recurs on a cron-like schedule.
     *
     * @param string $hook
     * @param string $schedule
     * @param array $args
     * @return void
     */
    static public function single($hook, $args = [])
    {
        $func = function () use ($hook, $args) {
            as_enqueue_async_action($hook, $args, OTOMATIC_AI_NAME);
        };

        if (did_action("action_scheduler_init")) {
            $func();
        } else {
            add_action("action_scheduler_init", $func);
        }
    }

    /**
     * Find scheduled actions.
     *
     * @param string $hook
     * @param array $args
     * @return array
     */
    static public function get($hook, $args = [], $options = '')
    {
        $options = array_merge([
            "hook" => $hook,
            "args" => $args,
            "group" => OTOMATIC_AI_NAME,
        ], $options);

        return as_get_scheduled_actions($options);
    }
}
