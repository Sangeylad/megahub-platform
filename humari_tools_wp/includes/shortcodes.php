<?php
// Sécurité
if (!defined('ABSPATH')) {
    exit;
}

// Enregistrer les shortcodes
add_action('init', 'humari_tools_register_shortcodes');

function humari_tools_register_shortcodes() {
    add_shortcode('humari_tool', 'humari_tool_shortcode');
}

function humari_tool_shortcode($atts) {
    // Attributs par défaut
    $atts = shortcode_atts(array(
        'tool' => 'converter',
        'category' => 'document',
    ), $atts);
    
    // ✅ AJOUT : Support du calculateur ROAS
    $allowed_tools = array(
        'document' => array('converter'),
        'web' => array('shortener'),
        'real-estate' => array('simulator'),
        'file' => array('optimizer'),
        'ecommerce' => array('roas-calculator')  // ← NOUVEAU
    );
    
    if (!isset($allowed_tools[$atts['category']]) || 
        !in_array($atts['tool'], $allowed_tools[$atts['category']])) {
        return '<div class="error">Outil non reconnu</div>';
    }
    
    // ✅ AJOUT : Script AJAX pour WordPress
    $ajax_script = '<script>window.ajaxurl = "' . admin_url('admin-ajax.php') . '";</script>';
    
    // Appel vers Django pour récupérer le HTML
    $html_content = humari_tools_get_tool_html($atts['category'], $atts['tool']);
    
    if (is_wp_error($html_content)) {
        return '<div class="error">Erreur lors du chargement de l\'outil</div>';
    }
    
    // Traitement des formulaires (si POST)
    $processed_html = humari_tools_handle_form_submission($html_content, $atts);
    
    return $ajax_script . $processed_html;
}