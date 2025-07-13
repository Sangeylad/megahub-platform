<?php
/*
Plugin Name: Mega Hub
Plugin URI: Ton URL de plugin
Description: Un plugin WordPress offrant une suite de fonctionnalités, y compris le Text to Speech, personnalisables via Mega Hub.
Version: 1.0
Author: Ton Nom
Author URI: Ton URL
License: GPL2
*/

// Empêche l'accès direct au fichier
defined('ABSPATH') or die('Accès interdit.');


add_action('admin_menu', function() {
    require_once plugin_dir_path(__FILE__) . 'includes/settings-page.php';
    require_once plugin_dir_path(__FILE__) . 'includes/text-to-speech/tts-page.php';
    require_once plugin_dir_path(__FILE__) . 'includes/auto-blogger/ab-page.php';
    require_once plugin_dir_path(__FILE__) . 'includes/helpers.php';
    require_once plugin_dir_path(__FILE__) . 'includes/seo-tools/seo-page.php';
    require_once plugin_dir_path(__FILE__) . 'includes/content-tools/content-tools-page.php';
    require_once plugin_dir_path(__FILE__) . 'includes/image-generation/dalle-page.php';
});

require_once plugin_dir_path(__FILE__) . '/videogenerator.php';
require_once plugin_dir_path(__FILE__) . 'includes/woocommerce/woocommerce-functions.php';
require_once plugin_dir_path(__FILE__) . 'includes/text-to-speech/tts-functions.php';
require_once plugin_dir_path(__FILE__) . 'includes/auto-blogger/ab-functions.php';
require_once plugin_dir_path(__FILE__) . 'includes/seo-tools/ai-functions.php';
require_once plugin_dir_path(__FILE__) . 'includes/seo-tools/struct_datas_functions.php';
require_once plugin_dir_path(__FILE__) . 'includes/image-generation/dalle-functions.php';



require_once plugin_dir_path(__FILE__) . 'includes/content-tools/content-tools-public.php';
require_once plugin_dir_path(__FILE__) . 'includes/text-to-speech/tts-public.php';


function mega_hub_load_textdomain() {
    load_plugin_textdomain('mega-hub', false, basename(dirname(__FILE__)) . '/languages/');
}
add_action('plugins_loaded', 'mega_hub_load_textdomain');


function mega_hub_add_admin_menu() {
    // Page principale de paramètres
    add_menu_page(
        'Mega Hub Settings',
        'Mega Hub',
        'manage_options',
        'mega-hub-settings',
        'mega_hub_settings_page',
        'dashicons-admin-generic',
        3
    );

    // Sous-menu "Settings" pointant vers la même page mais avec un paramètre différent
    add_submenu_page(
        'mega-hub-settings',
        'Mega Hub Settings',
        'Settings',
        'manage_options',
        'mega-hub-settings-general', // Un slug unique
        'mega_hub_settings_page' // La même fonction de rappel
    );

    // Supprime le sous-menu par défaut
    remove_submenu_page('mega-hub-settings', 'mega-hub-settings');

    // Récupère les options du plugin
    $tts_options = get_option('mega_hub_options_tts', []);
    $auto_blogger_options = get_option('mega_hub_options_auto_blogger', []);
    $dalle_options = get_option('mega_hub_options_dalle', []);
    $content_tools_options = get_option('mega_hub_options_content_tools', []);
    


    // Conditionnellement ajoute la sous-page Text to Speech si activée
    if (isset($tts_options['mega_hub_tts_enable']) && $tts_options['mega_hub_tts_enable'] === 'on') {
        add_submenu_page(
            'mega-hub-settings',
            'TTS Audio Generator',
            'TTS Audio Generator',
            'manage_options',
            'mega-hub-text-to-speech',
            'mega_hub_text_to_speech_page'
        );
    }

    if (isset($dalle_options['mega_hub_dalle_enable']) && $dalle_options['mega_hub_dalle_enable'] === 'on') {
    add_submenu_page(
        'mega-hub-settings',
        __('Dalle Image Generator', 'mega-hub'), // Le titre de la page
        __('Dalle Image Generator', 'mega-hub'), // Le titre du menu
        'manage_options', // La capacité requise pour voir cette page
        'mega-hub-dalle-image-generator', // Le slug du menu
        'mega_hub_dalle_image_generator_page' // La fonction qui va afficher le contenu de la page
    );
    }
    

    // Conditionnellement ajoute la sous-page Auto Blogger si activée
    if (isset($auto_blogger_options['mega_hub_auto_blogger_enable']) && $auto_blogger_options['mega_hub_auto_blogger_enable'] === 'on') {
        add_submenu_page(
            'mega-hub-settings',
            'Auto Blogger Settings',
            'Auto Blogger',
            'manage_options',
            'mega-hub-auto-blogger',
            'mega_hub_auto_blogger_page'
        );
    }

    // Conditionnellement ajoute la sous-page Auto Indexeur si activée
    add_submenu_page(
        'mega-hub-settings',
        __('SEO Tools', 'mega-hub'), // Le titre de la page
        __('SEO Tools', 'mega-hub'), // Le titre du menu
        'manage_options', // La capacité requise pour voir cette page
        'mega-hub-seo-tools', // Le slug du menu
        'mega_hub_seo_tools_page' // La fonction qui va afficher le contenu de la page
    );

    if (isset($content_tools_options['mega_hub_content_tools_enable']) && $content_tools_options['mega_hub_content_tools_enable'] === 'on') {
    add_submenu_page(
        'mega-hub-settings',
        __('Content Tools', 'mega-hub'), // Le titre de la page
        __('Content Tools', 'mega-hub'), // Le titre du menu
        'manage_options', // La capacité requise pour voir cette page
        'mega-hub-content-tools', // Le slug du menu
        'mega_hub_content_tools_page' // La fonction qui va afficher le contenu de la page
    );
    }
    
}
add_action('admin_menu', 'mega_hub_add_admin_menu');


