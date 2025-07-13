<?php
function display_video_generation_form() {
    echo '<h2>Générer une vidéo diaporama</h2>';
    echo '<form method="post" action="">';
    echo '<label for="photo1">Photo 1 (URL) :</label>';
    echo '<input type="text" id="photo1" name="photo1" required><br>';
    echo '<label for="photo2">Photo 2 (URL) :</label>';
    echo '<input type="text" id="photo2" name="photo2" required><br>';
    echo '<label for="photo3">Photo 3 (URL) :</label>';
    echo '<input type="text" id="photo3" name="photo3" required><br>';
    echo '<input type="hidden" name="generate_video" value="1">';
    echo '<button type="submit" class="button">Générer la vidéo</button>';
    echo '</form>';

    if (isset($_POST['generate_video'])) {
        handle_video_generation();
    }
}

function handle_video_generation() {
    $photo1_url = esc_url_raw($_POST['photo1']);
    $photo2_url = esc_url_raw($_POST['photo2']);
    $photo3_url = esc_url_raw($_POST['photo3']);
    $image_urls = [$photo1_url, $photo2_url, $photo3_url];
    $upload_dir = wp_upload_dir();
    $downloaded_images = [];

    foreach ($image_urls as $image_url) {
        $image_data = file_get_contents($image_url);
        if ($image_data !== false) {
            $file_name = basename($image_url);
            $file_path = $upload_dir['path'] . '/' . $file_name;
            file_put_contents($file_path, $image_data);
            $downloaded_images[] = $file_path;
        } else {
            echo 'Erreur lors du téléchargement de l\'image: ' . $image_url . '<br>';
        }
    }

    if (!empty($downloaded_images)) {
        $plugin_dir = plugin_dir_path(__FILE__);
        $timestamp = time();
        $command = escapeshellcmd("python3 {$plugin_dir}video_builder.py " . implode(' ', $downloaded_images) . " {$upload_dir['path']}");
        echo 'Commande exécutée: ' . $command . '<br>';
        $output = shell_exec($command);
        echo 'Sortie du script Python: ' . $output . '<br>';

        $output_filename = "output_video_" . date("Ymd-His", $timestamp) . ".mp4";
        $output_path = $upload_dir['path'] . '/' . $output_filename;

        if (file_exists($output_path)) {
            // Enregistrer la vidéo dans la médiathèque de WordPress
            $file_array = [
                'name' => $output_filename,
                'tmp_name' => $output_path
            ];

            $attachment_id = media_handle_sideload($file_array, 0);
            if (!is_wp_error($attachment_id)) {
                $video_url = wp_get_attachment_url($attachment_id);
                echo 'Vidéo créée avec succès ! ';
                echo '<a href="' . $video_url . '" target="_blank">Voir la vidéo</a>';
            } else {
                echo 'Erreur lors de l\'upload de la vidéo.';
            }
        } else {
            echo 'Erreur lors de la création de la vidéo.';
        }
    } else {
        echo 'Impossible de télécharger les images à partir des URLs fournies.';
    }
}

// Ajoute cette fonction à un hook ou shortcode pour l'afficher dans le back-office
add_action('admin_menu', function() {
    add_menu_page('Générateur de Vidéo', 'Générateur de Vidéo', 'manage_options', 'video-generator', 'display_video_generation_form');
});
