<?php

namespace OtomaticAi\Vendors\Illuminate\Database\PDO;

use OtomaticAi\Vendors\Doctrine\DBAL\Driver\AbstractMySQLDriver;
use OtomaticAi\Vendors\Illuminate\Database\PDO\Concerns\ConnectsToDatabase;
class MySqlDriver extends AbstractMySQLDriver
{
    use ConnectsToDatabase;
}
