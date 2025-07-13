<?php



function mega_hub_settings_page() {
    $active_tab = isset($_GET['tab']) ? $_GET['tab'] : 'general_settings';
    ?>
    <div class="wrap">
    <h2><?php _e('Mega Hub Settings', 'mega-hub'); ?></h2>
    <h2 class="nav-tab-wrapper">
        <a href="?page=mega-hub-settings&tab=general_settings" class="nav-tab <?php echo $active_tab == 'general_settings' ? 'nav-tab-active' : ''; ?>"><?php _e('General', 'mega-hub'); ?></a>
        <a href="?page=mega-hub-settings&tab=tts_settings" class="nav-tab <?php echo $active_tab == 'tts_settings' ? 'nav-tab-active' : ''; ?>"><?php _e('TTS', 'mega-hub'); ?></a>
        <a href="?page=mega-hub-settings&tab=dalle_settings" class="nav-tab <?php echo $active_tab == 'dalle_settings' ? 'nav-tab-active' : ''; ?>"><?php _e('Dalle', 'mega-hub'); ?></a>
        <a href="?page=mega-hub-settings&tab=seo_settings" class="nav-tab <?php echo $active_tab == 'seo_settings' ? 'nav-tab-active' : ''; ?>"><?php _e('SEO', 'mega-hub'); ?></a>
        <a href="?page=mega-hub-settings&tab=auto_blogger_settings" class="nav-tab <?php echo $active_tab == 'auto_blogger_settings' ? 'nav-tab-active' : ''; ?>"><?php _e('Auto Blogger', 'mega-hub'); ?></a>
        <a href="?page=mega-hub-settings&tab=content_tools" class="nav-tab <?php echo $active_tab == 'content_tools' ? 'nav-tab-active' : ''; ?>"><?php _e('Content Tools', 'mega-hub'); ?></a>
        <a href="?page=mega-hub-settings&tab=woocommerce_settings" class="nav-tab <?php echo $active_tab == 'woocommerce_settings' ? 'nav-tab-active' : ''; ?>"><?php _e('WooCommerce', 'mega-hub'); ?></a>
    </h2>


        <div id="general_settings" class="tab-content" <?php echo $active_tab == 'general_settings' ? 'style="display: block;"' : ''; ?>>
            <form method="post" action="options.php">
                <?php
                settings_fields('mega_hub_global');
                do_settings_sections('mega_hub_global');
                submit_button();
                ?>
            </form>
        </div>

        <div id="tts_settings" class="tab-content" <?php echo $active_tab == 'tts_settings' ? 'style="display: block;"' : 'style="display: none;"'; ?>>
            <form method="post" action="options.php">
                <?php
                settings_fields('mega_hub_tts');
                do_settings_sections('mega_hub_tts');
                submit_button();
                ?>
            </form>
        </div>

        <div id="dalle_settings" class="tab-content" <?php echo $active_tab == 'dalle_settings' ? 'style="display: block;"' : 'style="display: none;"'; ?>>
            <form method="post" action="options.php">
                <?php
                // Assurez-vous que 'mega_hub_dalle' est enregistré avec register_setting() et que les sections/fields appropriés sont ajoutés
                settings_fields('mega_hub_dalle');
                do_settings_sections('mega_hub_dalle');
                submit_button();
                ?>
            </form>
        </div>


        <div id="seo_settings" class="tab-content" <?php echo $active_tab == 'seo_settings' ? 'style="display: block;"' : 'style="display: none;"'; ?>>
            <form method="post" action="options.php">
                <?php
                settings_fields('mega_hub_seo');
                do_settings_sections('mega_hub_seo');
                submit_button();
                ?>
            </form>
        </div>

        <div id="auto_blogger_settings" class="tab-content" <?php echo $active_tab == 'auto_blogger_settings' ? 'style="display: block;"' : 'style="display: none;"'; ?>>
            <form method="post" action="options.php">
                <?php
                settings_fields('mega_hub_auto_blogger');
                do_settings_sections('mega_hub_auto_blogger');
                submit_button();
                ?>
            </form>
        </div>

        <div id="content_tools" class="tab-content" <?php echo $active_tab == 'content_tools' ? 'style="display: block;"' : 'style="display: none;"'; ?>>
            <form method="post" action="options.php">
                <?php
                settings_fields('mega_hub_content_tools');
                do_settings_sections('mega_hub_content_tools');
                submit_button();
                ?>
            </form>
        </div>

        <div id="woocommerce_settings" class="tab-content" <?php echo $active_tab == 'woocommerce_settings' ? 'style="display: block;"' : 'style="display: none;"'; ?>>
            <form method="post" action="options.php">
                <?php
                // Assurez-vous d'enregistrer les paramètres de WooCommerce et d'ajouter les sections/champs appropriés
                settings_fields('mega_hub_woocommerce');
                do_settings_sections('mega_hub_woocommerce');
                submit_button();
                ?>
            </form>
        </div>


    </div>
    <?php

display_logs();
}






