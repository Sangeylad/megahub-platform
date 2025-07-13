<?php


function init_tts_feature_public() {
    $options = get_option('mega_hub_options_tts');

    // Vérifie si l'option 'mega_hub_tts_enable' est définie et différente de 'on'
    if (!isset($options['mega_hub_tts_enable']) || $options['mega_hub_tts_enable'] !== 'on') {
        return; // Sort de la fonction si TTS n'est pas activé
    }

    function mega_hub_shortcode_tts_player() {
        global $post; // Récupère l'objet post global
        // Récupère l'URL du fichier audio TTS stocké dans une méta du post
        $audioUrl = get_post_meta($post->ID, '_tts_audio_url', true);
    
        if (!empty($audioUrl)) {
            // Génère la balise audio HTML5 avec le fichier audio TTS
            return '
            <div class="mega-hub-tts-player">
                <audio controls class="custom-audio-player">
                    <source src="' . esc_url($audioUrl) . '" type="audio/mpeg">
                    Votre navigateur ne prend pas en charge l\'élément audio.
                </audio>
            </div>';
        }
    
        // Si l'URL est vide, ne retourne rien
        return '';
    }
    add_shortcode('mega_hub_tts_player', 'mega_hub_shortcode_tts_player');
    
    function mega_hub_shortcode_tts_block() {
        global $post;
        // Récupère les options du plugin pour les couleurs
        $ttsOptions = get_option('mega_hub_options_tts');
        $primaryColor = !empty($ttsOptions['mega_hub_tts_primary_color']) ? $ttsOptions['mega_hub_tts_primary_color'] : '#000000'; // Noir par défaut
        $secondaryColor = !empty($ttsOptions['mega_hub_tts_secondary_color']) ? $ttsOptions['mega_hub_tts_secondary_color'] : '#CCCCCC'; // Gris par défaut
    
        // Récupère le titre TTS et l'URL du fichier audio TTS stockés dans des méta du post
        $ttsTitle = get_post_meta($post->ID, '_tts_title', true);
        $audioUrl = get_post_meta($post->ID, '_tts_audio_url', true);
    
        if (!empty($audioUrl)) {
            // Titre par défaut si aucun titre personnalisé n'est fourni
            $title = !empty($ttsTitle) ? $ttsTitle : get_the_title($post->ID);
    
            // Construit le bloc complet avec titre et lecteur audio, incluant le CSS
            return '
            <div class="mega-hub-tts-block" style="border: 2px solid ' . esc_attr($secondaryColor) . '; padding: 20px; margin-bottom: 20px;">
                <h3 class="mega-hub-tts-title" style="color: ' . esc_attr($primaryColor) . ';">' . esc_html($title) . '</h3>
                <audio controls class="custom-audio-player">
                    <source src="' . esc_url($audioUrl) . '" type="audio/mpeg">
                    Votre navigateur ne prend pas en charge l\'élément audio.
                </audio>
            </div>';
        }
    
        // Si l'URL est vide, ne retourne rien
        return '';
    }
    add_shortcode('mega_hub_tts_block', 'mega_hub_shortcode_tts_block');
    
    


function insert_audio_meta_in_head() {
    // Vérifie si on est sur une page de post et que le post n'est pas dans la catégorie 'agence-immobiliere'
    if (is_single() && !has_category('agence-immobiliere')) {
        global $post;
        
        // Récupère la méta de l'audio pour ce post
        $audioId = get_post_meta($post->ID, '_audio_attachment_id', true);

        // Si une méta audio existe, insère la balise meta dans le head
        if (!empty($audioId)) {
            echo '<meta name="audio_attachment_id" content="' . esc_attr($audioId) . '">';
        }
    }
}
add_action('wp_head', 'insert_audio_meta_in_head');



} // fermeture du init
add_action('init', 'init_tts_feature_public');



/* ----------------- A partir d'ici ça charde même si la fonctionnalité est désactivée ----------------------- */