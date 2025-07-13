<?php


function init_indexer_feature() {
    // Récupère les options du plugin pour l'Indexeur
    $options = get_option('mega_hub_options_indexer');

    // Vérifie si l'option 'mega_hub_indexer_enable' est définie et différente de 'on'
    if (!isset($options['mega_hub_indexer_enable']) || $options['mega_hub_indexer_enable'] !== 'on') {
        return; // Sort de la fonction si l'Indexeur n'est pas activé
    }

/* ---------------------- INDEXING DISPLAY -------------------------------------*/



function add_custom_indexing_metabox() {
    add_meta_box(
        'custom_indexing_metabox',
        __('Content Indexing', 'mega-hub'),
        'custom_indexing_metabox_content',
        ['post', 'page'], // Ajoute ici les types de post que tu veux indexer
        'side',
        'high'
    );
}
add_action('add_meta_boxes', 'add_custom_indexing_metabox');


function custom_indexing_metabox_content($post) {
    wp_nonce_field('custom_indexing_metabox', 'custom_indexing_metabox_nonce');
    echo '<button id="indexing_button" class="button button-primary button-large">' . esc_html__('Index on Google', 'mega-hub') . '</button>';
    echo '<p style="margin-top: 10px;"><small>' . esc_html__('The post will be submitted for indexing to Google.', 'mega-hub') . '</small></p>';
}


function add_ajaxurl_to_front() {
    echo '<script type="text/javascript">
            var ajaxurl = "' . admin_url('admin-ajax.php') . '";
          </script>';
}

add_action('wp_head', 'add_ajaxurl_to_front');

function add_indexing_option_to_admin_bar($wp_admin_bar) {
    if (is_singular(array('post', 'page'))) {
        $post = get_queried_object();
        if (current_user_can('edit_post', $post->ID) && $post->post_status === 'publish') {
            $args = array(
                'id'    => 'indexing_option',
                'title' => 'Indexer sur Google',
                'href'  => '#',
                'meta'  => array(
                    'onclick' => 'requestIndexing(' . $post->ID . ');',
                ),
            );
            $wp_admin_bar->add_node($args);
        }
    }
}

add_action('admin_bar_menu', 'add_indexing_option_to_admin_bar', 100);



/* ---------------------- INDEXING -------------------------------------*/



function indexing_script() {
    ?>
    <script type="text/javascript">
    jQuery(document).ready(function($) {
        $('#indexing_button').click(function(e) {
            e.preventDefault();
            var data = {
                'action': 'request_indexing_megahub',
                'post_id': $(this).data('post-id'),
                'nonce': '<?php echo wp_create_nonce('custom_indexing_metabox'); ?>'
            };

            $.post(ajaxurl, data, function(response) {
                alert(response.data.message);
            });
        });
    });
    </script>
    <?php
}
add_action('admin_footer', 'indexing_script');

function handle_request_indexing_megahub() {
    check_ajax_referer('custom_indexing_metabox', 'nonce');

    $post_id = isset($_POST['post_id']) ? intval($_POST['post_id']) : 0;
    $api_key = get_option('your_option_name_for_api_key'); // Récupère la clé API des réglages
    $indexing_url = get_option('your_option_name_for_indexing_url'); // Récupère l'URL d'indexation des réglages

    // Assure-toi que le post existe et est publié
    $post = get_post($post_id);
    if (!$post || $post->post_status !== 'publish') {
        wp_send_json_error(['message' => __('The post must be published to be indexed.', 'mega-hub')]);
        return;
    }

    // Ici, tu appelles ta fonction d'indexation
    $result = request_indexing_megahub($post_id, $api_key, $indexing_url);

    if ($result) {
        wp_send_json_success(['message' => __('Indexing was successful.', 'mega-hub')]);
    } else {
        wp_send_json_error(['message' => __('Indexing failed.', 'mega-hub')]);
    }
}
add_action('wp_ajax_request_indexing_megahub', 'handle_request_indexing_megahub');






/* ---------------------- BULK INDEXING -------------------------------------*/



function add_bulk_indexing_option($bulk_actions) {
    $bulk_actions['index_on_google'] = __('Index on Google', 'mega-hub');
    return $bulk_actions;
}

add_filter('bulk_actions-edit-post', 'add_bulk_indexing_option');
add_filter('bulk_actions-edit-page', 'add_bulk_indexing_option');



function handle_bulk_indexing($redirect_to, $doaction, $post_ids) {
    if ($doaction === 'index_on_google') {
        foreach ($post_ids as $post_id) {
            // Ici, tu appelles ta fonction d'indexation pour chaque article
            // Assure-toi que cette fonction ne cause pas de redirection ou d'erreur fatale
            request_indexing_megahub($post_id);
        }
        // Ajoute un paramètre à l'URL pour afficher une notification
        $redirect_to = add_query_arg('bulk_indexed_posts', count($post_ids), $redirect_to);
    }
    return $redirect_to;
}

add_filter('handle_bulk_actions-edit-post', 'handle_bulk_indexing', 10, 3);
add_filter('handle_bulk_actions-edit-page', 'handle_bulk_indexing', 10, 3);



function bulk_indexing_admin_notice() {
    if (!empty($_REQUEST['bulk_indexed_posts'])) {
        $count = intval($_REQUEST['bulk_indexed_posts']);
        printf('<div id="message" class="updated notice is-dismissible"><p>' .
            _n('%s post has been submitted for indexing on Google.',
               '%s posts have been submitted for indexing on Google.',
               $count,
               'mega-hub'
            ) . '</p></div>', $count);
    }
}

add_action('admin_notices', 'bulk_indexing_admin_notice');

function add_indexing_link_to_row_actions($actions, $post) {
    if ($post->post_status === 'publish') {
        $actions['index_on_google'] = '<a href="#" class="index-on-google" data-post-id="' . $post->ID . '">' . __('Index on Google', 'mega-hub') . '</a>';
    }
    return $actions;
}

add_filter('post_row_actions', 'add_indexing_link_to_row_actions', 10, 2);
add_filter('page_row_actions', 'add_indexing_link_to_row_actions', 10, 2);



function add_indexation_status_column($columns) {
    $columns['indexation_status'] = __('Indexation Status', 'mega-hub');
    return $columns;
}

add_filter('manage_posts_columns', 'add_indexation_status_column');
add_filter('manage_pages_columns', 'add_indexation_status_column');

function fill_indexation_status_column($column, $post_id) {
    if ($column === 'indexation_status') {
        $last_update = get_the_modified_date('U', $post_id);
        $last_index_request = get_post_meta($post_id, 'last_index_request', true);

        if ($last_index_request && $last_update <= $last_index_request) {
            echo '<span class="indexation-status-icon good" title="' . esc_attr__('Good', 'mega-hub') . '"></span>';
        } else {
            echo '<span class="indexation-status-icon bad" title="' . esc_attr__('Not submitted since last update', 'mega-hub') . '"></span>';
        }
    }
}

add_action('manage_posts_custom_column', 'fill_indexation_status_column', 10, 2);
add_action('manage_pages_custom_column', 'fill_indexation_status_column', 10, 2);




} // fermeture du init
add_action('init', 'init_indexer_feature');



/* ----------------- A partir d'ici ça charge même si la fonctionnalité est désactivée ----------------------- */