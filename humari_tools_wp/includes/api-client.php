<?php
// Sécurité
if (!defined('ABSPATH')) {
    exit;
}

function humari_tools_get_tool_html($category, $tool) {
    // Construction de l'URL de l'API
    $api_url = HUMARI_TOOLS_API_BASE . $category . '/' . $tool . '/render/';
    
    // Cache de 5 minutes pour éviter les appels répétés
    $cache_key = 'humari_tool_' . $category . '_' . $tool;
    $cached_html = get_transient($cache_key);
    
    if ($cached_html !== false) {
        return $cached_html;
    }
    
    // Appel vers Django
    $response = wp_remote_get($api_url, array(
        'timeout' => 10,
        'headers' => array(
            'User-Agent' => 'Humari WordPress Plugin/1.0.0'
        )
    ));
    
    if (is_wp_error($response)) {
        error_log('Humari Tools API Error: ' . $response->get_error_message());
        return $response;
    }
    
    $response_code = wp_remote_retrieve_response_code($response);
    if ($response_code !== 200) {
        error_log('Humari Tools API HTTP Error: ' . $response_code);
        return new WP_Error('api_error', 'Erreur API: ' . $response_code);
    }
    
    $html_content = wp_remote_retrieve_body($response);
    
    // Mise en cache
    set_transient($cache_key, $html_content, 5 * MINUTE_IN_SECONDS);
    
    return $html_content;
}

function humari_tools_handle_form_submission($html_content, $tool_atts) {
    // Vérifier si c'est une soumission de formulaire pour cet outil
    if ($_SERVER['REQUEST_METHOD'] !== 'POST' || 
        !isset($_POST['megahub_action'])) {
        return $html_content;
    }
    
    // Traitement selon l'outil
    $action = sanitize_text_field($_POST['megahub_action']);
    
    switch ($action) {
        case 'convert':
            return humari_tools_process_conversion($html_content);
        case 'shorten':
            return humari_tools_process_url_shortening($html_content);
        case 'simulate':
            return humari_tools_process_simulation($html_content);
        case 'optimize':
            return humari_tools_process_optimization($html_content);
        case 'calculate_roas':  // ← NOUVEAU AJOUT
            return humari_tools_process_roas_calculation($html_content);
        default:
            return $html_content;
    }
}

function humari_tools_process_conversion($original_html) {
    // URL de traitement server-side
    $api_url = HUMARI_TOOLS_API_BASE . 'document/converter/process-server/';
    
    // Récupérer les fichiers - SUPPORT MULTIPLE FILES
    $files = [];
    
    // Vérifier si on a des fichiers multiples
    if (isset($_FILES['files']) && is_array($_FILES['files']['name'])) {
        // Multiple files
        for ($i = 0; $i < count($_FILES['files']['name']); $i++) {
            if ($_FILES['files']['error'][$i] === UPLOAD_ERR_OK) {
                $files[] = [
                    'name' => $_FILES['files']['name'][$i],
                    'type' => $_FILES['files']['type'][$i],
                    'tmp_name' => $_FILES['files']['tmp_name'][$i],
                    'size' => $_FILES['files']['size'][$i]
                ];
            }
        }
    } elseif (isset($_FILES['file']) && $_FILES['file']['error'] === UPLOAD_ERR_OK) {
        // Single file
        $files[] = [
            'name' => $_FILES['file']['name'],
            'type' => $_FILES['file']['type'],
            'tmp_name' => $_FILES['file']['tmp_name'],
            'size' => $_FILES['file']['size']
        ];
    }
    
    if (empty($files)) {
        return $original_html . '<div class="conversion-error">❌ Aucun fichier reçu</div>';
    }
    
    if (!isset($_POST['target_format']) || empty($_POST['target_format'])) {
        return $original_html . '<div class="conversion-error">❌ Format de sortie requis</div>';
    }
    
    $target_format = sanitize_text_field($_POST['target_format']);
    
    // Préparer les données pour l'API Django avec support multiple files
    $boundary = wp_generate_password(24, false);
    $body = '';
    
    // Ajouter chaque fichier
    foreach ($files as $index => $file) {
        $body .= "--{$boundary}\r\n";
        $body .= "Content-Disposition: form-data; name=\"files[]\"; filename=\"{$file['name']}\"\r\n";
        $body .= "Content-Type: {$file['type']}\r\n\r\n";
        $body .= file_get_contents($file['tmp_name']) . "\r\n";
    }
    
    // Ajouter le format
    $body .= "--{$boundary}\r\n";
    $body .= "Content-Disposition: form-data; name=\"target_format\"\r\n\r\n";
    $body .= $target_format . "\r\n";
    $body .= "--{$boundary}--\r\n";
    
    // Appel vers Django
    $response = wp_remote_post($api_url, array(
        'timeout' => 60,
        'body' => $body,
        'headers' => array(
            'Content-Type' => 'multipart/form-data; boundary=' . $boundary
        )
    ));
    
    if (is_wp_error($response)) {
        error_log('Conversion error: ' . $response->get_error_message());
        return $original_html . '<div class="conversion-error">❌ Erreur de connexion</div>';
    }
    
    $result_html = wp_remote_retrieve_body($response);
    
    // Retourner le HTML original + le résultat
    return $original_html . $result_html;
}

