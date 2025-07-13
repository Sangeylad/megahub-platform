<?php
/**
 * Plugin Name: Humari Tools
 * Description: Outils publics intégrés depuis MegaHub
 * Version: 1.0.0
 * Author: Humari
 */

// Sécurité - empêche l'accès direct
if (!defined('ABSPATH')) {
    exit;
}


// Constantes du plugin
define('HUMARI_TOOLS_PLUGIN_DIR', plugin_dir_path(__FILE__));
define('HUMARI_TOOLS_PLUGIN_URL', plugin_dir_url(__FILE__));
define('HUMARI_TOOLS_API_BASE', 'https://backoffice.humari.fr/public-tools/');

// Charger les fichiers du plugin
require_once HUMARI_TOOLS_PLUGIN_DIR . 'includes/api-client.php';
require_once HUMARI_TOOLS_PLUGIN_DIR . 'includes/shortcodes.php';


// Hook d'activation
register_activation_hook(__FILE__, 'humari_tools_activate');
function humari_tools_activate() {
    // Rien pour l'instant
}

// Hook de désactivation
register_deactivation_hook(__FILE__, 'humari_tools_deactivate');
function humari_tools_deactivate() {
    // Rien pour l'instant
}

// Charger les styles CSS
add_action('wp_enqueue_scripts', 'humari_tools_enqueue_styles');
function humari_tools_enqueue_styles() {
    wp_enqueue_style(
        'humari-tools-css',
        HUMARI_TOOLS_PLUGIN_URL . 'assets/tools.css',
        array(),
        '1.0.0'
    );
}

// Ajouter ces lignes
require_once HUMARI_TOOLS_PLUGIN_DIR . 'includes/glossary-client.php';
require_once HUMARI_TOOLS_PLUGIN_DIR . 'includes/glossary-shortcodes.php';
require_once HUMARI_TOOLS_PLUGIN_DIR . 'includes/glossary-recall.php';        // ⭐ NOUVEAU
require_once HUMARI_TOOLS_PLUGIN_DIR . 'includes/glossary-rewrite.php';

// CSS supplémentaire
function humari_tools_enqueue_glossary_styles() {
    wp_enqueue_style('humari-glossary-css', HUMARI_TOOLS_PLUGIN_URL . 'assets/glossary.css', array(), '1.0.0');
    wp_enqueue_style('humari-glossary-recall-css', HUMARI_TOOLS_PLUGIN_URL . 'assets/glossary-recall.css', array(), '1.0.0');
}
add_action('wp_enqueue_scripts', 'humari_tools_enqueue_glossary_styles');