<?php
// Sécurité
if (!defined('ABSPATH')) {
    exit;
}

// ================================
// REWRITE RULES POUR GLOSSAIRE
// ================================

add_action('init', 'humari_glossary_add_rewrite_rules');

function humari_glossary_add_rewrite_rules() {
    // /glossaire/ - Hub principal
    add_rewrite_rule(
        '^glossaire/?$',
        'index.php?glossary_page=hub',
        'top'
    );
    
    // /glossaire/recherche/ - Page de recherche
    add_rewrite_rule(
        '^glossaire/recherche/?$',
        'index.php?glossary_page=search',
        'top'
    );
    
    // /glossaire/categorie-slug/ - Page catégorie
    add_rewrite_rule(
        '^glossaire/([^/]+)/?$',
        'index.php?glossary_page=category&glossary_category=$matches[1]',
        'top'
    );
    
    // /glossaire/categorie-slug/terme-slug/ - Page terme
    add_rewrite_rule(
        '^glossaire/([^/]+)/([^/]+)/?$',
        'index.php?glossary_page=term&glossary_category=$matches[1]&glossary_term=$matches[2]',
        'top'
    );
}

add_filter('query_vars', 'humari_glossary_add_query_vars');

function humari_glossary_add_query_vars($vars) {
    $vars[] = 'glossary_page';
    $vars[] = 'glossary_category';
    $vars[] = 'glossary_term';
    return $vars;
}

add_action('template_redirect', 'humari_glossary_template_redirect');

function humari_glossary_template_redirect() {
    $page_type = get_query_var('glossary_page');
    
    if (!$page_type) {
        return;
    }
    
    switch ($page_type) {
        case 'hub':
            humari_glossary_render_hub_page();
            break;
        case 'category':
            humari_glossary_render_category_page();
            break;
        case 'term':
            humari_glossary_render_term_page();
            break;
        case 'search':
            humari_glossary_render_search_page();
            break;
    }
    
    exit;
}

function humari_glossary_render_hub_page() {
    // Récupérer les données nécessaires
    $categories = humari_glossary_get_category_tree();
    $popular_terms = humari_glossary_get_popular_terms(10);
    
    // SEO Meta
    humari_glossary_set_seo_meta(
        'Glossaire Business - Humari',
        'Découvrez notre glossaire complet des termes business, marketing, SEO et vente avec plus de 60 définitions essentielles.',
        'glossaire, business, marketing, SEO, vente, définitions'
    );
    
    get_header();
    
    echo '<div class="glossary-page glossary-hub-page">';
    echo '<div class="container">';
    
    // En-tête
    echo '<header class="page-header">';
    echo '<h1>Glossaire Business</h1>';
    echo '<p class="page-description">Découvrez les termes essentiels du business, marketing digital, SEO et vente</p>';
    echo '</header>';
    
    // Barre de recherche principale
    echo do_shortcode('[humari_glossary_search placeholder="Rechercher un terme..." auto_search="true"]');
    
    // Termes populaires
    echo do_shortcode('[humari_glossary_popular limit="10" title="🔥 Termes populaires" layout="inline"]');
    
    // Catégories principales
    if (!is_wp_error($categories)) {
        echo '<section class="categories-overview">';
        echo '<h2>Explorez par catégorie</h2>';
        echo '<div class="categories-grid">';
        
        foreach ($categories as $category) {
            $terms_count = $category['terms_count'] ?? 0;
            
            echo '<div class="category-card">';
            echo '<h3><a href="/glossaire/' . esc_attr($category['slug']) . '/">';
            echo esc_html($category['name']);
            echo '</a></h3>';
            
            if (!empty($category['description'])) {
                echo '<p>' . esc_html(wp_trim_words($category['description'], 15)) . '</p>';
            }
            
            echo '<div class="category-meta">';
            echo '<span class="terms-count">' . $terms_count . ' termes</span>';
            echo '</div>';
            
            if (!empty($category['children'])) {
                echo '<ul class="subcategories-preview">';
                $shown = 0;
                foreach ($category['children'] as $child) {
                    if ($shown >= 3) break;
                    echo '<li><a href="/glossaire/' . esc_attr($child['slug']) . '/">' . esc_html($child['name']) . '</a></li>';
                    $shown++;
                }
                if (count($category['children']) > 3) {
                    echo '<li class="more">+' . (count($category['children']) - 3) . ' autres</li>';
                }
                echo '</ul>';
            }
            
            echo '</div>';
        }
        
        echo '</div>';
        echo '</section>';
    }
    
    // Termes essentiels
    echo do_shortcode('[humari_glossary_essential title="📚 Termes essentiels à connaître" layout="cards"]');
    
    echo '</div>';
    echo '</div>';
    
    get_footer();
}

