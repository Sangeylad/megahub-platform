<?php

namespace OtomaticAi\Vendors\Carbon\Doctrine;

use OtomaticAi\Vendors\Carbon\Carbon;
use OtomaticAi\Vendors\Doctrine\DBAL\Types\VarDateTimeType;
class DateTimeType extends VarDateTimeType implements CarbonDoctrineType
{
    /** @use CarbonTypeConverter<Carbon> */
    use CarbonTypeConverter;
}