/* ---------------------------------- Parametres globaux ------------------------------------------*/

function mega_hub_section_global_cb() {
    echo '<p>' . esc_html__('General settings for the Mega Hub plugin. Configure your API key, brand name, site information, and preferred language here.', 'mega-hub') . '</p>';
}

function mega_hub_brand_render() {
    $options = get_option('mega_hub_options_global');
    $brand = isset($options['mega_hub_brand']) ? esc_attr($options['mega_hub_brand']) : '';
    echo "<input type='text' name='mega_hub_options_global[mega_hub_brand]' value='{$brand}' placeholder='" . esc_attr__('Enter your brand name here', 'mega-hub') . "'>";
}


function mega_hub_api_key_render() {
    $options = get_option('mega_hub_options_global');
    $isApiKeySet = !empty($options['mega_hub_api_key']);

    // Champ de saisie pour la nouvelle clé API ou pour modifier l'existante
    echo "<input type='text' id='mega_hub_api_key' name='mega_hub_options_global[mega_hub_api_key]' " . ($isApiKeySet ? "style='display: none;'" : "") . " placeholder='" . esc_attr__('Enter your MegaHub API key here', 'mega-hub') . "' />";

    // Si la clé API est définie, afficher un placeholder et un lien pour modifier
    if ($isApiKeySet) {
        echo "<span id='api_key_placeholder'>**********</span>";
        echo "<a href='#' id='change_api_key_link' onclick='document.getElementById(\"mega_hub_api_key\").style.display=\"inline\"; document.getElementById(\"api_key_placeholder\").style.display=\"none\"; document.getElementById(\"change_api_key_link\").style.display=\"none\"; return false;'>" . esc_html__('Change API Key', 'mega-hub') . "</a>";
    }
}

function mega_hub_email_notifications_render() {
    $options = get_option('mega_hub_options_global');

    // Utilise 'on' comme valeur par défaut si l'option n'est pas encore définie
    $email_notifications_enable = isset($options['mega_hub_email_notifications']) ? $options['mega_hub_email_notifications'] : 'on';

    // Début du rendu du champ de sélection
    echo "<select name='mega_hub_options_global[mega_hub_email_notifications]'>";
    echo "<option value='on' " . selected($email_notifications_enable, 'on', false) . ">" . esc_html__('On', 'mega-hub') . "</option>";
    echo "<option value='off' " . selected($email_notifications_enable, 'off', false) . ">" . esc_html__('Off', 'mega-hub') . "</option>";
    echo "</select>";
}


function mega_hub_email_render() {
    $options = get_option('mega_hub_options_global', array('mega_hub_email' => get_option('admin_email')));
    $email = !empty($options['mega_hub_email']) ? $options['mega_hub_email'] : get_option('admin_email');
    echo "<input type='email' id='mega_hub_email' name='mega_hub_options_global[mega_hub_email]' value='" . esc_attr($email) . "' class='regular-text' />";
}


function mega_hub_business_description_render() {
    $options = get_option('mega_hub_options_global');
    echo "<input type='text' name='mega_hub_options_global[mega_hub_business_description]' value='" . esc_attr($options['mega_hub_business_description'] ?? '') . "' maxlength='150' placeholder='" . esc_attr__('Describe your business in a few words (max 150 characters)', 'mega-hub') . "'>";
    echo "<p class='description'>" . esc_html__('Please keep the description under 150 characters.', 'mega-hub') . "</p>";
}

function mega_hub_currency_render() {
    $options = get_option('mega_hub_options_global', ['mega_hub_currency' => 'USD']);
    echo "<select name='mega_hub_options_global[mega_hub_currency]'>";
    $currencies = [
        'USD' => 'United States Dollar (USD)',
        'EUR' => 'Euro (EUR)',
        'JPY' => 'Japanese Yen (JPY)',
        'GBP' => 'British Pound (GBP)',
        'AUD' => 'Australian Dollar (AUD)',
        'CAD' => 'Canadian Dollar (CAD)',
        'CHF' => 'Swiss Franc (CHF)',
        'CNY' => 'Chinese Yuan (CNY)',
        'SEK' => 'Swedish Krona (SEK)',
        'NZD' => 'New Zealand Dollar (NZD)'
    ];
    foreach ($currencies as $code => $name) {
        echo "<option value='{$code}' " . selected($options['mega_hub_currency'], $code, false) . ">{$name}</option>";
    }
    echo "</select>";
}


