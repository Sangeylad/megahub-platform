<?php


function send_tts_request_to_megahub() {
    check_ajax_referer('custom_tts_metabox', 'nonce');
    $postId = isset($_POST['post_id']) ? intval($_POST['post_id']) : 0;
    $api_key = get_option('mega_hub_options_global')['mega_hub_api_key'];
    $tts_voice = get_option('mega_hub_options_tts')['mega_hub_tts_voice'];

    $post = get_post($postId);
    if (!$post) {
        wp_send_json_error(['message' => 'Post introuvable.']);
        return;
    }

    // Nettoyer le contenu des balises [exclude_from_audio]...[/exclude_from_audio]
    $content = mb_convert_encoding($post->post_content, 'UTF-8');
    $content = preg_replace('/\[exclude_from_audio\].*?\[\/exclude_from_audio\]/s', '', $content);

    $django_api_url = 'https://your-django-api-url.com/tts';
    $response = wp_remote_post($django_api_url, [
        'body' => json_encode([
            'api_key' => $api_key,
            'voice' => $tts_voice,
            'content' => $content
        ]),
        'headers' => ['Content-Type' => 'application/json']
    ]);

    if (is_wp_error($response)) {
        wp_send_json_error(['message' => 'Erreur de communication avec l\'API.']);
        return;
    }

    $body = wp_remote_retrieve_body($response);
    $data = json_decode($body, true);

    if (isset($data['success']) && $data['success']) {
        $audio_content = base64_decode($data['audio_content_base64']);
        $audioId = store_audio_on_wordpress($audio_content, 'TTS_' . $postId . '_' . time());
        if ($audioId) {
            update_post_meta($postId, '_audio_attachment_id', $audioId);
            wp_send_json_success(['message' => 'TTS généré et sauvegardé avec succès.']);
        } else {
            wp_send_json_error(['message' => 'Erreur lors de l\'enregistrement du fichier audio.']);
        }
    } else {
        wp_send_json_error(['message' => 'Erreur lors de la génération du TTS.']);
    }
}







function request_indexing_megahub($post_id, $api_key, $indexing_url) {
    // Ton code pour envoyer la requête d'indexation à ton API
    // Utilise wp_remote_post() ou wp_remote_get() selon les besoins de ton API
}



function send_image_request_to_megahub(){

}




function display_logs() {
    $log_file = ABSPATH . 'wp-content/debug.log';
    
    // Vérifiez si le fichier de logs existe
    if (!file_exists($log_file)) {
        echo '<p>Aucun log n\'a été enregistré pour le moment.</p>';
        return;
    }
    
    else{
        // Ajoutez un bouton pour réinitialiser les logs
        echo '<form action="" method="post">';
        echo '<input type="submit" name="reset_logs" value="Réinitialiser les logs" class="button button-primary" />';
        echo '</form>';

        // Si le bouton de réinitialisation des logs a été cliqué
        if (isset($_POST['reset_logs'])) {
            // Réinitialiser le contenu du fichier de logs
            file_put_contents($log_file, '');
        }

        // Récupérez le contenu du fichier de logs
        $log_content = file_get_contents($log_file);

        // Séparez le contenu en lignes
        $log_lines = explode(PHP_EOL, $log_content);

        // Affichez chaque ligne de log
        foreach ($log_lines as $line) {
            // Vérifiez si la ligne de log doit être exclue
            if (strpos($line, '/home/pdxmjbn/ito2/wp-content/plugins/elementor-pro/modules/loop-builder/module.php') !== false) {
                continue;
            }

            // Affichez la ligne de log
            echo '<p>' . esc_html($line) . '</p>';
        }
    }

}


function send_autoblog_request_to_megahub($post_status, $publish_frequency, $author_id, $generate_thumbnail, $model_selection, $titles, $thumbnail_instructions){

}



