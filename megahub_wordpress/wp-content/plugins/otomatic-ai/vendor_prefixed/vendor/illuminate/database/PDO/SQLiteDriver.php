<?php

namespace OtomaticAi\Vendors\Illuminate\Database\PDO;

use OtomaticAi\Vendors\Doctrine\DBAL\Driver\AbstractSQLiteDriver;
use OtomaticAi\Vendors\Illuminate\Database\PDO\Concerns\ConnectsToDatabase;
class SQLiteDriver extends AbstractSQLiteDriver
{
    use ConnectsToDatabase;
}