function humari_tools_process_url_shortening($original_html) {
    // URL de traitement server-side
    $api_url = HUMARI_TOOLS_API_BASE . 'web/shortener/process-server/';
    
    // Récupérer l'URL depuis POST
    if (!isset($_POST['url']) || empty($_POST['url'])) {
        return $original_html . '<div class="shortener-error">❌ URL requise</div>';
    }
    
    $url = sanitize_url($_POST['url']);
    
    // Validation basique côté WordPress
    if (!filter_var($url, FILTER_VALIDATE_URL)) {
        return $original_html . '<div class="shortener-error">❌ Format d\'URL invalide</div>';
    }
    
    // Préparer les données pour Django
    $body_data = array(
        'url' => $url
    );
    
    // Appel vers Django
    $response = wp_remote_post($api_url, array(
        'timeout' => 15,
        'body' => $body_data,
        'headers' => array(
            'User-Agent' => 'Humari WordPress Plugin/1.0.0'
        )
    ));
    
    if (is_wp_error($response)) {
        error_log('URL Shortening error: ' . $response->get_error_message());
        return $original_html . '<div class="shortener-error">❌ Erreur de connexion</div>';
    }
    
    $response_code = wp_remote_retrieve_response_code($response);
    if ($response_code !== 200) {
        error_log('URL Shortening HTTP Error: ' . $response_code);
        return $original_html . '<div class="shortener-error">❌ Erreur du serveur (' . $response_code . ')</div>';
    }
    
    $result_html = wp_remote_retrieve_body($response);
    
    // Retourner le HTML original + le résultat
    return $original_html . $result_html;
}