function humari_glossary_render_category_page() {
    $category_slug = get_query_var('glossary_category');
    
    if (!$category_slug) {
        wp_redirect('/glossaire/');
        exit;
    }
    
    // Récupérer la catégorie
    $category = humari_glossary_get_category_by_slug($category_slug);
    
    if (is_wp_error($category) || !$category) {
        wp_redirect('/glossaire/');
        exit;
    }
    
    // SEO Meta
    humari_glossary_set_seo_meta(
        $category['name'] . ' - Glossaire Business Humari',
        'Découvrez tous les termes liés à ' . $category['name'] . ' dans notre glossaire business complet.',
        $category['name'] . ', glossaire, définitions, business'
    );
    
    get_header();
    
    echo '<div class="glossary-page glossary-category-page">';
    echo '<div class="container">';
    
    // Breadcrumb
    echo humari_glossary_render_breadcrumb_nav($category);
    
    // Contenu de la catégorie via shortcode
    echo do_shortcode('[humari_glossary_category slug="' . esc_attr($category_slug) . '" terms_per_page="20"]');
    
    echo '</div>';
    echo '</div>';
    
    get_footer();
}

function humari_glossary_render_term_page() {
    $category_slug = get_query_var('glossary_category');
    $term_slug = get_query_var('glossary_term');
    
    if (!$category_slug || !$term_slug) {
        wp_redirect('/glossaire/');
        exit;
    }
    
    // Récupérer le terme
    $term = humari_glossary_get_term_by_slug($term_slug);
    
    if (is_wp_error($term) || !$term) {
        wp_redirect('/glossaire/' . $category_slug . '/');
        exit;
    }
    
    // Vérifier que le terme appartient bien à cette catégorie et rediriger si nécessaire
    if ($term['category']['slug'] !== $category_slug) {
        wp_redirect('/glossaire/' . $term['category']['slug'] . '/' . $term_slug . '/');
        exit;
    }
    
    // Récupérer la traduction courante
    $translation = $term['current_translation'] ?? $term['translations'][0] ?? null;
    
    if (!$translation) {
        wp_redirect('/glossaire/' . $category_slug . '/');
        exit;
    }
    
    // SEO Meta dynamique
    $meta_title = $translation['title'] . ' - Définition | Glossaire Humari';
    $meta_description = 'Définition de ' . $translation['title'] . ' : ' . wp_trim_words($translation['definition'], 25);
    $meta_keywords = $translation['title'] . ', définition, ' . $term['category']['name'] . ', glossaire business';
    
    humari_glossary_set_seo_meta($meta_title, $meta_description, $meta_keywords);
    
    // Structured Data (JSON-LD)
    humari_glossary_add_structured_data($term);
    
    get_header();
    
    echo '<div class="glossary-page glossary-term-page">';
    echo '<div class="container">';
    
    // Breadcrumb
    echo humari_glossary_render_breadcrumb_nav($term['category']);
    echo ' <span>›</span> <span>' . esc_html($translation['title']) . '</span>';
    
    // Contenu du terme
    echo '<article class="term-content">';
    
    // Header
    echo '<header class="term-header">';
    echo '<h1 class="term-title">' . esc_html($translation['title']) . '</h1>';
    echo '<a href="/glossaire/' . esc_attr($term['category']['slug']) . '/" class="term-category-badge">';
    echo esc_html($term['category']['name']);
    echo '</a>';
    echo '</header>';
    
    // Définition
    if (!empty($translation['definition'])) {
        echo '<div class="term-definition">';
        echo '<p>' . esc_html($translation['definition']) . '</p>';
        echo '</div>';
    }
    
    // Exemples
    if (!empty($translation['examples'])) {
        echo '<div class="term-examples">';
        echo '<h4>💡 Exemple concret</h4>';
        echo '<p>' . esc_html($translation['examples']) . '</p>';
        echo '</div>';
    }
    
    // Formule
    if (!empty($translation['formula'])) {
        echo '<div class="term-formulas">';
        echo '<h4>📊 Formule</h4>';
        echo '<p><code>' . esc_html($translation['formula']) . '</code></p>';
        echo '</div>';
    }
    
    // Termes liés
    if (!empty($term['related_terms'])) {
        echo '<div class="related-terms">';
        echo '<h3>🔗 Termes liés</h3>';
        echo '<div class="related-terms-list">';
        
        foreach ($term['related_terms'] as $related) {
            echo '<a href="/glossaire/' . esc_attr($related['category']['slug']) . '/' . esc_attr($related['slug']) . '/" class="related-term">';
            echo esc_html($related['title']);
            echo '</a>';
        }
        
        echo '</div>';
        echo '</div>';
    }
    
    echo '</article>';
    
    echo '</div>';
    echo '</div>';
    
    get_footer();
}

