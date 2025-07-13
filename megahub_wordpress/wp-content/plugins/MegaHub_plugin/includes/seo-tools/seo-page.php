<?php

function mega_hub_seo_tools_page() {
    $current_tab = isset($_GET['tab']) ? $_GET['tab'] : 'structured-data';
    ?>
    <div class="wrap">
        <h1><?php _e('SEO Tools', 'mega-hub'); ?></h1>
        <h2 class="nav-tab-wrapper">
            <a href="?page=mega-hub-seo-tools&tab=structured-data" class="nav-tab <?php echo $current_tab == 'structured-data' ? 'nav-tab-active' : ''; ?>"><?php _e('Structured Data', 'mega-hub'); ?></a>
            <a href="?page=mega-hub-seo-tools&tab=coming-soon" class="nav-tab <?php echo $current_tab == 'coming-soon' ? 'nav-tab-active' : ''; ?>"><?php _e('Coming Soon', 'mega-hub'); ?></a>
        </h2>

        <div id="structured-data" class="tab-content" style="<?php echo $current_tab == 'structured-data' ? '' : 'display: none;'; ?>">
            <?php mega_hub_structured_data_content(); ?>
        </div>

        <div id="coming-soon" class="tab-content" style="<?php echo $current_tab == 'coming-soon' ? '' : 'display: none;'; ?>">
            <p><?php _e('Coming soon...', 'mega-hub'); ?></p>
        </div>
    </div>
    <?php
}

function mega_hub_seo_structured_data_section_cb() {
    echo '<p>' . __('Fill in the fields below with your structured data information. Only filled fields will be added to your page. Learn how to view structured data on your page', 'mega-hub') . ' <a href="https://humari.fr/structured-data-guide" target="_blank">' . __('here', 'mega-hub') . '</a>.</p>';
}

function mega_hub_structured_data_content() {
    echo '<form method="post" action="options.php">';
    settings_fields('mega_hub_seo_tools_structured_data');
    do_settings_sections('mega_hub_seo_tools_structured_data');
    submit_button();
    echo '</form>';

    echo '<p>' . sprintf(__('Learn how to view structured data on your page <a href="%s" target="_blank">here</a>.', 'mega-hub'), 'https://humari.fr/structured-data-guide') . '</p>';
}

function mega_hub_seo_tools_init() {
    register_setting('mega_hub_seo_tools_structured_data', 'mega_hub_options_seo_structured_data');

    // General Information Section
    add_settings_section(
        'mega_hub_general_information',
        __('General Information', 'mega-hub'),
        'mega_hub_general_information_cb',
        'mega_hub_seo_tools_structured_data'
    );

    // Organization Information Section
    add_settings_section(
        'mega_hub_organization_information',
        __('Organization Information', 'mega-hub'),
        'mega_hub_organization_information_cb',
        'mega_hub_seo_tools_structured_data'
    );

    // Contact Information Section
    add_settings_section(
        'mega_hub_contact_information',
        __('Contact Information', 'mega-hub'),
        'mega_hub_contact_information_cb',
        'mega_hub_seo_tools_structured_data'
    );

    // Add fields to General Information Section
    add_settings_field(
        'mega_hub_schema_type',
        __('Schema Type', 'mega-hub'),
        'mega_hub_schema_type_render',
        'mega_hub_seo_tools_structured_data',
        'mega_hub_general_information'
    );

    // Add fields to Organization Information Section
    add_settings_field(
        'mega_hub_organization_name',
        __('Organization Name', 'mega-hub'),
        'mega_hub_organization_name_render',
        'mega_hub_seo_tools_structured_data',
        'mega_hub_organization_information'
    );

    add_settings_field(
        'mega_hub_organization_url',
        __('Organization URL', 'mega-hub'),
        'mega_hub_organization_url_render',
        'mega_hub_seo_tools_structured_data',
        'mega_hub_organization_information'
    );

    add_settings_field(
        'mega_hub_organization_logo',
        __('Organization Logo URL', 'mega-hub'),
        'mega_hub_organization_logo_render',
        'mega_hub_seo_tools_structured_data',
        'mega_hub_organization_information'
    );

    // Add fields to Contact Information Section
    add_settings_field(
        'mega_hub_contact_type',
        __('Contact Type', 'mega-hub'),
        'mega_hub_contact_type_render',
        'mega_hub_seo_tools_structured_data',
        'mega_hub_contact_information'
    );

    add_settings_field(
        'mega_hub_contact_info',
        __('Contact Information', 'mega-hub'),
        'mega_hub_contact_info_render',
        'mega_hub_seo_tools_structured_data',
        'mega_hub_contact_information'
    );

    // More fields and sections as needed...
}