function mega_hub_language_render() {
    $options = get_option('mega_hub_options_global', ['mega_hub_language' => 'en']);
    echo "<select name='mega_hub_options_global[mega_hub_language]'>";
    $languages = [
        'ar' => 'العربية (Arabic)',
        'bn' => 'বাংলা (Bengali)',
        'en' => 'English',
        'fr' => 'Français (French)',
        'hi' => 'हिन्दी (Hindi)',
        'es' => 'Español (Spanish)',
        'ms' => 'Bahasa Melayu (Malay)',
        'pt' => 'Português (Portuguese)',
        'ru' => 'Русский (Russian)',
        'zh' => '中文 (Chinese)',
    ];
    foreach ($languages as $code => $name) {
        echo "<option value='{$code}' " . selected($options['mega_hub_language'], $code, false) . ">{$name}</option>";
    }
    echo "</select>";
}


/* ---------------------------------- TTS ------------------------------------------*/

function mega_hub_section_tts_cb() {
    echo '<p>' . esc_html__('Below are the shortcodes available for the Text to Speech feature:', 'mega-hub') . '</p>';
    
    echo '<table class="widefat">';
    echo '<thead>';
    echo '<tr>';
    echo '<th>' . esc_html__('Shortcode', 'mega-hub') . '</th>';
    echo '<th>' . esc_html__('Description', 'mega-hub') . '</th>';
    echo '</tr>';
    echo '</thead>';
    echo '<tbody>';
    echo '<tr>';
    echo '<td><code>[mega_hub_tts_player]</code></td>';
    echo '<td>' . esc_html__('Displays the TTS audio player.', 'mega-hub') . '</td>';
    echo '</tr>';
    echo '<tr>';
    echo '<td><code>[mega_hub_tts_block]</code></td>';
    echo '<td>' . esc_html__('Displays the full TTS block including title and player.', 'mega-hub') . '</td>';
    echo '</tr>';
    echo '</tbody>';
    echo '</table>';
}


function mega_hub_tts_block_title_render() {
    $options = get_option('mega_hub_options_tts');
    $title = !empty($options['mega_hub_tts_block_title']) ? $options['mega_hub_tts_block_title'] : ''; // Use an empty string as the default value

    echo "<input type='text' name='mega_hub_options_tts[mega_hub_tts_block_title]' value='" . esc_attr($title) . "' placeholder='" . esc_attr__('Enter default title for audio block or leave empty for default', 'mega-hub') . "' class='regular-text' />";
}



function mega_hub_tts_enable_render() {
    $options = get_option('mega_hub_options_tts', []);
    $tts_enable = isset($options['mega_hub_tts_enable']) ? $options['mega_hub_tts_enable'] : 'on';

    echo "<select name='mega_hub_options_tts[mega_hub_tts_enable]'>";
    echo "<option value='on' " . selected($tts_enable, 'on', false) . ">" . esc_html__('On', 'mega-hub') . "</option>";
    echo "<option value='off' " . selected($tts_enable, 'off', false) . ">" . esc_html__('Off', 'mega-hub') . "</option>";
    echo "</select>";
}


function mega_hub_tts_voice_render() {
    $options = get_option('mega_hub_options_tts');
    echo "<select name='mega_hub_options_tts[mega_hub_tts_voice]'>";
    $voices = [
        'alloy' => 'Alloy',
        'echo' => 'Echo',
        'fable' => 'Fable',
        'onyx' => 'Onyx',
        'nova' => 'Nova',
        'shimmer' => 'Shimmer',
    ];
    foreach ($voices as $value => $label) {
        echo "<option value='{$value}' " . selected($options['mega_hub_tts_voice'], $value, false) . ">{$label}</option>";
    }
    echo "</select>";
}



function mega_hub_tts_primary_color_render() {
    $options = get_option('mega_hub_options_tts');
    // Assure-toi que la couleur par défaut est définie si aucune couleur n'est enregistrée
    $color = !empty($options['mega_hub_tts_primary_color']) ? $options['mega_hub_tts_primary_color'] : '#ffffff'; // Utilise le blanc comme couleur par défaut

    // Champ de saisie pour la couleur avec la classe 'color-picker' pour initialiser le sélecteur de couleurs
    echo "<input type='text' name='mega_hub_options_tts[mega_hub_tts_primary_color]' value='" . esc_attr($color) . "' class='color-picker' />";
}



