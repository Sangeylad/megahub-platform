<?php

namespace OtomaticAi\Database\Migrations;

class CreateTemplatesTableMigration extends Migration
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

        $charset_collate = $wpdb->get_charset_collate();

        // templates table
        $templates_table_name = $wpdb->prefix . "otomatic_ai_templates";

        $sql = "CREATE TABLE IF NOT EXISTS `{$templates_table_name}` (
        	`id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
            `name` varchar(255) NOT NULL,
            `plugin_version` varchar(255) NOT NULL,
            `payload` longtext DEFAULT NULL,
        	`created_at` datetime DEFAULT NOW() NOT NULL,
        	`updated_at` datetime DEFAULT NOW() NOT NULL,
        	PRIMARY KEY  (`id`)
          ) ENGINE=InnoDB {$charset_collate}";

        $out = \dbDelta($sql);
    }
}
