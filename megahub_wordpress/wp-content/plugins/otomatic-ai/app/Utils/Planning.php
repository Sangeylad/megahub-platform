<?php

namespace OtomaticAi\Utils;

use OtomaticAi\Vendors\Carbon\Carbon;
use OtomaticAi\Vendors\Illuminate\Support\Arr;
use OtomaticAi\Vendors\Illuminate\Support\Collection;

class Planning
{
    public const MONDAY = "monday";
    public const TUESDAY = "tuesday";
    public const WEDNESDAY = "wednesday";
    public const THURSDAY = "thursday";
    public const FRIDAY = "friday";
    public const SATURDAY = "saturday";
    public const SUNDAY = "sunday";

    private $items;
    private $per_day = 1;
    private $weekdays = [
        self::MONDAY => true,
        self::TUESDAY => true,
        self::WEDNESDAY => true,
        self::THURSDAY => true,
        self::FRIDAY => true,
        self::SATURDAY => false,
        self::SUNDAY => false,
    ];
    private $start_time = [0, 0];
    private $end_time = [23, 59];

    public function __construct($items = [])
    {
        $this->setItems($items);
    }

    public function addItem($item)
    {
        $this->items->push($item);
    }

    public function setItems($items)
    {
        $this->items = new Collection($items);
    }

    public function perDay($value)
    {
        $value =  intval($value);
        $value =  max(1, $value);
        $this->per_day = $value;

        return $this;
    }

    public function startTime($hours, $minutes)
    {
        $hours = intval($hours);
        $hours = max(0, $hours);
        $hours = min(23, $hours);
        $minutes = intval($minutes);
        $minutes = max(0, $minutes);
        $minutes = min(59, $minutes);

        $this->start_time = [$hours, $minutes];

        return $this;
    }

    public function endTime($hours, $minutes)
    {
        $hours = intval($hours);
        $hours = max(0, $hours);
        $hours = min(23, $hours);
        $minutes = intval($minutes);
        $minutes = max(0, $minutes);
        $minutes = min(59, $minutes);

        $this->end_time = [$hours, $minutes];

        return $this;
    }

    public function weekdays(...$days)
    {
        $days = Arr::flatten($days);

        // reset weekdays
        foreach ($this->weekdays as $key => $value) {
            $this->weekdays[$key] = false;
        }

        // enable weekdays
        foreach ($days as $day) {
            if (isset($this->weekdays[$day])) {
                $this->weekdays[$day] = true;
            }
        }

        return $this;
    }

    public function each($callback)
    {
        $this->make()->each(function ($item, $key) use ($callback) {
            $callback($item, Carbon::createFromFormat("Y-m-d H:i", $key));
        });
    }

    private function make()
    {
        $date = Carbon::now();
        $items = $this->items->chunk($this->per_day);

        // set day
        $items = $items->keyBy(function () use (&$date) {
            $date = $this->getNextAvailableWeekday($date);
            $key = $date->format("Y-m-d");
            $date->addDay();
            return $key;
        });

        // set hours
        $items = $items->map(function ($elts, $key) {
            $start = Carbon::createFromFormat("Y-m-d", $key)->startOfDay()->setHour($this->start_time[0])->setMinute($this->start_time[1]);
            $end = $start->copy()->setHour($this->end_time[0])->setMinute($this->end_time[1]);
            $interval = $start->diffInMinutes($end);
            $interval = $elts->count() > 1 ? round($interval / ($elts->count() - 1)) : 0;
            return $elts->keyBy(function ($el, $key) use (&$start, $interval) {
                $key = $start->format("Y-m-d H:i");
                $start->addMinutes($interval);
                return $key;
            });
        });

        // make output
        $output = new Collection;
        $items->each(function ($elts) use (&$output) {
            $output = $output->merge($elts);
        });

        return $output;
    }