function humari_tools_process_optimization($original_html) {
    // URL de traitement server-side
    $api_url = HUMARI_TOOLS_API_BASE . 'file/optimizer/process-server/';
    
    // Récupérer le fichier
    if (!isset($_FILES['file']) || $_FILES['file']['error'] !== UPLOAD_ERR_OK) {
        return $original_html . '<div class="optimization-error">❌ Aucun fichier reçu</div>';
    }
    
    $file = $_FILES['file'];
    
    // Validation basique
    $allowed_types = array('image/jpeg', 'image/jpg', 'image/png', 'image/webp', 'application/pdf');
    if (!in_array($file['type'], $allowed_types)) {
        return $original_html . '<div class="optimization-error">❌ Type de fichier non supporté</div>';
    }
    
    // Taille max 10MB pour le public
    if ($file['size'] > 10 * 1024 * 1024) {
        return $original_html . '<div class="optimization-error">❌ Fichier trop volumineux (max 10MB)</div>';
    }
    
    // Récupérer les paramètres d'optimisation
    $quality_level = sanitize_text_field($_POST['quality_level'] ?? 'medium');
    $resize_enabled = isset($_POST['resize_enabled']) ? 'true' : 'false';
    $target_max_dimension = !empty($_POST['target_max_dimension']) ? 
        intval($_POST['target_max_dimension']) : null;
    
    // Préparer les données pour l'API Django
    $boundary = wp_generate_password(24, false);
    $body = '';
    
    // Ajouter le fichier
    $body .= "--{$boundary}\r\n";
    $body .= "Content-Disposition: form-data; name=\"file\"; filename=\"{$file['name']}\"\r\n";
    $body .= "Content-Type: {$file['type']}\r\n\r\n";
    $body .= file_get_contents($file['tmp_name']) . "\r\n";
    
    // Ajouter les paramètres
    $body .= "--{$boundary}\r\n";
    $body .= "Content-Disposition: form-data; name=\"quality_level\"\r\n\r\n";
    $body .= $quality_level . "\r\n";
    
    $body .= "--{$boundary}\r\n";
    $body .= "Content-Disposition: form-data; name=\"resize_enabled\"\r\n\r\n";
    $body .= $resize_enabled . "\r\n";
    
    if ($target_max_dimension) {
        $body .= "--{$boundary}\r\n";
        $body .= "Content-Disposition: form-data; name=\"target_max_dimension\"\r\n\r\n";
        $body .= $target_max_dimension . "\r\n";
    }
    
    $body .= "--{$boundary}--\r\n";
    
    // Appel vers Django
    $response = wp_remote_post($api_url, array(
        'timeout' => 60,
        'body' => $body,
        'headers' => array(
            'Content-Type' => 'multipart/form-data; boundary=' . $boundary
        )
    ));
    
    if (is_wp_error($response)) {
        error_log('Optimization error: ' . $response->get_error_message());
        return $original_html . '<div class="optimization-error">❌ Erreur de connexion</div>';
    }
    
    $response_code = wp_remote_retrieve_response_code($response);
    if ($response_code !== 200) {
        error_log('Optimization HTTP Error: ' . $response_code);
        return $original_html . '<div class="optimization-error">❌ Erreur du serveur (' . $response_code . ')</div>';
    }
    
    $result_html = wp_remote_retrieve_body($response);
    
    // Retourner le HTML original + le résultat
    return $original_html . $result_html;
}

function humari_tools_process_simulation($original_html) {
    // TODO: Implémenter le simulateur immobilier
    return $original_html . '<div class="simulation-info">🏠 Simulateur immobilier - à implémenter</div>';
}

// ================================
// NOUVEAU : TRAITEMENT ROAS
// ================================

function humari_tools_process_roas_calculation($original_html) {
    // Le calculateur ROAS fonctionne principalement côté client
    // Cette fonction est optionnelle pour validation côté serveur
    
    if (!isset($_POST['calculation_data'])) {
        return $original_html . '<div class="roas-error">❌ Données de calcul manquantes</div>';
    }
    
    $calculation_data = json_decode(stripslashes($_POST['calculation_data']), true);
    
    if (!$calculation_data) {
        return $original_html . '<div class="roas-error">❌ Format de données invalide</div>';
    }
    
    // URL de validation côté serveur Django
    $api_url = HUMARI_TOOLS_API_BASE . 'ecommerce/roas-calculator/process/';
    
    // Appel vers Django pour validation
    $response = wp_remote_post($api_url, array(
        'timeout' => 15,
        'body' => json_encode($calculation_data),
        'headers' => array(
            'Content-Type' => 'application/json',
            'User-Agent' => 'Humari WordPress Plugin/1.0.0'
        )
    ));
    
    if (is_wp_error($response)) {
        error_log('ROAS Calculation error: ' . $response->get_error_message());
        return $original_html . '<div class="roas-error">❌ Erreur de connexion</div>';
    }
    
    $response_code = wp_remote_retrieve_response_code($response);
    if ($response_code !== 200) {
        error_log('ROAS Calculation HTTP Error: ' . $response_code);
        return $original_html . '<div class="roas-error">❌ Erreur du serveur (' . $response_code . ')</div>';
    }
    
    $result_html = wp_remote_retrieve_body($response);
    
    // Retourner le HTML original + le résultat validé
    return $original_html . '<div class="roas-server-validation">' . $result_html . '</div>';
}

// ================================
// ACTIONS AJAX POUR CONVERSIONS
// ================================

add_action('wp_ajax_humari_process_conversion', 'humari_tools_ajax_process_conversion');
add_action('wp_ajax_nopriv_humari_process_conversion', 'humari_tools_ajax_process_conversion');