add_action('admin_init', 'mega_hub_seo_tools_init');

function mega_hub_general_information_cb() {
    echo '<p>' . __('Provide general information about the structured data type you are defining.', 'mega-hub') . '</p>';
}

function mega_hub_organization_information_cb() {
    echo '<p>' . __('Provide detailed information about the organization.', 'mega-hub') . '</p>';
}

function mega_hub_contact_information_cb() {
    echo '<p>' . __('Provide contact information for the organization.', 'mega-hub') . '</p>';
}

function mega_hub_schema_type_render() {
    $options = get_option('mega_hub_options_seo_structured_data');
    $schema_types = ['' => 'Select a Schema Type', 'Organization' => 'Organization', 'Person' => 'Person', 'Event' => 'Event', 'Product' => 'Product', 'Article' => 'Article', 'LocalBusiness' => 'LocalBusiness'];
    echo "<select name='mega_hub_options_seo_structured_data[mega_hub_schema_type]' class='regular-text'>";
    foreach ($schema_types as $value => $label) {
        $selected = (isset($options['mega_hub_schema_type']) && $options['mega_hub_schema_type'] === $value) ? 'selected' : '';
        echo "<option value='$value' $selected>$label</option>";
    }
    echo "</select>";
}

function mega_hub_organization_name_render() {
    $options = get_option('mega_hub_options_seo_structured_data');
    echo "<input type='text' name='mega_hub_options_seo_structured_data[mega_hub_organization_name]' value='" . esc_attr($options['mega_hub_organization_name'] ?? '') . "' class='regular-text' />";
}

function mega_hub_organization_url_render() {
    $options = get_option('mega_hub_options_seo_structured_data');
    echo "<input type='url' name='mega_hub_options_seo_structured_data[mega_hub_organization_url]' value='" . esc_attr($options['mega_hub_organization_url'] ?? '') . "' class='regular-text' />";
}

function mega_hub_organization_logo_render() {
    $options = get_option('mega_hub_options_seo_structured_data');
    echo "<input type='url' name='mega_hub_options_seo_structured_data[mega_hub_organization_logo]' value='" . esc_attr($options['mega_hub_organization_logo'] ?? '') . "' class='regular-text' />";
}

function mega_hub_contact_type_render() {
    $options = get_option('mega_hub_options_seo_structured_data');
    $contact_types = ['' => 'Select a Contact Type', 'customer support' => 'Customer Support', 'technical support' => 'Technical Support', 'billing support' => 'Billing Support', 'bill payment' => 'Bill Payment'];
    echo "<select name='mega_hub_options_seo_structured_data[mega_hub_contact_type]' class='regular-text'>";
    foreach ($contact_types as $value => $label) {
        $selected = (isset($options['mega_hub_contact_type']) && $options['mega_hub_contact_type'] === $value) ? 'selected' : '';
        echo "<option value='$value' $selected>$label</option>";
    }
    echo "</select>";
}

function mega_hub_contact_info_render() {
    $options = get_option('mega_hub_options_seo_structured_data');
    echo "<input type='text' name='mega_hub_options_seo_structured_data[mega_hub_contact_info]' value='" . esc_attr($options['mega_hub_contact_info'] ?? '') . "' class='regular-text' />";
}