    private function getNextAvailableWeekday($date)
    {
        switch ($date->weekday()) {
            case Carbon::MONDAY:
                if ($this->weekdays[self::MONDAY]) {
                    return $date;
                } elseif ($this->weekdays[self::TUESDAY]) {
                    return $date->next(Carbon::TUESDAY);
                } elseif ($this->weekdays[self::WEDNESDAY]) {
                    return $date->next(Carbon::WEDNESDAY);
                } elseif ($this->weekdays[self::THURSDAY]) {
                    return $date->next(Carbon::THURSDAY);
                } elseif ($this->weekdays[self::FRIDAY]) {
                    return $date->next(Carbon::FRIDAY);
                } elseif ($this->weekdays[self::SATURDAY]) {
                    return $date->next(Carbon::SATURDAY);
                } elseif ($this->weekdays[self::SUNDAY]) {
                    return $date->next(Carbon::SUNDAY);
                }
                break;
            case Carbon::TUESDAY:
                if ($this->weekdays[self::TUESDAY]) {
                    return $date;
                } elseif ($this->weekdays[self::WEDNESDAY]) {
                    return $date->next(Carbon::WEDNESDAY);
                } elseif ($this->weekdays[self::THURSDAY]) {
                    return $date->next(Carbon::THURSDAY);
                } elseif ($this->weekdays[self::FRIDAY]) {
                    return $date->next(Carbon::FRIDAY);
                } elseif ($this->weekdays[self::SATURDAY]) {
                    return $date->next(Carbon::SATURDAY);
                } elseif ($this->weekdays[self::SUNDAY]) {
                    return $date->next(Carbon::SUNDAY);
                } else if ($this->weekdays[self::MONDAY]) {
                    return $date->next(Carbon::MONDAY);
                }
                break;
            case Carbon::WEDNESDAY:
                if ($this->weekdays[self::WEDNESDAY]) {
                    return $date;
                } elseif ($this->weekdays[self::THURSDAY]) {
                    return $date->next(Carbon::THURSDAY);
                } elseif ($this->weekdays[self::FRIDAY]) {
                    return $date->next(Carbon::FRIDAY);
                } elseif ($this->weekdays[self::SATURDAY]) {
                    return $date->next(Carbon::SATURDAY);
                } elseif ($this->weekdays[self::SUNDAY]) {
                    return $date->next(Carbon::SUNDAY);
                } else if ($this->weekdays[self::MONDAY]) {
                    return $date->next(Carbon::MONDAY);
                } elseif ($this->weekdays[self::TUESDAY]) {
                    return $date->next(Carbon::TUESDAY);
                }
                break;
            case Carbon::THURSDAY:
                if ($this->weekdays[self::THURSDAY]) {
                    return $date;
                } elseif ($this->weekdays[self::FRIDAY]) {
                    return $date->next(Carbon::FRIDAY);
                } elseif ($this->weekdays[self::SATURDAY]) {
                    return $date->next(Carbon::SATURDAY);
                } elseif ($this->weekdays[self::SUNDAY]) {
                    return $date->next(Carbon::SUNDAY);
                } else if ($this->weekdays[self::MONDAY]) {
                    return $date->next(Carbon::MONDAY);
                } elseif ($this->weekdays[self::TUESDAY]) {
                    return $date->next(Carbon::TUESDAY);
                } elseif ($this->weekdays[self::WEDNESDAY]) {
                    return $date->next(Carbon::WEDNESDAY);
                }
                break;
            case Carbon::FRIDAY:
                if ($this->weekdays[self::FRIDAY]) {
                    return $date;
                } elseif ($this->weekdays[self::SATURDAY]) {
                    return $date->next(Carbon::SATURDAY);
                } elseif ($this->weekdays[self::SUNDAY]) {
                    return $date->next(Carbon::SUNDAY);
                } else if ($this->weekdays[self::MONDAY]) {
                    return $date->next(Carbon::MONDAY);
                } elseif ($this->weekdays[self::TUESDAY]) {
                    return $date->next(Carbon::TUESDAY);
                } elseif ($this->weekdays[self::WEDNESDAY]) {
                    return $date->next(Carbon::WEDNESDAY);
                } elseif ($this->weekdays[self::THURSDAY]) {
                    return $date->next(Carbon::THURSDAY);
                }
                break;
            case Carbon::SATURDAY:
                if ($this->weekdays[self::SATURDAY]) {
                    return $date;
                } elseif ($this->weekdays[self::SUNDAY]) {
                    return $date->next(Carbon::SUNDAY);
                } else if ($this->weekdays[self::MONDAY]) {
                    return $date->next(Carbon::MONDAY);
                } elseif ($this->weekdays[self::TUESDAY]) {
                    return $date->next(Carbon::TUESDAY);
                } elseif ($this->weekdays[self::WEDNESDAY]) {
                    return $date->next(Carbon::WEDNESDAY);
                } elseif ($this->weekdays[self::THURSDAY]) {
                    return $date->next(Carbon::THURSDAY);
                } elseif ($this->weekdays[self::FRIDAY]) {
                    return $date->next(Carbon::FRIDAY);
                }
                break;
            case Carbon::SUNDAY:
                if ($this->weekdays[self::SUNDAY]) {
                    return $date;
                } else if ($this->weekdays[self::MONDAY]) {
                    return $date->next(Carbon::MONDAY);
                } elseif ($this->weekdays[self::TUESDAY]) {
                    return $date->next(Carbon::TUESDAY);
                } elseif ($this->weekdays[self::WEDNESDAY]) {
                    return $date->next(Carbon::WEDNESDAY);
                } elseif ($this->weekdays[self::THURSDAY]) {
                    return $date->next(Carbon::THURSDAY);
                } elseif ($this->weekdays[self::FRIDAY]) {
                    return $date->next(Carbon::FRIDAY);
                } elseif ($this->weekdays[self::SATURDAY]) {
                    return $date->next(Carbon::SATURDAY);
                }
                break;
        }

        return $date;
    }
}