function humari_tools_ajax_process_conversion() {
    // Validation
    if (!isset($_FILES) || empty($_FILES)) {
        wp_send_json_error('No files uploaded');
        return;
    }
    
    if (!isset($_POST['target_format']) || empty($_POST['target_format'])) {
        wp_send_json_error('Missing target format');
        return;
    }
    
    $target_format = sanitize_text_field($_POST['target_format']);
    $api_url = HUMARI_TOOLS_API_BASE . 'document/converter/process/';
    
    // Récupérer le fichier (pour l'instant on fait du single file)
    $file_key = 'file';
    if (!isset($_FILES[$file_key]) || $_FILES[$file_key]['error'] !== UPLOAD_ERR_OK) {
        wp_send_json_error('File upload error');
        return;
    }
    
    $file = $_FILES[$file_key];
    
    // Préparer la requête multipart pour Django
    $boundary = wp_generate_password(24, false);
    $body = '';
    
    // Ajouter le fichier
    $body .= "--{$boundary}\r\n";
    $body .= "Content-Disposition: form-data; name=\"file\"; filename=\"{$file['name']}\"\r\n";
    $body .= "Content-Type: {$file['type']}\r\n\r\n";
    $body .= file_get_contents($file['tmp_name']) . "\r\n";
    
    // Ajouter le format
    $body .= "--{$boundary}\r\n";
    $body .= "Content-Disposition: form-data; name=\"target_format\"\r\n\r\n";
    $body .= $target_format . "\r\n";
    $body .= "--{$boundary}--\r\n";
    
    // Appel vers Django
    $response = wp_remote_post($api_url, array(
        'timeout' => 60,
        'body' => $body,
        'headers' => array(
            'Content-Type' => 'multipart/form-data; boundary=' . $boundary
        )
    ));
    
    if (is_wp_error($response)) {
        wp_send_json_error('Connection failed: ' . $response->get_error_message());
        return;
    }
    
    $response_code = wp_remote_retrieve_response_code($response);
    if ($response_code !== 201) {
        $body = wp_remote_retrieve_body($response);
        $data = json_decode($body, true);
        wp_send_json_error('API Error: ' . ($data['error'] ?? 'Unknown error'));
        return;
    }
    
    $data = json_decode(wp_remote_retrieve_body($response), true);
    wp_send_json_success($data);
}

add_action('wp_ajax_humari_conversion_status', 'humari_tools_ajax_status');
add_action('wp_ajax_nopriv_humari_conversion_status', 'humari_tools_ajax_status');

function humari_tools_ajax_status() {
    // Validation
    if (!isset($_GET['conversion_id'])) {
        wp_send_json_error('Missing conversion_id');
        return;
    }
    
    $conversion_id = sanitize_text_field($_GET['conversion_id']);
    
    // Call vers Django (pas de throttling côté serveur)
    $api_url = HUMARI_TOOLS_API_BASE . 'document/status/' . $conversion_id . '/';
    
    $response = wp_remote_get($api_url, array(
        'timeout' => 10,
        'headers' => array(
            'User-Agent' => 'Humari WordPress Plugin/1.0.0'
        )
    ));
    
    if (is_wp_error($response)) {
        wp_send_json_error('Connection failed');
        return;
    }
    
    $response_code = wp_remote_retrieve_response_code($response);
    if ($response_code !== 200) {
        wp_send_json_error('API Error: ' . $response_code);
        return;
    }
    
    $data = json_decode(wp_remote_retrieve_body($response), true);
    wp_send_json_success($data);
}

add_action('wp_ajax_humari_download_file', 'humari_tools_ajax_download');  
add_action('wp_ajax_nopriv_humari_download_file', 'humari_tools_ajax_download');

