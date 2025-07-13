<?php

namespace OtomaticAi\Database\Migrations;

class CreateLinkingTableMigration extends Migration
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

        // linking table
        $linkings_table_name = $wpdb->prefix . "otomatic_ai_linkings";

        $sql = "CREATE TABLE IF NOT EXISTS `{$linkings_table_name}` (
        	`id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
            `mode` varchar(255) NOT NULL,
            `post_id` bigint(20) unsigned DEFAULT NULL,
            `custom_url` text DEFAULT NULL,
            `keywords` longtext DEFAULT NULL,
            `max_links` integer(11) unsigned NOT NULL DEFAULT 0,
            `post_types` longtext DEFAULT NULL,
            `is_blank` tinyint(1) NOT NULL DEFAULT 0,
            `is_follow` tinyint(1) NOT NULL DEFAULT 1,
            `is_obfuscated` tinyint(1) NOT NULL DEFAULT 0,
        	`created_at` datetime DEFAULT NOW() NOT NULL,
        	`updated_at` datetime DEFAULT NOW() NOT NULL,
        	PRIMARY KEY  (`id`)
          ) ENGINE=InnoDB {$charset_collate}";

        $out = \dbDelta($sql);
    }
}