function mega_hub_settings_init() {
    // Enregistrement des options pour les paramètres globaux
    register_setting('mega_hub_global', 'mega_hub_options_global');

    add_settings_section(
        'mega_hub_section_global',
        __('Global Settings', 'mega-hub'),
        'mega_hub_section_global_cb',
        'mega_hub_global'
    );

    add_settings_field(
        'mega_hub_brand',
        __('Brand Name', 'mega-hub'),
        'mega_hub_brand_render',
        'mega_hub_global',
        'mega_hub_section_global',
        ['label_for' => 'mega_hub_brand']
    );
    
    add_settings_field(
        'mega_hub_api_key',
        __('MegaHub API Key', 'mega-hub'),
        'mega_hub_api_key_render',
        'mega_hub_global',
        'mega_hub_section_global',
        ['label_for' => 'mega_hub_api_key']
    );

    add_settings_field(
        'mega_hub_business_description',
        __('Business description', 'mega-hub'),
        'mega_hub_business_description_render',
        'mega_hub_global',
        'mega_hub_section_global',
        ['label_for' => 'mega_hub_business_description']
    );


    add_settings_field(
        'mega_hub_email_notifications',
        __('Enable Email Notifications', 'mega-hub'),
        'mega_hub_email_notifications_render',
        'mega_hub_global', // Assure-toi que cette section existe déjà dans ta page de réglages
        'mega_hub_section_global'
    );

    add_settings_field(
        'mega_hub_email',
        __('Notification Email', 'mega-hub'),
        'mega_hub_email_render',
        'mega_hub_global', // Assure-toi que cette section existe déjà dans ta page de réglages
        'mega_hub_section_global'
    );

    add_settings_field(
        'mega_hub_currency', // ID du champ
        __('Currency', 'mega-hub'), // Titre du champ
        'mega_hub_currency_render', // Fonction de rendu
        'mega_hub_global', // Page où ajouter le champ
        'mega_hub_section_global', // Section à laquelle le champ appartient
        ['label_for' => 'mega_hub_currency'] // Arguments supplémentaires
    );    

    add_settings_field(
        'mega_hub_language',
        __('Language', 'mega-hub'),
        'mega_hub_language_render',
        'mega_hub_global',
        'mega_hub_section_global',
        ['label_for' => 'mega_hub_language']
    );

    /* ---------------------------------- TTS OPTIONS ------------------------------------------*/


    register_setting('mega_hub_tts', 'mega_hub_options_tts');

    add_settings_section(
        'mega_hub_section_tts',
        __('TTS Settings', 'mega-hub'),
        'mega_hub_section_tts_cb',
        'mega_hub_tts'
    );

    add_settings_field(
        'mega_hub_tts_enable',
        __('Enable TTS Features', 'mega-hub'),
        'mega_hub_tts_enable_render',
        'mega_hub_tts',
        'mega_hub_section_tts',
        ['label_for' => 'mega_hub_tts_enable']
    );

    add_settings_field(
        'mega_hub_tts_block_title',
        __('Audio Block Title', 'mega-hub'),
        'mega_hub_tts_block_title_render',
        'mega_hub_tts',
        'mega_hub_section_tts',
        ['label_for' => 'mega_hub_tts_block_title']
    );

    add_settings_field(
        'mega_hub_tts_voice',
        __('TTS Voice', 'mega-hub'),
        'mega_hub_tts_voice_render',
        'mega_hub_tts',
        'mega_hub_section_tts',
        ['label_for' => 'mega_hub_tts_voice']
    );

    add_settings_field(
        'mega_hub_tts_primary_color',
        __('Primary Color', 'mega-hub'),
        'mega_hub_tts_primary_color_render',
        'mega_hub_tts',
        'mega_hub_section_tts',
        ['label_for' => 'mega_hub_tts_primary_color']
    );

    add_settings_field(
        'mega_hub_tts_secondary_color',
        __('Secondary Color', 'mega-hub'),
        'mega_hub_tts_secondary_color_render',
        'mega_hub_tts',
        'mega_hub_section_tts',
        ['label_for' => 'mega_hub_tts_secondary_color']
    );


/* ---------------------------------- IMAGE GENERATOR ------------------------------------------*/



    register_setting('mega_hub_dalle', 'mega_hub_options_dalle');

    // Ajout d'une section pour les paramètres Dalle
    add_settings_section(
        'mega_hub_section_dalle',
        __('Dalle Settings', 'mega-hub'),
        'mega_hub_section_dalle_cb',
        'mega_hub_dalle'
    );

    // Champ pour activer/désactiver Dalle Image Generator
    add_settings_field(
        'mega_hub_dalle_enable',
        __('Enable Dalle Image Generator', 'mega-hub'),
        'mega_hub_dalle_enable_render',
        'mega_hub_dalle',
        'mega_hub_section_dalle',
        ['label_for' => 'mega_hub_dalle_enable']
    );

    // Champ pour choisir le modèle Dalle
    add_settings_field(
        'mega_hub_dalle_model',
        __('Dalle Model', 'mega-hub'),
        'mega_hub_dalle_model_render',
        'mega_hub_dalle',
        'mega_hub_section_dalle',
        ['label_for' => 'mega_hub_dalle_model']
    );

/* ---------------------------------- SEO TOOLS ------------------------------------------*/


    register_setting('mega_hub_seo', 'mega_hub_options_seo');

    add_settings_section(
        'mega_hub_section_seo',
        __('SEO Settings', 'mega-hub'),
        'mega_hub_section_seo_cb',
        'mega_hub_seo'
    );

    add_settings_field(
        'mega_hub_indexer_enable',
        __('Enable Indexer', 'mega-hub'),
        'mega_hub_indexer_enable_render',
        'mega_hub_seo',
        'mega_hub_section_seo',
        ['label_for' => 'mega_hub_indexer_enable']
    );
    
    add_settings_field(
        'mega_hub_structured_data_enable',
        __('Enable Structured Data', 'mega-hub'),
        'mega_hub_structured_data_enable_render',
        'mega_hub_seo',
        'mega_hub_section_seo',
        ['label_for' => 'mega_hub_structured_data_enable']
    );
    
    /* ---------------------------------- AUTOBLOG ------------------------------------------*/


    register_setting('mega_hub_auto_blogger', 'mega_hub_options_auto_blogger');

    add_settings_section(
        'mega_hub_section_auto_blogger',
        __('Auto Blogger Settings', 'mega-hub'),
        'mega_hub_section_auto_blogger_cb',
        'mega_hub_auto_blogger'
    );


    add_settings_field(
        'mega_hub_auto_blogger_enable',
        __('Enable Auto Blogger', 'mega-hub'),
        'mega_hub_auto_blogger_enable_render',
        'mega_hub_auto_blogger',
        'mega_hub_section_auto_blogger',
        ['label_for' => 'mega_hub_auto_blogger_enable']
    );

    add_settings_field(
        'mega_hub_auto_blogger_gpt_model',
        __('Modèle préféré', 'mega-hub'),
        'mega_hub_auto_blogger_gpt_model_render',
        'mega_hub_auto_blogger',
        'mega_hub_section_auto_blogger',
        ['label_for' => 'mega_hub_auto_blogger_gpt_model']
    );


    add_settings_field(
        'mega_hub_autoblog_internal_urls',
        __('Auto Blog Internal URLs', 'mega-hub'),
        'mega_hub_autoblog_internal_urls_render',
        'mega_hub_auto_blogger',
        'mega_hub_section_auto_blogger',
        ['label_for' => 'mega_hub_autoblog_internal_urls']
    );

    add_settings_field(
        'mega_hub_auto_blogger_affiliate_urls',
        __('Affiliate URLs', 'mega-hub'),
        'mega_hub_auto_blogger_affiliate_urls_render',
        'mega_hub_auto_blogger',
        'mega_hub_section_auto_blogger',
        ['label_for' => 'mega_hub_auto_blogger_affiliate_urls']
    );

    /* ---------------------------------- CONTENT TOOL ------------------------------------------*/


    register_setting('mega_hub_content_tools', 'mega_hub_options_content_tools');

    add_settings_section(
        'mega_hub_section_content_tools',
        __('Content Tools Settings', 'mega-hub'),
        'mega_hub_section_content_tools_cb',
        'mega_hub_content_tools'
    );

    add_settings_field(
        'mega_hub_content_tools_enable',
        __('Enable Content Tools', 'mega-hub'),
        'mega_hub_content_tools_enable_render',
        'mega_hub_content_tools',
        'mega_hub_section_content_tools'
    );

    /* ---------------------------------- WOOCOMMERCE ------------------------------------------*/


    register_setting('mega_hub_woocommerce', 'mega_hub_options_woocommerce');

    add_settings_section(
        'mega_hub_section_woocommerce',
        __('WooCommerce Integration', 'mega-hub'),
        'mega_hub_section_woocommerce_cb',
        'mega_hub_woocommerce'
    );

    add_settings_field(
        'mega_hub_woocommerce_enable',
        __('Enable WooCommerce Integration', 'mega-hub'),
        'mega_hub_woocommerce_enable_render',
        'mega_hub_woocommerce',
        'mega_hub_section_woocommerce',
        ['label_for' => 'mega_hub_woocommerce_enable']
    );
}