function humari_tools_ajax_download() {
    if (!isset($_GET['token'])) {
        wp_die('Missing token');
        return;
    }
    
    $token = sanitize_text_field($_GET['token']);
    $download_url = HUMARI_TOOLS_API_BASE . 'document/download/' . $token . '/';
    
    // Proxy du téléchargement
    $response = wp_remote_get($download_url, array(
        'timeout' => 30,
        'headers' => array(
            'User-Agent' => 'Humari WordPress Plugin/1.0.0'
        )
    ));
    
    if (is_wp_error($response)) {
        wp_die('Download failed');
        return;
    }
    
    $content = wp_remote_retrieve_body($response);
    $headers = wp_remote_retrieve_headers($response);
    
    // Récupérer les headers originaux
    if (isset($headers['content-disposition'])) {
        header('Content-Disposition: ' . $headers['content-disposition']);
    }
    if (isset($headers['content-type'])) {
        header('Content-Type: ' . $headers['content-type']);
    }
    if (isset($headers['content-length'])) {
        header('Content-Length: ' . $headers['content-length']);
    }
    
    echo $content;
    exit;
}

// ================================
// ACTIONS AJAX POUR SHORTENER
// ================================

add_action('wp_ajax_humari_process_shortening', 'humari_tools_ajax_process_shortening');
add_action('wp_ajax_nopriv_humari_process_shortening', 'humari_tools_ajax_process_shortening');

function humari_tools_ajax_process_shortening() {
    // Validation
    if (!isset($_POST['url']) || empty($_POST['url'])) {
        wp_send_json_error('Missing URL');
        return;
    }
    
    $url = sanitize_url($_POST['url']);
    
    // Validation basique
    if (!filter_var($url, FILTER_VALIDATE_URL)) {
        wp_send_json_error('Invalid URL format');
        return;
    }
    
    $api_url = HUMARI_TOOLS_API_BASE . 'web/shortener/process/';
    
    // Appel vers Django API (JSON)
    $response = wp_remote_post($api_url, array(
        'timeout' => 15,
        'body' => json_encode(array('url' => $url)),
        'headers' => array(
            'Content-Type' => 'application/json',
            'User-Agent' => 'Humari WordPress Plugin/1.0.0'
        )
    ));
    
    if (is_wp_error($response)) {
        wp_send_json_error('Connection failed: ' . $response->get_error_message());
        return;
    }
    
    $response_code = wp_remote_retrieve_response_code($response);
    if ($response_code !== 201) {
        $body = wp_remote_retrieve_body($response);
        $data = json_decode($body, true);
        wp_send_json_error('API Error: ' . ($data['error'] ?? 'Unknown error'));
        return;
    }
    
    $data = json_decode(wp_remote_retrieve_body($response), true);
    wp_send_json_success($data);
}

// ================================
// ACTIONS AJAX POUR OPTIMIZER
// ================================

add_action('wp_ajax_humari_process_optimization', 'humari_tools_ajax_process_optimization');
add_action('wp_ajax_nopriv_humari_process_optimization', 'humari_tools_ajax_process_optimization');

