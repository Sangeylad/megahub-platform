<?php
function init_woocommerce_feature() {
    $options = get_option('mega_hub_options_woocommerce');

    // Vérifie si l'option 'mega_hub_tts_enable' est définie et différente de 'on'
    if (!isset($options['mega_hub_woocommerce_enable']) || $options['mega_hub_woocommerce_enable'] !== 'on') {
        return; // Sort de la fonction si TTS n'est pas activé
    }






















} // fermeture du init
add_action('init', 'init_woocommerce_feature');


/* ----------------- A partir d'ici ça charge même si la fonctionnalité est désactivée ----------------------- */