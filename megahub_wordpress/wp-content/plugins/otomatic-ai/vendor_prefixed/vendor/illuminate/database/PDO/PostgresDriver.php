<?php

namespace OtomaticAi\Vendors\Illuminate\Database\PDO;

use OtomaticAi\Vendors\Doctrine\DBAL\Driver\AbstractPostgreSQLDriver;
use OtomaticAi\Vendors\Illuminate\Database\PDO\Concerns\ConnectsToDatabase;
class PostgresDriver extends AbstractPostgreSQLDriver
{
    use ConnectsToDatabase;
}
