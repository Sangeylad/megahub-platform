<?php
/*
function mega_hub_add_structured_data_to_head() {
    $options = get_option('mega_hub_options_seo_structured_data');

    // Vérifie si au moins un champ est rempli pour éviter d'ajouter des données structurées inutiles
    $is_any_field_filled = false;
    foreach ($options as $value) {
        if (!empty($value)) {
            $is_any_field_filled = true;
            break;
        }
    }

    // Si aucun champ n'est rempli, ne rien faire
    if (!$is_any_field_filled) {
        return;
    }

    // Début de la construction du tableau de données structurées
    $structured_data = [
        '@context' => 'http://schema.org',
        '@type' => $options['mega_hub_schema_type'] ?? 'Organization',
    ];

    // Ajoute chaque champ rempli au tableau de données structurées
    if (!empty($options['mega_hub_organization_name'])) {
        $structured_data['name'] = $options['mega_hub_organization_name'];
    }

    if (!empty($options['mega_hub_organization_url'])) {
        $structured_data['url'] = $options['mega_hub_organization_url'];
    }

    if (!empty($options['mega_hub_organization_logo'])) {
        $structured_data['logo'] = $options['mega_hub_organization_logo'];
    }

    if (!empty($options['mega_hub_contact_type']) && !empty($options['mega_hub_contact_info'])) {
        $structured_data['contactPoint'] = [
            '@type' => 'ContactPoint',
            'contactType' => $options['mega_hub_contact_type'],
            'telephone' => $options['mega_hub_contact_info'],
        ];
    }

    // Ajoute d'autres champs ici selon les besoins, en vérifiant chaque fois s'ils ne sont pas vides

    // Encode les données structurées en JSON et les insère dans une balise <script> dans le <head>
    echo '<script type="application/ld+json">' . json_encode($structured_data, JSON_UNESCAPED_SLASHES | JSON_PRETTY_PRINT) . '</script>';
}

// Accroche la fonction au hook wp_head pour qu'elle s'exécute dans la section <head> des pages
add_action('wp_head', 'mega_hub_add_structured_data_to_head');



*/

// Ajouter la métabox
add_action('add_meta_boxes', 'mega_hub_add_custom_box');
function mega_hub_add_custom_box() {
    // Ajoute une métabox à toutes les types de post, y compris 'page' et 'post'
    $screens = ['post', 'page'];
    foreach ($screens as $screen) {
        add_meta_box(
            'mega_hub_box_id',           // ID unique de la métabox
            'SEO Structured Data',       // Titre de la métabox
            'mega_hub_custom_box_html',  // Fonction de callback pour le contenu de la métabox
            $screen                      // L'écran sur lequel afficher la métabox
        );
    }
}

// Le contenu de la métabox
function mega_hub_custom_box_html($post) {
    // Utilisez get_post_meta pour récupérer les valeurs existantes dans la base de données et les afficher dans la métabox
    $value = get_post_meta($post->ID, '_mega_hub_meta_key', true);
    ?>
    <label for="mega_hub_field">SEO Structured Data JSON-LD:</label>
    <textarea name="mega_hub_field" id="mega_hub_field" rows="10" style="width:100%"><?php echo esc_textarea($value); ?></textarea>
    <?php
}

// Sauvegarder les données de la métabox
add_action('save_post', 'mega_hub_save_postdata');
function mega_hub_save_postdata($post_id) {
    // Vérifiez si notre champ personnalisé est défini.
    if (array_key_exists('mega_hub_field', $_POST)) {
        // Mettez à jour les données de la métabox dans la base de données.
        update_post_meta(
            $post_id,
            '_mega_hub_meta_key',
            $_POST['mega_hub_field']
        );
    }
}

// Insérer les données structurées dans la section <head>
add_action('wp_head', 'mega_hub_add_structured_data_to_head');
function mega_hub_add_structured_data_to_head() {
    if (is_front_page()) { // Vérifier si c'est la page d'accueil
        $structured_data = get_post_meta(get_option('page_on_front'), '_mega_hub_meta_key', true);
        if (!empty($structured_data)) {
            echo '<script type="application/ld+json">' . $structured_data . '</script>';
        }
    }
}


/* ------------------------------ META TITRE & DESCRIPTION & SLUG ------------------------------------------ */
add_action('add_meta_boxes', 'custom_seo_meta_box');
function custom_seo_meta_box() {
    $screens = ['post', 'page'];
    foreach ($screens as $screen) {
        add_meta_box(
            'seo_meta_box',
            'SEO Settings',
            'seo_meta_box_html',
            $screen,
            'normal',
            'high'
        );
    }
}