function mega_hub_tts_secondary_color_render() {
    $options = get_option('mega_hub_options_tts');
    // Assure-toi que la couleur par défaut est définie si aucune couleur n'est enregistrée
    $color = !empty($options['mega_hub_tts_secondary_color']) ? $options['mega_hub_tts_secondary_color'] : '#ffffff'; // Utilise le blanc comme couleur par défaut

    // Champ de saisie pour la couleur avec la classe 'color-picker' pour initialiser le sélecteur de couleurs
    echo "<input type='text' name='mega_hub_options_tts[mega_hub_tts_secondary_color]' value='" . esc_attr($color) . "' class='color-picker' />";
}


/* ---------------------------------- IMAGE GENERATION ------------------------------------------*/


function mega_hub_section_dalle_cb() {
    echo '<p>' . esc_html__('Configure Dalle Image Generator settings here.', 'mega-hub') . '</p>';
}

function mega_hub_dalle_enable_render() {
    $options = get_option('mega_hub_options_dalle');
    ?>
    <select name="mega_hub_options_dalle[mega_hub_dalle_enable]">
        <option value="on" <?php selected($options['mega_hub_dalle_enable'], 'on'); ?>><?php _e('On', 'mega-hub'); ?></option>
        <option value="off" <?php selected($options['mega_hub_dalle_enable'], 'off'); ?>><?php _e('Off', 'mega-hub'); ?></option>
    </select>
    <?php
}

function mega_hub_dalle_model_render() {
    $options = get_option('mega_hub_options_dalle');
    ?>
    <select name="mega_hub_options_dalle[mega_hub_dalle_model]">
        <option value="dalle2" <?php selected($options['mega_hub_dalle_model'], 'dalle2'); ?>><?php _e('Dalle 2', 'mega-hub'); ?></option>
        <option value="dalle3" <?php selected($options['mega_hub_dalle_model'], 'dalle3'); ?>><?php _e('Dalle 3', 'mega-hub'); ?></option>
    </select>
    <?php
}


/* ---------------------------------- SEO ------------------------------------------*/


function mega_hub_section_seo_cb() {
    echo '<p>' . esc_html__('Configure Indexer settings here. Enable or disable the Indexer feature as needed.', 'mega-hub') . '</p>';
}


function mega_hub_indexer_enable_render() {
    $options = get_option('mega_hub_options_seo', []);

    $indexer_enable = isset($options['mega_hub_indexer_enable']) ? $options['mega_hub_indexer_enable'] : 'on';

    echo "<select name='mega_hub_options_seo[mega_hub_indexer_enable]'>";
    echo "<option value='on' " . selected($indexer_enable, 'on', false) . ">" . esc_html__('On', 'mega-hub') . "</option>";
    echo "<option value='off' " . selected($indexer_enable, 'off', false) . ">" . esc_html__('Off', 'mega-hub') . "</option>";
    echo "</select>";
}

function mega_hub_structured_data_enable_render() {
    $options = get_option('mega_hub_options_seo', []);

    $structured_data_enable = isset($options['mega_hub_structured_data_enable']) ? $options['mega_hub_structured_data_enable'] : 'on';

    echo "<select name='mega_hub_options_seo[mega_hub_structured_data_enable]'>";
    echo "<option value='on' " . selected($structured_data_enable, 'on', false) . ">" . esc_html__('On', 'mega-hub') . "</option>";
    echo "<option value='off' " . selected($structured_data_enable, 'off', false) . ">" . esc_html__('Off', 'mega-hub') . "</option>";
    echo "</select>";
}




/* ---------------------------------- AUTO BLOGGER ------------------------------------------*/


function mega_hub_section_auto_blogger_cb() {
    echo '<p>' . esc_html__('Configure Auto Blogger settings here. Enable or disable the Auto Blogger feature. Specify internal URLs for automatic linking, one per line, up to 20.', 'mega-hub') . '</p>';
}



function mega_hub_auto_blogger_enable_render() {
    // Récupère les options, ou utilise un tableau vide si rien n'est trouvé
    $options = get_option('mega_hub_options_auto_blogger', []);

    $auto_blogger_enable = isset($options['mega_hub_auto_blogger_enable']) ? $options['mega_hub_auto_blogger_enable'] : 'on';

    // Début du rendu du champ de sélection
    echo "<select name='mega_hub_options_auto_blogger[mega_hub_auto_blogger_enable]'>";
    // Option 'On'
    echo "<option value='on' " . selected($auto_blogger_enable, 'on', false) . ">" . esc_html__('On', 'mega-hub') . "</option>";
    // Option 'Off'
    echo "<option value='off' " . selected($auto_blogger_enable, 'off', false) . ">" . esc_html__('Off', 'mega-hub') . "</option>";
    // Fin du rendu du champ de sélection
    echo "</select>";
}


