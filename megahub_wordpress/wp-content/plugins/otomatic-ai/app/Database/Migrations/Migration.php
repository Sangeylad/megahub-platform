<?php

namespace OtomaticAi\Database\Migrations;

use OtomaticAi\Database\Contracts\ShouldRun;

abstract class Migration implements ShouldRun
{
    protected string $dbVersion;
    protected string $version;

    /**
     * Create a new Migration
     *
     * @param string $dbVersion
     * @param string $version
     */
    public function __construct(string $dbVersion, string $version)
    {
        $this->dbVersion = $dbVersion;
        $this->version = $version;
    }

    protected function canRun()
    {
        return version_compare($this->dbVersion, $this->version, "<");
    }
}
