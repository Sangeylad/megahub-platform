<?php

namespace OtomaticAi\Database\Migrations;

class InitialMigration extends Migration
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

        // personas table
        $personas_table_name = $wpdb->prefix . "otomatic_ai_personas";

        $sql = "CREATE TABLE IF NOT EXISTS `{$personas_table_name}` (
        	`id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
            `user_id` bigint(20) unsigned NOT NULL,
            `language` varchar(255) NOT NULL,
        	`job` varchar(255) DEFAULT NULL,
        	`writing_style` varchar(255) DEFAULT NULL,
        	`age` int(11) unsigned DEFAULT NULL,
        	`created_at` datetime DEFAULT NOW() NOT NULL,
        	`updated_at` datetime DEFAULT NOW() NOT NULL,
        	PRIMARY KEY  (`id`)
          ) ENGINE=InnoDB {$charset_collate}";

        $out = \dbDelta($sql);

        // projects table
        $projects_table_name = $wpdb->prefix . "otomatic_ai_projects";

        $sql = "CREATE TABLE IF NOT EXISTS `{$projects_table_name}` (
        	`id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
        	`name` varchar(255) NOT NULL,
        	`language` varchar(255) NOT NULL,
        	`type` varchar(255) NOT NULL,
        	`enabled` tinyint(1) NOT NULL DEFAULT 0,
        	`modules` longtext DEFAULT NULL ,
        	`planning` longtext DEFAULT NULL ,
            `persona_id` bigint(20) unsigned DEFAULT NULL,
            `metrics` longtext DEFAULT NULL ,
        	`created_at` datetime DEFAULT NOW() NOT NULL,
        	`updated_at` datetime DEFAULT NOW() NOT NULL,
        	PRIMARY KEY  (`id`),
            KEY `{$wpdb->prefix}projects_persona_id_foreign` (`persona_id`),
            CONSTRAINT `{$wpdb->prefix}projects_persona_id_foreign` FOREIGN KEY (`persona_id`) REFERENCES `{$personas_table_name}` (`id`) ON DELETE SET NULL
          ) ENGINE=InnoDB {$charset_collate};";

        $out = \dbDelta($sql);

        // publications table
        $publications_table_name = $wpdb->prefix . "otomatic_ai_publications";

        $sql = "CREATE TABLE IF NOT EXISTS `{$publications_table_name}` (
        	`id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
            `project_id` bigint(20) unsigned NOT NULL,
        	`title` text NOT NULL,
            `parent_id` bigint(20) unsigned DEFAULT NULL,
            `post_id` bigint(20) unsigned DEFAULT NULL,
        	`status` varchar(255) DEFAULT 'idle',
            `meta` longtext DEFAULT NULL,
            `published_at` datetime DEFAULT NOW() NOT NULL,
        	`created_at` datetime DEFAULT NOW() NOT NULL,
        	`updated_at` datetime DEFAULT NOW() NOT NULL,
        	PRIMARY KEY  (`id`),
            KEY `{$wpdb->prefix}publications_project_id_foreign` (`project_id`),
            KEY `{$wpdb->prefix}publications_parent_id_foreign` (`parent_id`),
            CONSTRAINT `{$wpdb->prefix}publications_project_id_foreign` FOREIGN KEY (`project_id`) REFERENCES `{$projects_table_name}` (`id`) ON DELETE CASCADE,
            CONSTRAINT `{$wpdb->prefix}publications_parent_id_foreign` FOREIGN KEY (`parent_id`) REFERENCES `{$publications_table_name}` (`id`) ON DELETE SET NULL
          ) ENGINE=InnoDB {$charset_collate};";

        $out = \dbDelta($sql);

        // presets table
        $presets_table_name = $wpdb->prefix . "otomatic_ai_presets";

        $sql = "CREATE TABLE IF NOT EXISTS `{$presets_table_name}` (
        	`id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
        	`name` varchar(255) NOT NULL,
        	`model` varchar(255) NOT NULL,
        	`messages` longtext DEFAULT NULL,
            `temperature` double(3,2) unsigned NOT NULL DEFAULT '1.00',
            `top_p` double(3,2) unsigned NOT NULL DEFAULT '1.00',
            `presence_penalty` double(3,2) NOT NULL DEFAULT '0.00',
            `frequency_penalty` double(3,2) NOT NULL DEFAULT '0.00',
        	`created_at` datetime DEFAULT NOW() NOT NULL,
        	`updated_at` datetime DEFAULT NOW() NOT NULL,
        	PRIMARY KEY  (`id`)
          ) ENGINE=InnoDB {$charset_collate};";

        $out = \dbDelta($sql);

        // usages table
        $usages_table_name = $wpdb->prefix . "otomatic_ai_usages";

        $sql = "CREATE TABLE IF NOT EXISTS `{$usages_table_name}` (
        	`id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
            `provider` varchar(20) NOT NULL,
            `payload` longtext DEFAULT NULL,
        	`created_at` datetime DEFAULT NOW() NOT NULL,
        	`updated_at` datetime DEFAULT NOW() NOT NULL,
        	PRIMARY KEY  (`id`)
          ) ENGINE=InnoDB {$charset_collate};";

        $out = \dbDelta($sql);
    }
}