function humari_tools_ajax_process_optimization() {
    // Validation
    if (!isset($_FILES['file']) || $_FILES['file']['error'] !== UPLOAD_ERR_OK) {
        wp_send_json_error('No file uploaded');
        return;
    }
    
    $file = $_FILES['file'];
    
    // Validation du type de fichier
    $allowed_types = array('image/jpeg', 'image/jpg', 'image/png', 'image/webp', 'application/pdf');
    if (!in_array($file['type'], $allowed_types)) {
        wp_send_json_error('Unsupported file type');
        return;
    }
    
    // Validation de la taille (max 10MB pour public)
    if ($file['size'] > 10 * 1024 * 1024) {
        wp_send_json_error('File too large (max 10MB)');
        return;
    }
    
    $api_url = HUMARI_TOOLS_API_BASE . 'file/optimizer/process/';
    
    // ✅ AJOUT DE DEBUG
    error_log('WordPress: Calling Django API: ' . $api_url);
    error_log('WordPress: File received: ' . $file['name'] . ' (' . $file['size'] . ' bytes)');
    
    // Récupérer les paramètres
    $quality_level = sanitize_text_field($_POST['quality_level'] ?? 'medium');
    $resize_enabled = isset($_POST['resize_enabled']) ? 'true' : 'false';
    $target_max_dimension = !empty($_POST['target_max_dimension']) ? 
        intval($_POST['target_max_dimension']) : null;
    
    // Préparer la requête multipart pour Django
    $boundary = wp_generate_password(24, false);
    $body = '';
    
    // Ajouter le fichier
    $body .= "--{$boundary}\r\n";
    $body .= "Content-Disposition: form-data; name=\"file\"; filename=\"{$file['name']}\"\r\n";
    $body .= "Content-Type: {$file['type']}\r\n\r\n";
    $body .= file_get_contents($file['tmp_name']) . "\r\n";
    
    // Ajouter les paramètres
    $body .= "--{$boundary}\r\n";
    $body .= "Content-Disposition: form-data; name=\"quality_level\"\r\n\r\n";
    $body .= $quality_level . "\r\n";
    
    $body .= "--{$boundary}\r\n";
    $body .= "Content-Disposition: form-data; name=\"resize_enabled\"\r\n\r\n";
    $body .= $resize_enabled . "\r\n";
    
    if ($target_max_dimension) {
        $body .= "--{$boundary}\r\n";
        $body .= "Content-Disposition: form-data; name=\"target_max_dimension\"\r\n\r\n";
        $body .= $target_max_dimension . "\r\n";
    }
    
    $body .= "--{$boundary}--\r\n";
    
    // Appel vers Django
    $response = wp_remote_post($api_url, array(
        'timeout' => 60,
        'body' => $body,
        'headers' => array(
            'Content-Type' => 'multipart/form-data; boundary=' . $boundary
        )
    ));
    
    if (is_wp_error($response)) {
        error_log('WordPress: Connection failed: ' . $response->get_error_message());
        wp_send_json_error('Connection failed: ' . $response->get_error_message());
        return;
    }
    
    $response_code = wp_remote_retrieve_response_code($response);
    $body_response = wp_remote_retrieve_body($response);
    
    // ✅ CORRECTION : Accepter 200 ET 201
    if (!in_array($response_code, [200, 201])) {
        error_log('WordPress: Django returned status: ' . $response_code);
        error_log('WordPress: Django response body: ' . $body_response);
        
        $data = json_decode($body_response, true);
        wp_send_json_error('API Error (' . $response_code . '): ' . ($data['error'] ?? 'Unknown error'));
        return;
    }
    
    $data = json_decode($body_response, true);
    
    // ✅ AJOUT DE VALIDATION DE LA RÉPONSE
    if (!$data || !isset($data['optimization_id'])) {
        error_log('WordPress: Invalid Django response format: ' . $body_response);
        wp_send_json_error('Invalid response format from server');
        return;
    }
    
    error_log('WordPress: Success! Optimization ID: ' . $data['optimization_id']);
    wp_send_json_success($data);
}

add_action('wp_ajax_humari_optimization_status', 'humari_tools_ajax_optimization_status');
add_action('wp_ajax_nopriv_humari_optimization_status', 'humari_tools_ajax_optimization_status');

function humari_tools_ajax_optimization_status() {
    // Validation
    if (!isset($_POST['optimization_id'])) {
        wp_send_json_error('Missing optimization_id');
        return;
    }
    
    $optimization_id = sanitize_text_field($_POST['optimization_id']);
    
    // Call vers Django
    $api_url = HUMARI_TOOLS_API_BASE . 'file/optimizer/status/' . $optimization_id . '/';
    
    $response = wp_remote_get($api_url, array(
        'timeout' => 10,
        'headers' => array(
            'User-Agent' => 'Humari WordPress Plugin/1.0.0'
        )
    ));
    
    if (is_wp_error($response)) {
        wp_send_json_error('Connection failed');
        return;
    }
    
    $response_code = wp_remote_retrieve_response_code($response);
    if ($response_code !== 200) {
        wp_send_json_error('API Error: ' . $response_code);
        return;
    }
    
    $data = json_decode(wp_remote_retrieve_body($response), true);
    wp_send_json_success($data);
}

add_action('wp_ajax_humari_download_optimized', 'humari_tools_ajax_download_optimized');  
add_action('wp_ajax_nopriv_humari_download_optimized', 'humari_tools_ajax_download_optimized');

