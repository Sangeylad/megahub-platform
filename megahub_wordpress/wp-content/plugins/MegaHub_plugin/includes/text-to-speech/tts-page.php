<?php


function mega_hub_text_to_speech_page() {
    $options = get_option('mega_hub_options_tts');
    $selected_voice = $options['mega_hub_tts_voice'] ?? 'alloy'; // 'alloy' est la valeur par défaut si aucune n'est sélectionnée dans les options

    ?>
    <div class="wrap">
        <h1><?php _e('TTS Audio Generator', 'mega-hub'); ?></h1>
        <div style="display: flex;">
            <div style="flex-grow: 1; margin-right: 20px;">
                <textarea id="mega-hub-tts-text" rows="4" style="width: 100%;" placeholder="<?php _e('Enter your text here...', 'mega-hub'); ?>"></textarea>
            </div>
            <div style="width: 200px; display: flex; flex-direction: column;">
                <select id="mega-hub-tts-voice" style="margin-bottom: 10px;">
                    <option value="alloy" <?php selected($selected_voice, 'alloy'); ?>>Alloy</option>
                    <option value="echo" <?php selected($selected_voice, 'echo'); ?>>Echo</option>
                    <option value="fable" <?php selected($selected_voice, 'fable'); ?>>Fable</option>
                    <option value="onyx" <?php selected($selected_voice, 'onyx'); ?>>Onyx</option>
                    <option value="nova" <?php selected($selected_voice, 'nova'); ?>>Nova</option>
                    <option value="shimmer" <?php selected($selected_voice, 'shimmer'); ?>>Shimmer</option>
                </select>
                <button type="button" id="mega-hub-tts-submit" class="button-primary" style="width: 100%;">Generate</button>
            </div>
        </div>
        <!-- Section pour afficher le dernier MP3 généré -->
        <?php mega_hub_display_last_generated_mp3(); ?>
    </div>
    <?php
}


function mega_hub_display_last_generated_mp3() {
    $last_mp3_id = get_option('mega_hub_last_tts_mp3_id');

    if ($last_mp3_id) {
        $mp3_url = wp_get_attachment_url($last_mp3_id);
        if ($mp3_url) {
            echo '<h2>' . __('Last Generated MP3', 'mega-hub') . '</h2>';
            echo '<audio controls><source src="' . esc_url($mp3_url) . '" type="audio/mpeg"></audio>';
            echo '<p><a href="' . esc_url($mp3_url) . '" download>' . __('Download MP3', 'mega-hub') . '</a></p>';
        }
    }
}

// Cette fonction devra être liée à une action AJAX pour gérer la requête de génération TTS.
function handle_tts_generation_request() {
    // Assurez-vous que le fichier MP3 est correctement reçu dans la requête, par exemple via $_FILES['mp3_file']
    if (isset($_FILES['mp3_file'])) {
        $file = $_FILES['mp3_file'];

        // Déterminer le chemin de stockage
        $upload_dir = wp_upload_dir();
        $target_dir = $upload_dir['path'] . '/TTS_megahub/'; // Chemin cible dans le dossier uploads
        if (!file_exists($target_dir)) {
            wp_mkdir_p($target_dir); // Crée le dossier s'il n'existe pas
        }

        // Déplacer le fichier MP3 dans le dossier cible
        $file_path = $target_dir . basename($file['name']);
        if (move_uploaded_file($file['tmp_name'], $file_path)) {
            // Enregistrer le fichier dans la bibliothèque des médias
            $attachment = array(
                'guid'           => $upload_dir['url'] . '/TTS_megahub/' . basename($file['name']), 
                'post_mime_type' => 'audio/mpeg',
                'post_title'     => preg_replace('/\.[^.]+$/', '', basename($file['name'])),
                'post_content'   => '',
                'post_status'    => 'inherit'
            );
            $attachment_id = wp_insert_attachment($attachment, $file_path);

            // Générer les métadonnées pour l'attachement et mettre à jour la base de données
            require_once(ABSPATH . 'wp-admin/includes/image.php');
            $attach_data = wp_generate_attachment_metadata($attachment_id, $file_path);
            wp_update_attachment_metadata($attachment_id, $attach_data);

            // Stocker l'ID de l'attachement comme le dernier MP3 généré
            update_option('mega_hub_last_tts_mp3_id', $attachment_id);

            // Renvoyer une réponse de succès
            wp_send_json_success(array('message' => 'MP3 file successfully uploaded and stored.', 'attachment_id' => $attachment_id));
        } else {
            wp_send_json_error(array('message' => 'Failed to move uploaded file.'));
        }
    } else {
        wp_send_json_error(array('message' => 'No MP3 file received.'));
    }
}


// Remplacez 'send_tts_request_to_megahub' par l'action réelle utilisée dans votre code JavaScript pour la requête AJAX
add_action('wp_ajax_send_tts_request_to_megahub', 'handle_tts_generation_request');
