<?php

/**
 * This file is part of the Carbon package.
 *
 * (c) Brian Nesbitt <brian@nesbot.com>
 *
 * For the full copyright and license information, please view the LICENSE
 * file that was distributed with this source code.
 */
namespace OtomaticAi\Vendors\Carbon;

use OtomaticAi\Vendors\Carbon\Exceptions\InvalidCastException;
use OtomaticAi\Vendors\Carbon\Exceptions\InvalidTimeZoneException;
use DateTimeInterface;
use DateTimeZone;
use Throwable;
class CarbonTimeZone extends DateTimeZone
{
    public function __construct($timezone = null)
    {
        parent::__construct(static::getDateTimeZoneNameFromMixed($timezone));
    }
    protected static function parseNumericTimezone($timezone)
    {
        if ($timezone <= -100 || $timezone >= 100) {
            throw new InvalidTimeZoneException('Absolute timezone offset cannot be greater than 100.');
        }
        return ($timezone >= 0 ? '+' : '') . \ltrim($timezone, '+') . ':00';
    }
    protected static function getDateTimeZoneNameFromMixed($timezone)
    {
        if ($timezone === null) {
            return \date_default_timezone_get();
        }
        if (\is_string($timezone)) {
            $timezone = \preg_replace('/^\\s*([+-]\\d+)(\\d{2})\\s*$/', '$1:$2', $timezone);
        }
        if (\is_numeric($timezone)) {
            return static::parseNumericTimezone($timezone);
        }
        return $timezone;
    }
    protected static function getDateTimeZoneFromName(&$name)
    {
        return @\timezone_open($name = (string) static::getDateTimeZoneNameFromMixed($name));
    }
    /**
     * Cast the current instance into the given class.
     *
     * @param string $className The $className::instance() method will be called to cast the current object.
     *
     * @return DateTimeZone
     */
    public function cast(string $className)
    {
        if (!\method_exists($className, 'instance')) {
            if (\is_a($className, DateTimeZone::class, \true)) {
                return new $className($this->getName());
            }
            throw new InvalidCastException("{$className} has not the instance() method needed to cast the date.");
        }
        return $className::instance($this);
    }
    /**
     * Create a CarbonTimeZone from mixed input.
     *
     * @param DateTimeZone|string|int|null $object     original value to get CarbonTimeZone from it.
     * @param DateTimeZone|string|int|null $objectDump dump of the object for error messages.
     *
     * @throws InvalidTimeZoneException
     *
     * @return false|static
     */
    public static function instance($object = null, $objectDump = null)
    {
        $tz = $object;
        if ($tz instanceof static) {
            return $tz;
        }
        if ($tz === null) {
            return new static();
        }
        if (!$tz instanceof DateTimeZone) {
            $tz = static::getDateTimeZoneFromName($object);
        }
        if ($tz !== \false) {
            return new static($tz->getName());
        }
        if (Carbon::isStrictModeEnabled()) {
            throw new InvalidTimeZoneException('Unknown or bad timezone (' . ($objectDump ?: $object) . ')');
        }
        return \false;
    }
    /**
     * Returns abbreviated name of the current timezone according to DST setting.
     *
     * @param bool $dst
     *
     * @return string
     */
    public function getAbbreviatedName($dst = \false)
    {
        $name = $this->getName();
        foreach ($this->listAbbreviations() as $abbreviation => $zones) {
            foreach ($zones as $zone) {
                if ($zone['timezone_id'] === $name && $zone['dst'] == $dst) {
                    return $abbreviation;
                }
            }
        }
        return 'unknown';
    }
    /**
     * @alias getAbbreviatedName
     *
     * Returns abbreviated name of the current timezone according to DST setting.
     *
     * @param bool $dst
     *
     * @return string
     */
    public function getAbbr($dst = \false)
    {
        return $this->getAbbreviatedName($dst);
    }
    /**
     * Get the offset as string "sHH:MM" (such as "+00:00" or "-12:30").
     *
     * @param DateTimeInterface|null $date
     *
     * @return string
     */
    public function toOffsetName(DateTimeInterface $date = null)
    {
        return static::getOffsetNameFromMinuteOffset($this->getOffset($date ?: Carbon::now($this)) / 60);
    }
    /**
     * Returns a new CarbonTimeZone object using the offset string instead of region string.
     *
     * @param DateTimeInterface|null $date
     *
     * @return CarbonTimeZone
     */
    public function toOffsetTimeZone(DateTimeInterface $date = null)
    {
        return new static($this->toOffsetName($date));
    }
    /**
     * Returns the first region string (such as "America/Toronto") that matches the current timezone or
     * false if no match is found.
     *
     * @see timezone_name_from_abbr native PHP function.
     *
     * @param DateTimeInterface|null $date
     * @param int                    $isDst
     *
     * @return string|false
     */
    public function toRegionName(DateTimeInterface $date = null, $isDst = 1)
    {
        $name = $this->getName();
        $firstChar = \substr($name, 0, 1);
        if ($firstChar !== '+' && $firstChar !== '-') {
            return $name;
        }
        $date = $date ?: Carbon::now($this);
        // Integer construction no longer supported since PHP 8
        // @codeCoverageIgnoreStart
        try {
            $offset = @$this->getOffset($date) ?: 0;
        } catch (Throwable $e) {
            $offset = 0;
        }
        // @codeCoverageIgnoreEnd
        $name = @\timezone_name_from_abbr('', $offset, $isDst);
        if ($name) {
            return $name;
        }
        foreach (\timezone_identifiers_list() as $timezone) {
            if (Carbon::instance($date)->tz($timezone)->getOffset() === $offset) {
                return $timezone;
            }
        }
        return \false;
    }
    /**
     * Returns a new CarbonTimeZone object using the region string instead of offset string.
     *
     * @param DateTimeInterface|null $date
     *
     * @return CarbonTimeZone|false
     */
    public function toRegionTimeZone(DateTimeInterface $date = null)
    {
        $tz = $this->toRegionName($date);
        if ($tz !== \false) {
            return new static($tz);
        }
        if (Carbon::isStrictModeEnabled()) {
            throw new InvalidTimeZoneException('Unknown timezone for offset ' . $this->getOffset($date ?: Carbon::now($this)) . ' seconds.');
        }
        return \false;
    }
    /**
     * Cast to string (get timezone name).
     *
     * @return string
     */
    public function __toString()
    {
        return $this->getName();
    }
    /**
     * Return the type number:
     *
     * Type 1; A UTC offset, such as -0300
     * Type 2; A timezone abbreviation, such as GMT
     * Type 3: A timezone identifier, such as Europe/London
     */
    public function getType() : int
    {
        return \preg_match('/"timezone_type";i:(\\d)/', \serialize($this), $match) ? (int) $match[1] : 3;
    }
    /**
     * Create a CarbonTimeZone from mixed input.
     *
     * @param DateTimeZone|string|int|null $object
     *
     * @return false|static
     */
    public static function create($object = null)
    {
        return static::instance($object);
    }
    /**
     * Create a CarbonTimeZone from int/float hour offset.
     *
     * @param float $hourOffset number of hour of the timezone shift (can be decimal).
     *
     * @return false|static
     */
    public static function createFromHourOffset(float $hourOffset)
    {
        return static::createFromMinuteOffset($hourOffset * Carbon::MINUTES_PER_HOUR);
    }
    /**
     * Create a CarbonTimeZone from int/float minute offset.
     *
     * @param float $minuteOffset number of total minutes of the timezone shift.
     *
     * @return false|static
     */
    public static function createFromMinuteOffset(float $minuteOffset)
    {
        return static::instance(static::getOffsetNameFromMinuteOffset($minuteOffset));
    }
    /**
     * Convert a total minutes offset into a standardized timezone offset string.
     *
     * @param float $minutes number of total minutes of the timezone shift.
     *
     * @return string
     */
    public static function getOffsetNameFromMinuteOffset(float $minutes) : string
    {
        $minutes = \round($minutes);
        $unsignedMinutes = \abs($minutes);
        return ($minutes < 0 ? '-' : '+') . \str_pad((string) \floor($unsignedMinutes / 60), 2, '0', \STR_PAD_LEFT) . ':' . \str_pad((string) ($unsignedMinutes % 60), 2, '0', \STR_PAD_LEFT);
    }
}