add_action('admin_init', 'mega_hub_settings_init');



    /* ---------------------------------- CHARGEMENT DES ASSETS ------------------------------------------*/



function mega_hub_enqueue_admin_resources() {
    // Enqueue le style principal pour l'administration
    wp_enqueue_style('mega-hub-admin-style', plugin_dir_url(__FILE__) . 'assets/css/admin-style.css');

    // Enqueue le script principal pour l'administration
// Enqueue le script principal pour l'administration avec wp-color-picker comme dépendance
    wp_enqueue_script('mega-hub-admin-script', plugin_dir_url(__FILE__) . 'assets/js/admin-scripts.js', array('wp-color-picker'), false, true);

    // Enqueue les styles spécifiques aux fonctionnalités
    wp_enqueue_style('mega-hub-auto-blogger-style', plugin_dir_url(__FILE__) . 'assets/css/features/auto-blogger.css');
    wp_enqueue_style('mega-hub-text-to-speech-style', plugin_dir_url(__FILE__) . 'assets/css/features/text-to-speech.css');
    wp_enqueue_style('mega-hub-auto-indexer-style', plugin_dir_url(__FILE__) . 'assets/css/features/auto-indexer.css');

    // Enqueue les scripts spécifiques aux fonctionnalités
    wp_enqueue_script('mega-hub-auto-blogger-script', plugin_dir_url(__FILE__) . 'assets/js/features/auto-blogger.js');
    wp_enqueue_script('mega-hub-text-to-speech-script', plugin_dir_url(__FILE__) . 'assets/js/features/text-to-speech.js');
    wp_enqueue_script('mega-hub-auto-indexer-script', plugin_dir_url(__FILE__) . 'assets/js/features/auto-indexer.js');
}

