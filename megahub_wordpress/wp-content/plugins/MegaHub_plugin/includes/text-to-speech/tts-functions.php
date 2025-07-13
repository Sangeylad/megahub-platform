<?php

function init_tts_feature() {
    $options = get_option('mega_hub_options_tts');

    // Vérifie si l'option 'mega_hub_tts_enable' est définie et différente de 'on'
    if (!isset($options['mega_hub_tts_enable']) || $options['mega_hub_tts_enable'] !== 'on') {
        return; // Sort de la fonction si TTS n'est pas activé
    }


function add_custom_tts_metabox() {
    add_meta_box(
        'custom_tts_metabox',
        __('Add Audio', 'mega-hub'),
        'custom_tts_metabox_content',
        'post',
        'side',
        'high'
    );
}
add_action('add_meta_boxes', 'add_custom_tts_metabox');


function custom_tts_metabox_content($post) {
    wp_nonce_field('custom_tts_metabox', 'custom_tts_metabox_nonce');
    $audioId = get_post_meta($post->ID, '_audio_attachment_id', true);

    $buttonText = empty($audioId) ? __('Generate TTS', 'mega-hub') : __('Update TTS', 'mega-hub');
    $messageText = __('The TTS will be generated and added to this post.', 'mega-hub');
    $excludeText = __('Use the [exclude_from_audio]...[/exclude_from_audio] shortcode to exclude specific content from TTS generation.', 'mega-hub');

    echo '<button id="tts_button" class="button button-primary button-large">' . esc_html($buttonText) . '</button>';
    echo '<p style="margin-top: 10px;"><small>' . esc_html($messageText) . '</small></p>';
    echo '<p style="margin-top: 10px;"><small>' . esc_html($excludeText) . '</small></p>';

    // JavaScript pour gérer le clic sur le bouton
    ?>
    <script type="text/javascript">
    jQuery(document).ready(function($) {
        $('#tts_button').click(function(e) {
            e.preventDefault();
            if (confirm("<?php _e('Generating TTS may incur costs. Continue?', 'mega-hub'); ?>")) {
                var data = {
                    'action': 'send_tts_megahub',
                    'post_id': <?php echo $post->ID; ?>,
                    'nonce': '<?php echo wp_create_nonce('custom_tts_metabox'); ?>'
                };
                $.post(ajaxurl, data, function(response) {
                    if (response.success) {
                        alert('<?php _e('TTS generated successfully.', 'mega-hub'); ?>');
                        location.reload();
                    } else {
                        alert(response.data.message);
                    }
                });
            }
        });
    });
    </script>
    <?php
}

function remove_exclude_from_audio_tags($content) {
    // Supprime uniquement les balises, mais laisse le contenu entre elles
    $content = preg_replace('/\[exclude_from_audio\]/', '', $content);
    $content = preg_replace('/\[\/exclude_from_audio\]/', '', $content);

    return $content;
}

add_filter('the_content', 'remove_exclude_from_audio_tags');


add_action('wp_ajax_send_tts_megahub', 'send_tts_request_to_megahub');




function store_audio_on_wordpress($audio_content, $audio_title = 'OpenAI_Generated_Audio') {
    $upload_dir = wp_upload_dir();
    $file_path = $upload_dir['path'] . '/' . $audio_title . '.mp3';
    file_put_contents($file_path, $audio_content);

    if (!file_exists($file_path)) {
        return null;
    }

    $file_array = ['name' => basename($file_path), 'tmp_name' => $file_path, 'error' => 0, 'size' => filesize($file_path)];
    $overrides = ['test_form' => false, 'test_size' => true];
    $file_moved = wp_handle_sideload($file_array, $overrides);

    if (isset($file_moved['error'])) {
        @unlink($file_path);
        return null;
    }

    $attachment = [
        'guid' => $upload_dir['url'] . '/' . basename($file_moved['file']), 
        'post_mime_type' => 'audio/mpeg',
        'post_title' => preg_replace('/\.[^.]+$/', '', basename($file_moved['file'])),
        'post_content' => '',
        'post_status' => 'inherit'
    ];

    $attachment_id = wp_insert_attachment($attachment, $file_moved['file']);
    require_once(ABSPATH . 'wp-admin/includes/image.php');
    $attach_data = wp_generate_attachment_metadata($attachment_id, $file_moved['file']);
    wp_update_attachment_metadata($attachment_id, $attach_data);

    return $attachment_id ? $attachment_id : null;
}


function add_tts_option_to_admin_bar($wp_admin_bar) {
    if (is_singular('post')) {
        $post = get_queried_object();
        if (current_user_can('edit_post', $post->ID) && $post->post_status === 'publish') {
            $args = array(
                'id'    => 'tts_option',
                'title' => 'Générer Audio TTS',
                'href'  => '#',
                'meta'  => array(
                    'onclick' => 'requestTTS(' . $post->ID . '); return false;', // Empêche la redirection par défaut
                ),
            );
            $wp_admin_bar->add_node($args);
        }
    }
}

add_action('admin_bar_menu', 'add_tts_option_to_admin_bar', 100);

// Ajoute le script JavaScript pour gérer la génération TTS
add_action('wp_footer', 'tts_admin_bar_script');
function tts_admin_bar_script() {
    if (is_singular('post')) {
        $nonce = wp_create_nonce('custom_tts_metabox');
        ?>
        <script type="text/javascript">
            function requestTTS(postId) {
                // Boîte de confirmation informant de la potentielle dépense
                var isConfirmed = confirm("Attention, cette requête coûte environ 20cts. Êtes-vous sûr ?");

                // Si l'utilisateur clique sur "OK", la requête est envoyée
                if (isConfirmed) {
                    var data = {
                        'action': 'request_tts',
                        'post_id': postId,
                        'nonce': '<?php echo $nonce; ?>'
                    };

                    jQuery.post(ajaxurl, data, function(response) {
                        alert(response.data.message);
                        // Actualise la page après avoir affiché le message
                        window.location.reload(true);
                    }).fail(function() {
                        alert("Erreur lors de l'envoi de la requête.");
                        // Tu peux aussi choisir d'actualiser la page en cas d'échec, ou non
                        // window.location.reload(true);
                    });
                }
            }


        </script>
        <?php
    }
}














} // fermeture du init
add_action('init', 'init_tts_feature');



/* ----------------- A partir d'ici ça charge même si la fonctionnalité est désactivée ----------------------- */