function humari_glossary_render_search_page() {
    humari_glossary_set_seo_meta(
        'Recherche - Glossaire Business Humari',
        'Recherchez dans notre glossaire business complet avec plus de 60 termes spécialisés.',
        'recherche, glossaire, business, marketing, SEO'
    );
    
    get_header();
    
    echo '<div class="glossary-page glossary-search-page">';
    echo '<div class="container">';
    
    echo '<header class="page-header">';
    echo '<h1>Recherche dans le glossaire</h1>';
    echo '</header>';
    
    echo do_shortcode('[humari_glossary_search placeholder="Que recherchez-vous ?" auto_search="true"]');
    
    echo '</div>';
    echo '</div>';
    
    get_footer();
}

function humari_glossary_render_breadcrumb_nav($category) {
    $html = '<nav class="glossary-breadcrumb">';
    $html .= '<a href="/glossaire/">Glossaire</a>';
    $html .= ' <span>›</span> ';
    
    if (isset($category['parent']) && $category['parent']) {
        $html .= '<a href="/glossaire/' . esc_attr($category['parent']['slug']) . '/">';
        $html .= esc_html($category['parent']['name']);
        $html .= '</a>';
        $html .= ' <span>›</span> ';
    }
    
    $html .= '<span>' . esc_html($category['name']) . '</span>';
    $html .= '</nav>';
    
    return $html;
}

function humari_glossary_set_seo_meta($title, $description, $keywords) {
    add_filter('wp_title', function() use ($title) {
        return $title;
    });
    
    add_action('wp_head', function() use ($description, $keywords) {
        echo '<meta name="description" content="' . esc_attr($description) . '">' . "\n";
        echo '<meta name="keywords" content="' . esc_attr($keywords) . '">' . "\n";
        echo '<meta property="og:description" content="' . esc_attr($description) . '">' . "\n";
        echo '<meta property="og:type" content="article">' . "\n";
    });
}

function humari_glossary_add_structured_data($term) {
    add_action('wp_head', function() use ($term) {
        $translation = $term['current_translation'] ?? $term['translations'][0] ?? null;
        
        if (!$translation) return;
        
        $structured_data = array(
            '@context' => 'https://schema.org',
            '@type' => 'DefinedTerm',
            'name' => $translation['title'],
            'description' => $translation['definition'],
            'inDefinedTermSet' => array(
                '@type' => 'DefinedTermSet',
                'name' => 'Glossaire Business Humari',
                'description' => 'Glossaire complet des termes business, marketing et SEO'
            )
        );
        
        if (!empty($translation['examples'])) {
            $structured_data['example'] = $translation['examples'];
        }
        
        echo '<script type="application/ld+json">';
        echo json_encode($structured_data, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
        echo '</script>' . "\n";
    });
}

// Activation des rewrite rules
register_activation_hook(__FILE__, 'humari_glossary_flush_rewrite_rules');
register_deactivation_hook(__FILE__, 'humari_glossary_flush_rewrite_rules');

function humari_glossary_flush_rewrite_rules() {
    humari_glossary_add_rewrite_rules();
    flush_rewrite_rules();
}