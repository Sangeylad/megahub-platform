<?php
// Sécurité
if (!defined('ABSPATH')) {
    exit;
}

// Ajouter le shortcode de rappel
add_shortcode('humari_glossary_recall', 'humari_glossary_recall_shortcode');

function humari_glossary_recall_shortcode($atts) {
    $atts = shortcode_atts(array(
        'term' => '',                    // Slug du terme (obligatoire)
        'link' => 'dofollow',           // dofollow/nofollow/none
        'style' => 'block',             // block/inline/tooltip/card
        'definition_length' => '100',    // Nombre de caractères de la définition
        'show_category' => 'true',       // Afficher la catégorie
        'custom_text' => '',             // Texte personnalisé pour le lien
        'css_class' => ''                // Classes CSS additionnelles
    ), $atts);
    
    if (empty($atts['term'])) {
        return '<div class="glossary-error">⚠️ Paramètre "term" requis</div>';
    }
    
    // Récupérer le terme depuis l'API
    $term = humari_glossary_get_term_by_slug($atts['term']);
    
    if (is_wp_error($term) || !$term) {
        return '<div class="glossary-error">❌ Terme "' . esc_html($atts['term']) . '" non trouvé</div>';
    }
    
    // Construction du lien
    $term_url = '/glossaire/' . $term['category']['slug'] . '/' . $term['slug'] . '/';
    $link_attributes = '';
    
    switch ($atts['link']) {
        case 'nofollow':
            $link_attributes = ' rel="nofollow"';
            break;
        case 'dofollow':
            $link_attributes = '';
            break;
        case 'none':
            $term_url = '#';
            $link_attributes = ' onclick="return false;" style="cursor: default;"';
            break;
    }
    
    // Texte du lien
    $link_text = !empty($atts['custom_text']) ? $atts['custom_text'] : $term['title'];
    
    // Définition tronquée
    $definition = wp_trim_words($term['definition'], ceil($atts['definition_length'] / 6));
    
    // Classes CSS
    $css_classes = 'humari-glossary-recall style-' . esc_attr($atts['style']);
    if (!empty($atts['css_class'])) {
        $css_classes .= ' ' . esc_attr($atts['css_class']);
    }
    
    // Rendu selon le style
    switch ($atts['style']) {
        case 'inline':
            return humari_glossary_recall_inline($term, $term_url, $link_text, $link_attributes, $definition, $css_classes, $atts);
        case 'tooltip':
            return humari_glossary_recall_tooltip($term, $term_url, $link_text, $link_attributes, $definition, $css_classes, $atts);
        case 'card':
            return humari_glossary_recall_card($term, $term_url, $link_text, $link_attributes, $definition, $css_classes, $atts);
        default: // block
            return humari_glossary_recall_block($term, $term_url, $link_text, $link_attributes, $definition, $css_classes, $atts);
    }
}

function humari_glossary_recall_block($term, $term_url, $link_text, $link_attributes, $definition, $css_classes, $atts) {
    $html = '<div class="' . $css_classes . '">';
    $html .= '<div class="recall-header">';
    $html .= '<h4 class="recall-title">';
    
    if ($atts['link'] !== 'none') {
        $html .= '<a href="' . esc_url($term_url) . '"' . $link_attributes . '>';
    }
    
    $html .= '💡 ' . esc_html($link_text);
    
    if ($atts['link'] !== 'none') {
        $html .= '</a>';
    }
    
    $html .= '</h4>';
    
    // Badge catégorie
    if ($atts['show_category'] === 'true') {
        $html .= '<span class="recall-category">' . esc_html($term['category']['name']) . '</span>';
    }
    
    $html .= '</div>';
    
    $html .= '<div class="recall-definition">';
    $html .= esc_html($definition);
    $html .= '</div>';
    
    // Lien "En savoir plus" si pas de lien principal
    if ($atts['link'] === 'none') {
        $html .= '<div class="recall-footer">';
        $html .= '<a href="' . esc_url($term_url) . '" class="recall-more">En savoir plus →</a>';
        $html .= '</div>';
    }
    
    $html .= '</div>';
    
    return $html;
}

function humari_glossary_recall_inline($term, $term_url, $link_text, $link_attributes, $definition, $css_classes, $atts) {
    $html = '<span class="' . $css_classes . '">';
    
    if ($atts['link'] !== 'none') {
        $html .= '<a href="' . esc_url($term_url) . '"' . $link_attributes . ' class="recall-link" title="' . esc_attr($definition) . '">';
    }
    
    $html .= '<strong>' . esc_html($link_text) . '</strong>';
    
    if ($atts['link'] !== 'none') {
        $html .= '</a>';
    }
    
    $html .= '</span>';
    
    return $html;
}

function humari_glossary_recall_tooltip($term, $term_url, $link_text, $link_attributes, $definition, $css_classes, $atts) {
    $html = '<span class="' . $css_classes . '" data-tooltip="' . esc_attr($definition) . '">';
    
    if ($atts['link'] !== 'none') {
        $html .= '<a href="' . esc_url($term_url) . '"' . $link_attributes . ' class="recall-tooltip-link">';
    }
    
    $html .= '<span class="recall-tooltip-text">' . esc_html($link_text) . '</span>';
    $html .= '<span class="recall-tooltip-icon">ℹ️</span>';
    
    if ($atts['link'] !== 'none') {
        $html .= '</a>';
    }
    
    $html .= '<div class="recall-tooltip-content">';
    $html .= '<div class="tooltip-definition">' . esc_html($definition) . '</div>';
    
    if ($atts['show_category'] === 'true') {
        $html .= '<div class="tooltip-category">Catégorie: ' . esc_html($term['category']['name']) . '</div>';
    }
    
    if ($atts['link'] !== 'none') {
        $html .= '<div class="tooltip-link"><a href="' . esc_url($term_url) . '"' . $link_attributes . '>Voir la définition complète →</a></div>';
    }
    
    $html .= '</div>';
    $html .= '</span>';
    
    return $html;
}

function humari_glossary_recall_card($term, $term_url, $link_text, $link_attributes, $definition, $css_classes, $atts) {
    $html = '<div class="' . $css_classes . '">';
    $html .= '<div class="recall-card-header">';
    $html .= '<div class="recall-card-title">';
    
    if ($atts['link'] !== 'none') {
        $html .= '<a href="' . esc_url($term_url) . '"' . $link_attributes . '>';
    }
    
    $html .= '<strong>' . esc_html($link_text) . '</strong>';
    
    if ($atts['link'] !== 'none') {
        $html .= '</a>';
    }
    
    $html .= '</div>';
    
    if ($atts['show_category'] === 'true') {
        $html .= '<span class="recall-card-category">' . esc_html($term['category']['name']) . '</span>';
    }
    
    $html .= '</div>';
    
    $html .= '<div class="recall-card-body">';
    $html .= '<p>' . esc_html($definition) . '</p>';
    $html .= '</div>';
    
    if ($atts['link'] !== 'none') {
        $html .= '<div class="recall-card-footer">';
        $html .= '<a href="' . esc_url($term_url) . '"' . $link_attributes . ' class="recall-card-link">Définition complète →</a>';
        $html .= '</div>';
    }
    
    $html .= '</div>';
    
    return $html;
}