add_action('admin_enqueue_scripts', 'mega_hub_enqueue_admin_resources');



// Fonction à exécuter lors de l'activation du plugin
function mega_hub_activate() {
    // Définir les valeurs par défaut pour les options globales
    $default_global_options = array(
        'mega_hub_brand' => '', // Marque par défaut
        'mega_hub_api_key' => '', // Clé API par défaut
        'mega_hub_business_description' => '', // Description par défaut de l'entreprise
        'mega_hub_email_notifications' => 'on', // Notifications par e-mail activées par défaut
        'mega_hub_email' => get_option('admin_email'), // E-mail par défaut pour les notifications
        'mega_hub_language' => 'en', // Langue par défaut
    );
    add_option('mega_hub_options_global', $default_global_options);

    // Définir les valeurs par défaut pour les options TTS
    $default_tts_options = array(
        'mega_hub_tts_enable' => 'on', // TTS activé par défaut
        'mega_hub_tts_voice' => '', // Voix TTS par défaut
        'mega_hub_tts_primary_color' => '', // Couleur primaire par défaut pour TTS
        'mega_hub_tts_secondary_color' => '', // Couleur secondaire par défaut pour TTS
    );
    add_option('mega_hub_options_tts', $default_tts_options);

    // Définir les valeurs par défaut pour les options de l'Indexeur
    $default_seo_options = array(
        'mega_hub_indexer_enable' => 'on',
        'mega_hub_structured_data_enable' => 'on', 
    );
    add_option('mega_hub_options_seo', $default_seo_options);

    // Définir les valeurs par défaut pour les options Auto Blogger
    $default_auto_blogger_options = array(
        'mega_hub_auto_blogger_enable' => 'on', // Auto Blogger activé par défaut
        'mega_hub_autoblog_internal_urls' => '', // URL internes par défaut pour Auto Blogger
    );
    add_option('mega_hub_options_auto_blogger', $default_auto_blogger_options);
}

// Associer la fonction d'activation avec l'activation du plugin
register_activation_hook(__FILE__, 'mega_hub_activate');