<?php

namespace OtomaticAi\Database\Migrations;

class AddLogsToPublicationTableMigration extends Migration
{
    /**
     * Run a new migration
     *
     * @return void
     */
    public function run()
    {
        global $wpdb;

        if (!$this->canRun()) {
            return;
        }

        require_once(ABSPATH . 'wp-admin/includes/upgrade.php');

        $publications_table_name = $wpdb->prefix . "otomatic_ai_publications";

        $sql = "ALTER TABLE `{$publications_table_name}` ADD COLUMN `logs` longtext DEFAULT NULL AFTER `meta`;";

        $wpdb->query($sql);
    }
}
