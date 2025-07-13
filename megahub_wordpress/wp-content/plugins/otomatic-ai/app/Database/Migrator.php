<?php

namespace OtomaticAi\Database;

use OtomaticAi\Database\Migrations\AddLogsToPublicationTableMigration;
use OtomaticAi\Database\Migrations\CreateLinkingTableMigration;
use OtomaticAi\Database\Migrations\CreateTemplatesTableMigration;
use OtomaticAi\Database\Migrations\InitialMigration;

abstract class Migrator
{
    static private $migrations = [
        "0.0.2" => [
            InitialMigration::class,
        ],
        "0.0.3" => [
            AddLogsToPublicationTableMigration::class,
        ],
        "0.0.4" => [
            CreateLinkingTableMigration::class,
        ],
        "0.0.5" => [
            CreateTemplatesTableMigration::class,
        ]
    ];

    static public function run()
    {
        $dbVersion = get_option(OTOMATIC_AI_DB_VERSION_OPTION, "0.0.0");
        $lastVersion = $dbVersion;
        foreach (self::$migrations as $version => $migrations) {
            foreach ($migrations as $migration) {
                $lastVersion = $version;
                $inst = new $migration($dbVersion, $version);
                $inst->run();
            }
        }

        if (version_compare($dbVersion, $lastVersion, "<")) {
            update_option(OTOMATIC_AI_DB_VERSION_OPTION, OTOMATIC_AI_DB_VERSION);
        }
    }
}