function seo_meta_box_html($post) {
    $seo_title = get_post_meta($post->ID, '_seo_title', true);
    $seo_description = get_post_meta($post->ID, '_seo_description', true);
    $seo_slug = get_post_meta($post->ID, '_seo_custom_slug', true);

    ?>
    <div class="seo-meta-box-content">
        <p>
            <label for="seo_title"><?php _e('SEO Title:', 'mega-hub'); ?></label>
            <input type="text" id="seo_title" name="seo_title" value="<?php echo esc_attr($seo_title); ?>" class="widefat" placeholder="<?php _e('Optimal length: 40 characters', 'mega-hub'); ?>" />
            <div id="seo_title_feedback" style="height: 2px; width: 100%;"></div>
        </p>
        <p>
            <label for="seo_description"><?php _e('SEO Description:', 'mega-hub'); ?></label>
            <textarea id="seo_description" name="seo_description" class="widefat" rows="4" placeholder="<?php _e('Optimal length: 140 characters', 'mega-hub'); ?>"><?php echo esc_textarea($seo_description); ?></textarea>
            <div id="seo_description_feedback" style="height: 2px; width: 100%;"></div>
        </p>
        <p>
            <label for="seo_slug"><?php _e('Custom Slug:', 'mega-hub'); ?></label>
            <input type="text" id="seo_slug" name="seo_slug" value="<?php echo esc_attr($seo_slug); ?>" class="widefat" />
        </p>
        <p><?php _e('For more information on choosing the right meta title and description,', 'mega-hub'); ?> <a href="https://www.humari.fr/complete_guide_meta_titles_meta_description?utm_source=plugin_wp" target="_blank"><?php _e('click here', 'mega-hub'); ?></a>.</p>
    </div>
    <script>
    document.addEventListener('DOMContentLoaded', function() {
        var seoTitleInput = document.getElementById('seo_title');
        var seoDescriptionTextarea = document.getElementById('seo_description');

        function updateFeedbackBar(element, feedbackElementId, lowThreshold, highThreshold) {
            var feedbackElement = document.getElementById(feedbackElementId);
            var length = element.value.length;
            feedbackElement.style.backgroundColor = length <= lowThreshold ? 'green' : length <= highThreshold ? 'orange' : 'red';
        }

        seoTitleInput.addEventListener('input', function() {
            updateFeedbackBar(this, 'seo_title_feedback', 40, 60);
        });

        seoDescriptionTextarea.addEventListener('input', function() {
            updateFeedbackBar(this, 'seo_description_feedback', 140, 160);
        });

        // Initial update on load
        updateFeedbackBar(seoTitleInput, 'seo_title_feedback', 40, 60);
        updateFeedbackBar(seoDescriptionTextarea, 'seo_description_feedback', 140, 160);
    });
    </script>
    <?php
}




add_action('save_post', 'save_seo_meta_box_data');
function save_seo_meta_box_data($post_id) {
    if (defined('DOING_AUTOSAVE') && DOING_AUTOSAVE) return;
    if (!current_user_can('edit_post', $post_id)) return;

    if (isset($_POST['seo_title'])) {
        update_post_meta($post_id, '_seo_title', sanitize_text_field($_POST['seo_title']));
    }

    if (isset($_POST['seo_description'])) {
        update_post_meta($post_id, '_seo_description', sanitize_textarea_field($_POST['seo_description']));
    }

    if (isset($_POST['seo_slug'])) {
        update_post_meta($post_id, '_seo_custom_slug', sanitize_title($_POST['seo_slug']));
    }
}

add_filter('pre_get_document_title', 'custom_seo_title', 999);
function custom_seo_title($title) {
    global $post;
    if (isset($post) && is_a($post, 'WP_Post')) {
        $seo_title = get_post_meta($post->ID, '_seo_title', true);
        if (!empty($seo_title)) {
            return do_shortcode($seo_title);
        }
    }
    return $title;
}

add_action('wp_head', 'custom_seo_description');
function custom_seo_description() {
    global $post;
    if (isset($post) && is_a($post, 'WP_Post')) {
        $seo_description = get_post_meta($post->ID, '_seo_description', true);
        if (!empty($seo_description)) {
            echo '<meta name="description" content="' . esc_attr(do_shortcode($seo_description)) . '">' . "\n";
        }
    }
}
