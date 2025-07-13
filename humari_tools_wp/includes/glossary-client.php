<?php
// Sécurité
if (!defined('ABSPATH')) {
    exit;
}

// ================================
// BASE URL CORRECTE POUR GLOSSAIRE
// ================================
define('HUMARI_GLOSSARY_API_BASE', 'https://backoffice.humari.fr/glossaire/');

function humari_glossary_get_categories($params = array()) {
    $api_url = HUMARI_GLOSSARY_API_BASE . 'categories/';
    
    // Ajouter paramètres de requête
    if (!empty($params)) {
        $api_url .= '?' . http_build_query($params);
    }
    
    // Cache de 2h pour les catégories (changent peu)
    $cache_key = 'humari_glossary_categories_' . md5($api_url);
    $cached_data = get_transient($cache_key);
    
    if ($cached_data !== false) {
        return $cached_data;
    }
    
    $response = wp_remote_get($api_url, array(
        'timeout' => 15,
        'headers' => array(
            'User-Agent' => 'Humari WordPress Plugin/1.0.0'
        )
    ));
    
    if (is_wp_error($response)) {
        error_log('Glossary Categories API Error: ' . $response->get_error_message());
        return new WP_Error('api_error', 'Erreur de connexion');
    }
    
    $response_code = wp_remote_retrieve_response_code($response);
    if ($response_code !== 200) {
        error_log('Glossary Categories HTTP Error: ' . $response_code);
        return new WP_Error('api_error', 'Erreur API: ' . $response_code);
    }
    
    $data = json_decode(wp_remote_retrieve_body($response), true);
    
    // Cache 2h
    set_transient($cache_key, $data, 2 * HOUR_IN_SECONDS);
    
    return $data;
}

function humari_glossary_get_category_tree() {
    $api_url = HUMARI_GLOSSARY_API_BASE . 'categories/tree/';
    
    $cache_key = 'humari_glossary_category_tree';
    $cached_data = get_transient($cache_key);
    
    if ($cached_data !== false) {
        return $cached_data;
    }
    
    $response = wp_remote_get($api_url, array(
        'timeout' => 15,
        'headers' => array(
            'User-Agent' => 'Humari WordPress Plugin/1.0.0'
        )
    ));
    
    if (is_wp_error($response)) {
        return new WP_Error('api_error', 'Erreur de connexion');
    }
    
    $data = json_decode(wp_remote_retrieve_body($response), true);
    
    // Cache 2h
    set_transient($cache_key, $data, 2 * HOUR_IN_SECONDS);
    
    return $data;
}

function humari_glossary_get_category_by_slug($slug) {
    $api_url = HUMARI_GLOSSARY_API_BASE . 'categories/by-slug/' . urlencode($slug) . '/';
    
    $cache_key = 'humari_glossary_category_' . $slug;
    $cached_data = get_transient($cache_key);
    
    if ($cached_data !== false) {
        return $cached_data;
    }
    
    $response = wp_remote_get($api_url, array(
        'timeout' => 10,
        'headers' => array(
            'User-Agent' => 'Humari WordPress Plugin/1.0.0'
        )
    ));
    
    if (is_wp_error($response)) {
        return new WP_Error('api_error', 'Erreur de connexion');
    }
    
    $response_code = wp_remote_retrieve_response_code($response);
    if ($response_code === 404) {
        return null;
    } elseif ($response_code !== 200) {
        return new WP_Error('api_error', 'Erreur API: ' . $response_code);
    }
    
    $data = json_decode(wp_remote_retrieve_body($response), true);
    
    // Cache 1h
    set_transient($cache_key, $data, HOUR_IN_SECONDS);
    
    return $data;
}

function humari_glossary_get_terms($params = array()) {
    $api_url = HUMARI_GLOSSARY_API_BASE . 'terms/';
    
    // Paramètres par défaut
    $default_params = array(
        'lang' => 'fr',
        'page_size' => 20
    );
    
    $params = array_merge($default_params, $params);
    $api_url .= '?' . http_build_query($params);
    
    // Cache plus court pour les termes (plus dynamique)
    $cache_key = 'humari_glossary_terms_' . md5($api_url);
    $cached_data = get_transient($cache_key);
    
    if ($cached_data !== false) {
        return $cached_data;
    }
    
    $response = wp_remote_get($api_url, array(
        'timeout' => 15,
        'headers' => array(
            'User-Agent' => 'Humari WordPress Plugin/1.0.0'
        )
    ));
    
    if (is_wp_error($response)) {
        return new WP_Error('api_error', 'Erreur de connexion');
    }
    
    $data = json_decode(wp_remote_retrieve_body($response), true);
    
    // Cache 1h
    set_transient($cache_key, $data, HOUR_IN_SECONDS);
    
    return $data;
}

function humari_glossary_get_term_by_slug($slug, $lang = 'fr', $context = '') {
    $api_url = HUMARI_GLOSSARY_API_BASE . 'terms/by-slug/' . urlencode($slug) . '/';
    
    $params = array('lang' => $lang);
    if (!empty($context)) {
        $params['context'] = $context;
    }
    
    $api_url .= '?' . http_build_query($params);
    
    $cache_key = 'humari_glossary_term_' . $slug . '_' . $lang . '_' . $context;
    $cached_data = get_transient($cache_key);
    
    if ($cached_data !== false) {
        return $cached_data;
    }
    
    $response = wp_remote_get($api_url, array(
        'timeout' => 10,
        'headers' => array(
            'User-Agent' => 'Humari WordPress Plugin/1.0.0'
        )
    ));
    
    if (is_wp_error($response)) {
        return new WP_Error('api_error', 'Erreur de connexion');
    }
    
    $response_code = wp_remote_retrieve_response_code($response);
    if ($response_code === 404) {
        return null;
    } elseif ($response_code !== 200) {
        return new WP_Error('api_error', 'Erreur API: ' . $response_code);
    }
    
    $data = json_decode(wp_remote_retrieve_body($response), true);
    
    // Cache 1h pour les termes individuels
    set_transient($cache_key, $data, HOUR_IN_SECONDS);
    
    return $data;
}

