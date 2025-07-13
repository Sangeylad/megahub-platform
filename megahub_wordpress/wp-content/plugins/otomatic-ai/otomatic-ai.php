<?php

/**
 * @wordpress-plugin
 * Plugin Name:       otomatic.ai
 * Plugin URI:        https://otomatic.ai
 * Description:       Generate AI content for your WordPress sites in minutes.
 * Version:           3.0.0
 * Update URI:        https://otomatic.ai
 * Author:            otomatic.ai
 * Author URI:        https://otomatic.ai
 * License:           GPL v3 or later
 * License URI:       https://www.gnu.org/licenses/gpl-3.0.txt
 * Text Domain:       otomatic-ai
 * Domain Path:       /languages
 * Requires at least: 6.0
 * Requires PHP:      7.4
 */

use OtomaticAi\Plugin;
use YahnisElsts\PluginUpdateChecker\v5\PucFactory;

// If this file is called directly, abort.
if (!defined('WPINC')) {
    die;
}

define('OTOMATIC_AI_VERSION', '3.0.0');
define('OTOMATIC_AI_DB_VERSION_OPTION', "otomatic_ai_db_version");
define('OTOMATIC_AI_DB_VERSION', "0.0.5");
define('OTOMATIC_AI_NONCE', 'otomatic-ai-nonce');
define('OTOMATIC_AI_NAME', 'otomatic-ai');
define('OTOMATIC_AI_ROOT_PATH', plugin_dir_path(__FILE__));
define('OTOMATIC_AI_ROOT_URL', plugin_dir_url(__FILE__));
define('OTOMATIC_AI_API_ENDPOINT', "https://api.otomatic.ai/api/v1");
define('OTOMATIC_AI_TEST', false);

// load updater
try {
    if (is_readable(OTOMATIC_AI_ROOT_PATH . '/libraries/plugin-update-checker/plugin-update-checker.php')) {
        require OTOMATIC_AI_ROOT_PATH . '/libraries/plugin-update-checker/plugin-update-checker.php';
        PucFactory::buildUpdateChecker(
            OTOMATIC_AI_API_ENDPOINT . '/plugin',
            __FILE__,
            OTOMATIC_AI_NAME
        );
    }
} catch (Exception $e) {
}

// load composer vendors.
if (is_readable(OTOMATIC_AI_ROOT_PATH . '/vendor_prefixed/vendor/autoload.php')) {
    require_once OTOMATIC_AI_ROOT_PATH . '/vendor_prefixed/vendor/autoload.php';
}
if (is_readable(OTOMATIC_AI_ROOT_PATH . '/vendor_prefixed/vendor/illuminate/collections/helpers.php')) {
    require_once OTOMATIC_AI_ROOT_PATH . '/vendor_prefixed/vendor/illuminate/collections/helpers.php';
}
if (is_readable(OTOMATIC_AI_ROOT_PATH . '/vendor_prefixed/vendor/illuminate/support/helpers.php')) {
    require_once OTOMATIC_AI_ROOT_PATH . '/vendor_prefixed/vendor/illuminate/support/helpers.php';
}

// load action scheduler
try {
    if (is_readable(OTOMATIC_AI_ROOT_PATH . '/libraries/action-scheduler/action-scheduler.php')) {
        require_once OTOMATIC_AI_ROOT_PATH . '/libraries/action-scheduler/action-scheduler.php';
    }
} catch (\Exception $e) {
}

spl_autoload_register(function ($class) {
    $namespaces = explode("\\", $class);
    if (count($namespaces) > 0 && $namespaces[0] === "OtomaticAi") {
        if (count($namespaces) > 1 && $namespaces[1] === "Vendors") {
            return;
        }
        $namespaces[0] = "app";

        require_once plugin_dir_path(__FILE__) . implode("/", $namespaces) . '.php';
    }
});

add_action('plugins_loaded', function () {
    $plugin = new Plugin;
    $plugin->activate();
    $plugin->run();
});