function humari_tools_ajax_download_optimized() {
    if (!isset($_GET['token'])) {
        wp_die('Missing token');
        return;
    }
    
    $token = sanitize_text_field($_GET['token']);
    $download_url = HUMARI_TOOLS_API_BASE . 'file/optimizer/download/' . $token . '/';
    
    // Proxy du téléchargement
    $response = wp_remote_get($download_url, array(
        'timeout' => 30,
        'headers' => array(
            'User-Agent' => 'Humari WordPress Plugin/1.0.0'
        )
    ));
    
    if (is_wp_error($response)) {
        wp_die('Download failed');
        return;
    }
    
    $content = wp_remote_retrieve_body($response);
    $headers = wp_remote_retrieve_headers($response);
    
    // Récupérer les headers originaux
    if (isset($headers['content-disposition'])) {
        header('Content-Disposition: ' . $headers['content-disposition']);
    }
    if (isset($headers['content-type'])) {
        header('Content-Type: ' . $headers['content-type']);
    }
    if (isset($headers['content-length'])) {
        header('Content-Length: ' . $headers['content-length']);
    }
    
    echo $content;
    exit;
}

// ================================
// NOUVEAU : ACTIONS AJAX POUR CALCULATEUR ROAS
// ================================

add_action('wp_ajax_humari_process_roas_calculation', 'humari_tools_ajax_process_roas');
add_action('wp_ajax_nopriv_humari_process_roas_calculation', 'humari_tools_ajax_process_roas');

function humari_tools_ajax_process_roas() {
    // Validation
    if (!isset($_POST['calculation_data'])) {
        wp_send_json_error('Missing calculation data');
        return;
    }
    
    $calculation_data = json_decode(stripslashes($_POST['calculation_data']), true);
    
    if (!$calculation_data) {
        wp_send_json_error('Invalid calculation data format');
        return;
    }
    
    $api_url = HUMARI_TOOLS_API_BASE . 'ecommerce/roas-calculator/process/';
    
    // Appel vers Django API pour validation/calcul côté serveur
    $response = wp_remote_post($api_url, array(
        'timeout' => 15,
        'body' => json_encode($calculation_data),
        'headers' => array(
            'Content-Type' => 'application/json',
            'User-Agent' => 'Humari WordPress Plugin/1.0.0'
        )
    ));
    
    if (is_wp_error($response)) {
        wp_send_json_error('Connection failed: ' . $response->get_error_message());
        return;
    }
    
    $response_code = wp_remote_retrieve_response_code($response);
    if ($response_code !== 200) {
        $body = wp_remote_retrieve_body($response);
        $data = json_decode($body, true);
        wp_send_json_error('API Error: ' . ($data['error'] ?? 'Unknown error'));
        return;
    }
    
    $data = json_decode(wp_remote_retrieve_body($response), true);
    wp_send_json_success($data);
}

add_action('wp_ajax_humari_export_roas_scenario', 'humari_tools_ajax_export_roas');
add_action('wp_ajax_nopriv_humari_export_roas_scenario', 'humari_tools_ajax_export_roas');

function humari_tools_ajax_export_roas() {
    // Validation
    if (!isset($_POST['scenario_data'])) {
        wp_send_json_error('Missing scenario data');
        return;
    }
    
    $scenario_data = json_decode(stripslashes($_POST['scenario_data']), true);
    $export_format = sanitize_text_field($_POST['format'] ?? 'json');
    
    if (!$scenario_data) {
        wp_send_json_error('Invalid scenario data format');
        return;
    }
    
    $api_url = HUMARI_TOOLS_API_BASE . 'ecommerce/roas-calculator/export/';
    
    // Appel vers Django pour export
    $response = wp_remote_post($api_url, array(
        'timeout' => 30,
        'body' => json_encode(array(
            'scenario_data' => $scenario_data,
            'format' => $export_format
        )),
        'headers' => array(
            'Content-Type' => 'application/json',
            'User-Agent' => 'Humari WordPress Plugin/1.0.0'
        )
    ));
    
    if (is_wp_error($response)) {
        wp_send_json_error('Export failed: ' . $response->get_error_message());
        return;
    }
    
    $response_code = wp_remote_retrieve_response_code($response);
    if ($response_code !== 200) {
        wp_send_json_error('Export Error: ' . $response_code);
        return;
    }
    
    $data = json_decode(wp_remote_retrieve_body($response), true);
    wp_send_json_success($data);
}