function mega_hub_auto_blogger_gpt_model_render($select_id = '') {
    $options = get_option('mega_hub_options_auto_blogger');
    // Assure-toi que $select_id est une chaîne
    $select_id_attribute = is_string($select_id) && !empty($select_id) ? "id='{$select_id}'" : '';

    echo "<select {$select_id_attribute} class='model-selection' name='mega_hub_options_auto_blogger[mega_hub_auto_blogger_gpt_model]'>";
    $models = [
        'gpt-4-0125-preview' => 'GPT-4-0125-Preview',
        'gpt-4-1106-preview' => 'GPT-4-1106-Preview',
        'gpt-3.5-turbo-0125' => 'GPT-3.5-Turbo-0125',
        'gpt-4' => 'GPT-4',
        'gemini-1.0' => 'Gemini 1.0',
    ];

    foreach ($models as $value => $label) {
        $selected = isset($options['mega_hub_auto_blogger_gpt_model']) && $options['mega_hub_auto_blogger_gpt_model'] === $value ? 'selected' : '';
        echo "<option value='{$value}' {$selected}>{$label}</option>";
    }
    echo "</select>";
}






function mega_hub_autoblog_internal_urls_render() {
    $options = get_option('mega_hub_options_auto_blogger');
    echo "<textarea id='mega_hub_autoblog_internal_urls' name='mega_hub_options_auto_blogger[mega_hub_autoblog_internal_urls]' rows='20' cols='80' placeholder='example : https://www.mywebsite.com/myurl'>" . esc_textarea($options['mega_hub_autoblog_internal_urls'] ?? '') . "</textarea>";
    echo "<p class='description'>" . esc_html__('Enter each URL on a new line. Use full URLs, not relative paths (e.g., https://www.mywebsite.com/myurl). Limit to 20 URLs.', 'mega-hub') . "</p>";
}

function mega_hub_auto_blogger_affiliate_urls_render() {
    $options = get_option('mega_hub_options_auto_blogger');
    echo "<textarea id='mega_hub_auto_blogger_affiliate_urls' name='mega_hub_options_auto_blogger[mega_hub_auto_blogger_affiliate_urls]' rows='10' cols='80' placeholder='example : https://www.amazon.com/example-affiliate-link'>" . esc_textarea($options['mega_hub_auto_blogger_affiliate_urls'] ?? '') . "</textarea>";
    echo "<p class='description'>" . esc_html__('Enter each affiliate URL on a new line. Use full URLs, not relative paths. Limit to 20 URLs. Leave empty if you do not wish to integrate affiliate options in Auto Blogger.', 'mega-hub') . "</p>";
}


/* ---------------------------------- CONTENT SETTING ------------------------------------------*/



function mega_hub_section_content_tools_cb() {
    echo '<p>' . esc_html__('Enable or disable the Content Tools feature.', 'mega-hub') . '</p>';
}

function mega_hub_content_tools_enable_render() {
    $options = get_option('mega_hub_options_content_tools');
    $isEnabled = isset($options['mega_hub_content_tools_enable']) ? $options['mega_hub_content_tools_enable'] : 'off';

    echo "<select name='mega_hub_options_content_tools[mega_hub_content_tools_enable]'>";
    echo "<option value='on' " . selected($isEnabled, 'on', false) . ">" . esc_html__('On', 'mega-hub') . "</option>";
    echo "<option value='off' " . selected($isEnabled, 'off', false) . ">" . esc_html__('Off', 'mega-hub') . "</option>";
    echo "</select>";
}




/* ---------------------------------- WOOCOMMERCE ------------------------------------------*/


function mega_hub_section_woocommerce_cb() {
    echo '<p>' . esc_html__('Enable or disable integration with WooCommerce.', 'mega-hub') . '</p>';
}

function mega_hub_woocommerce_enable_render() {
    $options = get_option('mega_hub_options_woocommerce');
    ?>
    <select name="mega_hub_options_woocommerce[mega_hub_woocommerce_enable]">
        <option value="on" <?php selected($options['mega_hub_woocommerce_enable'], 'on'); ?>><?php _e('On', 'mega-hub'); ?></option>
        <option value="off" <?php selected($options['mega_hub_woocommerce_enable'], 'off'); ?>><?php _e('Off', 'mega-hub'); ?></option>
    </select>
    <?php
}