function humari_glossary_search_terms($query, $params = array()) {
    if (empty($query)) {
        return new WP_Error('invalid_query', 'Requête de recherche vide');
    }
    
    $api_url = HUMARI_GLOSSARY_API_BASE . 'terms/search/';
    
    $default_params = array(
        'q' => $query,
        'lang' => 'fr',
        'page_size' => 20
    );
    
    $params = array_merge($default_params, $params);
    $api_url .= '?' . http_build_query($params);
    
    // Cache plus court pour les recherches (30 min)
    $cache_key = 'humari_glossary_search_' . md5($api_url);
    $cached_data = get_transient($cache_key);
    
    if ($cached_data !== false) {
        return $cached_data;
    }
    
    $response = wp_remote_get($api_url, array(
        'timeout' => 15,
        'headers' => array(
            'User-Agent' => 'Humari WordPress Plugin/1.0.0'
        )
    ));
    
    if (is_wp_error($response)) {
        return new WP_Error('api_error', 'Erreur de connexion');
    }
    
    $data = json_decode(wp_remote_retrieve_body($response), true);
    
    // Cache 30min
    set_transient($cache_key, $data, 30 * MINUTE_IN_SECONDS);
    
    return $data;
}

function humari_glossary_get_popular_terms($limit = 10, $lang = 'fr') {
    $api_url = HUMARI_GLOSSARY_API_BASE . 'terms/popular/';
    $api_url .= '?' . http_build_query(array('limit' => $limit, 'lang' => $lang));
    
    $cache_key = 'humari_glossary_popular_' . $limit . '_' . $lang;
    $cached_data = get_transient($cache_key);
    
    if ($cached_data !== false) {
        return $cached_data;
    }
    
    $response = wp_remote_get($api_url, array(
        'timeout' => 10,
        'headers' => array(
            'User-Agent' => 'Humari WordPress Plugin/1.0.0'
        )
    ));
    
    if (is_wp_error($response)) {
        return new WP_Error('api_error', 'Erreur de connexion');
    }
    
    $data = json_decode(wp_remote_retrieve_body($response), true);
    
    // Cache 1h
    set_transient($cache_key, $data, HOUR_IN_SECONDS);
    
    return $data;
}

function humari_glossary_get_essential_terms($category = '', $lang = 'fr') {
    $api_url = HUMARI_GLOSSARY_API_BASE . 'terms/essential/';
    
    $params = array('lang' => $lang);
    if (!empty($category)) {
        $params['category'] = $category;
    }
    
    $api_url .= '?' . http_build_query($params);
    
    $cache_key = 'humari_glossary_essential_' . $category . '_' . $lang;
    $cached_data = get_transient($cache_key);
    
    if ($cached_data !== false) {
        return $cached_data;
    }
    
    $response = wp_remote_get($api_url, array(
        'timeout' => 10,
        'headers' => array(
            'User-Agent' => 'Humari WordPress Plugin/1.0.0'
        )
    ));
    
    if (is_wp_error($response)) {
        return new WP_Error('api_error', 'Erreur de connexion');
    }
    
    $data = json_decode(wp_remote_retrieve_body($response), true);
    
    // Cache 2h
    set_transient($cache_key, $data, 2 * HOUR_IN_SECONDS);
    
    return $data;
}

// ================================
// ACTIONS AJAX POUR RECHERCHE DYNAMIQUE
// ================================

add_action('wp_ajax_humari_glossary_search', 'humari_glossary_ajax_search');
add_action('wp_ajax_nopriv_humari_glossary_search', 'humari_glossary_ajax_search');

function humari_glossary_ajax_search() {
    // Validation
    if (!isset($_GET['q']) || empty($_GET['q'])) {
        wp_send_json_error('Paramètre "q" requis');
        return;
    }
    
    $query = sanitize_text_field($_GET['q']);
    $lang = sanitize_text_field($_GET['lang'] ?? 'fr');
    $category = sanitize_text_field($_GET['category'] ?? '');
    $limit = intval($_GET['limit'] ?? 10);
    
    $params = array(
        'lang' => $lang,
        'page_size' => $limit
    );
    
    if (!empty($category)) {
        $params['category'] = $category;
    }
    
    $results = humari_glossary_search_terms($query, $params);
    
    if (is_wp_error($results)) {
        wp_send_json_error($results->get_error_message());
        return;
    }
    
    wp_send_json_success($results);
}

add_action('wp_ajax_humari_glossary_get_term', 'humari_glossary_ajax_get_term');
add_action('wp_ajax_nopriv_humari_glossary_get_term', 'humari_glossary_ajax_get_term');

function humari_glossary_ajax_get_term() {
    if (!isset($_GET['slug'])) {
        wp_send_json_error('Paramètre "slug" requis');
        return;
    }
    
    $slug = sanitize_text_field($_GET['slug']);
    $lang = sanitize_text_field($_GET['lang'] ?? 'fr');
    $context = sanitize_text_field($_GET['context'] ?? '');
    
    $term = humari_glossary_get_term_by_slug($slug, $lang, $context);
    
    if (is_wp_error($term)) {
        wp_send_json_error($term->get_error_message());
        return;
    }
    
    if (!$term) {
        wp_send_json_error('Terme non trouvé');
        return;
    }
    
    wp_send_json_success($term);
}