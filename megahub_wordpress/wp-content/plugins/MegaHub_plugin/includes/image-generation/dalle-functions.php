<?php
function init_dalle_feature() {

    $options = get_option('mega_hub_options_dalle');

    // Vérifie si l'option 'mega_hub_auto_blogger_enable' est définie et différente de 'on'
    if (!isset($options['mega_hub_dalle_enable']) || $options['mega_hub_dalle_enable'] !== 'on') {
        return; // Sort de la fonction si Auto Blogger n'est pas activé
    }

function add_dalle_thumbnail_button() {
    global $pagenow;

    // Vérifiez si vous êtes sur la page de création ou d'édition d'un article
    if (in_array($pagenow, array('post-new.php', 'post.php'))) {
        ?>
        <script type="text/javascript">
        jQuery(document).ready(function($) {
            // Sélectionnez la boîte de l'image à la une
            var featuredImageBox = $('#postimagediv');

            // Créez le bouton
            var dalleButton = $('<button/>', {
                text: '<?php _e('Generate Thumbnail with DALL·E', 'mega-hub'); ?>',
                id: 'dalle_generate_button',
                class: 'button',
                style: 'margin-top: 10px; width: 100%;'
            });

            // Ajoutez le bouton sous la zone de l'image à la une
            featuredImageBox.find('.inside').append(dalleButton);

            // Gérez le clic sur le bouton
            $('#dalle_generate_button').click(function(e) {
                e.preventDefault();
                // Ici, vous pouvez appeler la fonction send_image_request_to_megahub()
                // avec le contenu de l'article et le titre comme arguments.
                // Notez que cette partie du code est à titre d'exemple.
                // Vous devez implémenter la logique d'envoi et de gestion de la réponse.
                var data = {
                    'action': 'send_image_request_to_megahub',
                    'post_id': <?php echo get_the_ID(); ?>,
                    'nonce': '<?php echo wp_create_nonce('dalle_generate_nonce'); ?>'
                };
                $.post(ajaxurl, data, function(response) {
                    if (response.success) {
                        alert('<?php _e('Thumbnail generated successfully.', 'mega-hub'); ?>');
                        // Mettez à jour l'image à la une ici si nécessaire
                    } else {
                        alert(response.data.message);
                    }
                });
            });
        });
        </script>
        <?php
    }
}
add_action('admin_footer', 'add_dalle_thumbnail_button');


}


add_action('init', 'init_dalle_feature');


/* -------------------------------- Tout ce qui est en dessous de cette ligne sera chargé même si la génération d'images est désactivée --------------------------------------*/