<?php
// Sécurité
if (!defined('ABSPATH')) {
    exit;
}

// ================================
// SHORTCODES GLOSSAIRE
// ================================

add_action('init', 'humari_glossary_register_shortcodes');

function humari_glossary_register_shortcodes() {
    add_shortcode('humari_glossary_hub', 'humari_glossary_hub_shortcode');
    add_shortcode('humari_glossary_category', 'humari_glossary_category_shortcode');
    add_shortcode('humari_glossary_term', 'humari_glossary_term_shortcode');
    add_shortcode('humari_glossary_search', 'humari_glossary_search_shortcode');
    add_shortcode('humari_glossary_popular', 'humari_glossary_popular_shortcode');
    add_shortcode('humari_glossary_essential', 'humari_glossary_essential_shortcode');
}

function humari_glossary_hub_shortcode($atts) {
    $atts = shortcode_atts(array(
        'show_categories' => 'true',
        'show_search' => 'true',
        'show_popular' => 'true',
        'popular_limit' => '5',
        'show_stats' => 'false'
    ), $atts);
    
    $html = '<div class="humari-glossary-hub">';
    
    // Script AJAX
    $html .= '<script>window.ajaxurl = "' . admin_url('admin-ajax.php') . '";</script>';
    
    // Section recherche
    if ($atts['show_search'] === 'true') {
        $html .= humari_glossary_render_search_section();
    }
    
    // Section catégories
    if ($atts['show_categories'] === 'true') {
        $html .= humari_glossary_render_categories_section();
    }
    
    // Section termes populaires
    if ($atts['show_popular'] === 'true') {
        $html .= humari_glossary_render_popular_section($atts['popular_limit']);
    }
    
    // Section statistiques
    if ($atts['show_stats'] === 'true') {
        $html .= humari_glossary_render_stats_section();
    }
    
    $html .= '</div>';
    
    return $html;
}

function humari_glossary_category_shortcode($atts) {
    $atts = shortcode_atts(array(
        'slug' => '',
        'show_breadcrumb' => 'true',
        'show_description' => 'true',
        'terms_per_page' => '20',
        'show_subcategories' => 'true'
    ), $atts);
    
    if (empty($atts['slug'])) {
        return '<div class="error">Paramètre "slug" requis pour afficher une catégorie</div>';
    }
    
    // Récupérer la catégorie
    $category = humari_glossary_get_category_by_slug($atts['slug']);
    
    if (is_wp_error($category)) {
        return '<div class="error">Erreur lors du chargement de la catégorie</div>';
    }
    
    if (!$category) {
        return '<div class="error">Catégorie non trouvée</div>';
    }
    
    $html = '<div class="humari-glossary-category">';
    $html .= '<script>window.ajaxurl = "' . admin_url('admin-ajax.php') . '";</script>';
    
    // Breadcrumb
    if ($atts['show_breadcrumb'] === 'true') {
        $html .= humari_glossary_render_breadcrumb($category);
    }
    
    // En-tête catégorie
    $html .= '<header class="category-header">';
    $html .= '<h1>' . esc_html($category['name']) . '</h1>';
    
    if ($atts['show_description'] === 'true' && !empty($category['description'])) {
        $html .= '<p class="category-description">' . esc_html($category['description']) . '</p>';
    }
    $html .= '</header>';
    
    // Sous-catégories
    if ($atts['show_subcategories'] === 'true' && !empty($category['children'])) {
        $html .= humari_glossary_render_subcategories($category['children']);
    }
    
    // Liste des termes
    $html .= humari_glossary_render_category_terms($atts['slug'], $atts['terms_per_page']);
    
    $html .= '</div>';
    
    return $html;
}

function humari_glossary_term_shortcode($atts) {
    $atts = shortcode_atts(array(
        'slug' => '',
        'lang' => 'fr',
        'context' => '',
        'show_breadcrumb' => 'true',
        'show_related' => 'true',
        'show_examples' => 'true'
    ), $atts);
    
    if (empty($atts['slug'])) {
        return '<div class="error">Paramètre "slug" requis pour afficher un terme</div>';
    }
    
    // Récupérer le terme
    $term = humari_glossary_get_term_by_slug($atts['slug'], $atts['lang'], $atts['context']);
    
    if (is_wp_error($term)) {
        return '<div class="error">Erreur lors du chargement du terme</div>';
    }
    
    if (!$term) {
        return '<div class="error">Terme non trouvé</div>';
    }
    
    $html = '<div class="humari-glossary-term">';
    $html .= '<script>window.ajaxurl = "' . admin_url('admin-ajax.php') . '";</script>';
    
    // Breadcrumb
    if ($atts['show_breadcrumb'] === 'true') {
        $html .= humari_glossary_render_breadcrumb($term['category']);
        
        // Titre du terme dans le breadcrumb
        $title = $term['primary_translation']['title'] ?? 
                 $term['current_translation']['title'] ?? 
                 $term['translations'][0]['title'] ?? 'N/A';
        $html .= ' <span>›</span> <span>' . esc_html($title) . '</span>';
    }
    
    // Contenu principal du terme
    $html .= humari_glossary_render_term_content($term, $atts);
    
    // Termes liés
    if ($atts['show_related'] === 'true' && !empty($term['related_terms'])) {
        $html .= humari_glossary_render_related_terms($term['related_terms']);
    }
    
    $html .= '</div>';
    
    return $html;
}

function humari_glossary_search_shortcode($atts) {
    $atts = shortcode_atts(array(
        'placeholder' => 'Rechercher un terme...',
        'results_per_page' => '10',
        'show_categories_filter' => 'true',
        'auto_search' => 'true'
    ), $atts);
    
    $html = '<div class="humari-glossary-search">';
    $html .= '<script>window.ajaxurl = "' . admin_url('admin-ajax.php') . '";</script>';
    
    // Formulaire de recherche
    $html .= '<form class="glossary-search-form" id="glossary-search-form">';
    $html .= '<div class="search-input-group">';
    $html .= '<input type="text" id="glossary-search-input" placeholder="' . esc_attr($atts['placeholder']) . '" />';
    $html .= '<button type="submit" class="search-button">🔍</button>';
    $html .= '</div>';
    
    // Filtre par catégorie (optionnel)
    if ($atts['show_categories_filter'] === 'true') {
        $html .= humari_glossary_render_categories_filter();
    }
    
    $html .= '</form>';
    
    // Zone de résultats
    $html .= '<div id="glossary-search-results" class="search-results"></div>';
    
    // JavaScript pour la recherche
    if ($atts['auto_search'] === 'true') {
        $html .= humari_glossary_search_javascript();
    }
    
    $html .= '</div>';
    
    return $html;
}

function humari_glossary_popular_shortcode($atts) {
    $atts = shortcode_atts(array(
        'limit' => '10',
        'lang' => 'fr',
        'show_title' => 'true',
        'title' => 'Termes populaires',
        'layout' => 'list' // list, grid, inline
    ), $atts);
    
    $popular_terms = humari_glossary_get_popular_terms($atts['limit'], $atts['lang']);
    
    if (is_wp_error($popular_terms)) {
        return '<div class="error">Erreur lors du chargement des termes populaires</div>';
    }
    
    $html = '<div class="humari-glossary-popular layout-' . esc_attr($atts['layout']) . '">';
    
    if ($atts['show_title'] === 'true') {
        $html .= '<h3>' . esc_html($atts['title']) . '</h3>';
    }
    
    $html .= humari_glossary_render_terms_list($popular_terms, $atts['layout']);
    $html .= '</div>';
    
    return $html;
}

function humari_glossary_essential_shortcode($atts) {
    $atts = shortcode_atts(array(
        'category' => '',
        'lang' => 'fr',
        'show_title' => 'true',
        'title' => 'Termes essentiels',
        'layout' => 'grid' // list, grid, cards
    ), $atts);
    
    $essential_terms = humari_glossary_get_essential_terms($atts['category'], $atts['lang']);
    
    if (is_wp_error($essential_terms)) {
        return '<div class="error">Erreur lors du chargement des termes essentiels</div>';
    }
    
    $html = '<div class="humari-glossary-essential layout-' . esc_attr($atts['layout']) . '">';
    
    if ($atts['show_title'] === 'true') {
        $html .= '<h3>' . esc_html($atts['title']) . '</h3>';
    }
    
    $html .= humari_glossary_render_terms_list($essential_terms, $atts['layout']);
    $html .= '</div>';
    
    return $html;
}

// ================================
// FONCTIONS DE RENDU
// ================================

function humari_glossary_render_search_section() {
    $html = '<section class="glossary-search-section">';
    $html .= '<h2>Rechercher un terme</h2>';
    $html .= '<form class="glossary-search-form" id="glossary-search-form">';
    $html .= '<div class="search-input-group">';
    $html .= '<input type="text" id="glossary-search-input" placeholder="Tapez votre recherche..." />';
    $html .= '<button type="submit" class="search-button">Rechercher</button>';
    $html .= '</div>';
    $html .= '</form>';
    $html .= '<div id="search-suggestions" class="search-suggestions"></div>';
    $html .= '</section>';
    
    return $html;
}

function humari_glossary_render_categories_section() {
    $categories = humari_glossary_get_category_tree();
    
    if (is_wp_error($categories)) {
        return '<div class="error">Erreur lors du chargement des catégories</div>';
    }
    
    $html = '<section class="glossary-categories-section">';
    $html .= '<h2>Catégories</h2>';
    $html .= '<div class="categories-grid">';
    
    foreach ($categories as $category) {
        $html .= '<div class="category-card">';
        $html .= '<h3><a href="/glossaire/' . esc_attr($category['slug']) . '/">' . esc_html($category['name']) . '</a></h3>';
        
        if (!empty($category['description'])) {
            $html .= '<p>' . esc_html(wp_trim_words($category['description'], 20)) . '</p>';
        }
        
        if (!empty($category['children'])) {
            $html .= '<ul class="subcategories">';
            foreach ($category['children'] as $child) {
                $html .= '<li><a href="/glossaire/' . esc_attr($child['slug']) . '/">' . esc_html($child['name']) . '</a></li>';
            }
            $html .= '</ul>';
        }
        
        $html .= '</div>';
    }
    
    $html .= '</div>';
    $html .= '</section>';
    
    return $html;
}

function humari_glossary_render_popular_section($limit) {
    $popular_terms = humari_glossary_get_popular_terms($limit);
    
    if (is_wp_error($popular_terms)) {
        return '<div class="error">Erreur lors du chargement des termes populaires</div>';
    }
    
    $html = '<section class="glossary-popular-section">';
    $html .= '<h2>Termes populaires</h2>';
    $html .= '<div class="popular-terms">';
    
    foreach ($popular_terms as $term) {
        // ✅ FIX: Utiliser primary_translation
        $title = $term['primary_translation']['title'] ?? 
                 $term['current_translation']['title'] ?? 
                 $term['translations'][0]['title'] ?? 'N/A';
                 
        $html .= '<a href="/glossaire/' . esc_attr($term['category']['slug']) . '/' . esc_attr($term['slug']) . '/" class="popular-term">';
        $html .= esc_html($title) . ' <span class="popularity-score">(' . $term['popularity_score'] . ')</span>';
        $html .= '</a>';
    }
    
    $html .= '</div>';
    $html .= '</section>';
    
    return $html;
}

function humari_glossary_render_stats_section() {
    return '<section class="glossary-stats-section"><h2>Statistiques</h2><p>Bientôt disponible...</p></section>';
}

function humari_glossary_render_breadcrumb($category) {
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

function humari_glossary_render_subcategories($subcategories) {
    $html = '<section class="subcategories-section">';
    $html .= '<h3>Sous-catégories</h3>';
    $html .= '<div class="subcategories-grid">';
    
    foreach ($subcategories as $subcategory) {
        $html .= '<div class="subcategory-card">';
        $html .= '<h4><a href="/glossaire/' . esc_attr($subcategory['slug']) . '/">' . esc_html($subcategory['name']) . '</a></h4>';
        if (!empty($subcategory['description'])) {
            $html .= '<p>' . esc_html(wp_trim_words($subcategory['description'], 15)) . '</p>';
        }
        $html .= '</div>';
    }
    
    $html .= '</div>';
    $html .= '</section>';
    
    return $html;
}

function humari_glossary_render_category_terms($category_slug, $limit) {
    $terms = humari_glossary_get_terms(array(
        'category_slug' => $category_slug,
        'page_size' => $limit
    ));
    
    if (is_wp_error($terms)) {
        return '<div class="error">Erreur lors du chargement des termes</div>';
    }
    
    $html = '<section class="category-terms-section">';
    $html .= '<h3>Termes de cette catégorie</h3>';
    
    if (empty($terms['results'])) {
        $html .= '<p>Aucun terme trouvé dans cette catégorie.</p>';
    } else {
        $html .= '<div class="terms-grid">';
        
        foreach ($terms['results'] as $term) {
            // ✅ FIX: Utiliser primary_translation
            $title = $term['primary_translation']['title'] ?? 
                     $term['current_translation']['title'] ?? 
                     $term['translations'][0]['title'] ?? 'N/A';
            $definition = $term['primary_translation']['definition'] ?? 
                         $term['current_translation']['definition'] ?? 
                         $term['translations'][0]['definition'] ?? '';
            
            $html .= '<div class="term-card">';
            $html .= '<h4><a href="/glossaire/' . esc_attr($term['category']['slug']) . '/' . esc_attr($term['slug']) . '/">' . esc_html($title) . '</a></h4>';
            if (!empty($definition)) {
                $html .= '<p>' . esc_html(wp_trim_words($definition, 20)) . '</p>';
            }
            $html .= '</div>';
        }
        
        $html .= '</div>';
    }
    
    $html .= '</section>';
    
    return $html;
}

function humari_glossary_render_term_content($term, $atts) {
    // ✅ FIX: Utiliser primary_translation
    $translation = $term['primary_translation'] ?? 
                   $term['current_translation'] ?? 
                   $term['translations'][0] ?? null;
    
    if (!$translation) {
        return '<div class="error">Traduction non trouvée</div>';
    }
    
    $html = '<article class="term-content">';
    
    // Header
    $html .= '<header class="term-header">';
    $html .= '<h1 class="term-title">' . esc_html($translation['title']) . '</h1>';
    $html .= '<a href="/glossaire/' . esc_attr($term['category']['slug']) . '/" class="term-category-badge">';
    $html .= esc_html($term['category']['name']);
    $html .= '</a>';
    $html .= '</header>';
    
    // Définition
    if (!empty($translation['definition'])) {
        $html .= '<div class="term-definition">';
        $html .= '<p>' . esc_html($translation['definition']) . '</p>';
        $html .= '</div>';
    }
    
    // Exemples
    if ($atts['show_examples'] === 'true' && !empty($translation['examples'])) {
        $html .= '<div class="term-examples">';
        $html .= '<h4>💡 Exemple concret</h4>';
        $html .= '<p>' . esc_html($translation['examples']) . '</p>';
        $html .= '</div>';
    }
    
    // Formule
    if (!empty($translation['formula'])) {
        $html .= '<div class="term-formulas">';
        $html .= '<h4>📊 Formule</h4>';
        $html .= '<p><code>' . esc_html($translation['formula']) . '</code></p>';
        $html .= '</div>';
    }
    
    $html .= '</article>';
    
    return $html;
}

function humari_glossary_render_related_terms($related_terms) {
    if (empty($related_terms)) {
        return '';
    }
    
    $html = '<div class="related-terms">';
    $html .= '<h3>🔗 Termes liés</h3>';
    $html .= '<div class="related-terms-list">';
    
    foreach ($related_terms as $related) {
        // ✅ VÉRIFICATION SÉCURISÉE DES DONNÉES
        $title = 'N/A';
        if (isset($related['title'])) {
            $title = $related['title'];
        } elseif (isset($related['primary_translation']['title'])) {
            $title = $related['primary_translation']['title'];
        } elseif (isset($related['current_translation']['title'])) {
            $title = $related['current_translation']['title'];
        } elseif (isset($related['translations'][0]['title'])) {
            $title = $related['translations'][0]['title'];
        }
        
        // ✅ CONSTRUCTION SÉCURISÉE DE L'URL
        $url = '/glossaire/';
        if (isset($related['category']) && isset($related['category']['slug']) && isset($related['slug'])) {
            $url .= esc_attr($related['category']['slug']) . '/' . esc_attr($related['slug']) . '/';
        } elseif (isset($related['slug'])) {
            // Fallback : essayer de récupérer la catégorie via une requête API
            $term_details = humari_glossary_get_term_by_slug($related['slug']);
            if (!is_wp_error($term_details) && $term_details && isset($term_details['category']['slug'])) {
                $url .= esc_attr($term_details['category']['slug']) . '/' . esc_attr($related['slug']) . '/';
            } else {
                // Dernier fallback : URL sans catégorie (page de recherche)
                $url = '/glossaire/?q=' . urlencode($related['slug']);
            }
        }
        
        $html .= '<a href="' . $url . '" class="related-term">';
        $html .= esc_html($title);
        $html .= '</a>';
    }
    
    $html .= '</div>';
    $html .= '</div>';
    
    return $html;
}

function humari_glossary_render_terms_list($terms, $layout = 'list') {
    if (empty($terms)) {
        return '<p>Aucun terme trouvé.</p>';
    }
    
    $html = '<div class="terms-list layout-' . esc_attr($layout) . '">';
    
    foreach ($terms as $term) {
        // ✅ FIX: Utiliser primary_translation
        $title = $term['primary_translation']['title'] ?? 
                 $term['current_translation']['title'] ?? 
                 $term['translations'][0]['title'] ?? 'N/A';
        
        if ($layout === 'inline') {
            $html .= '<a href="/glossaire/' . esc_attr($term['category']['slug']) . '/' . esc_attr($term['slug']) . '/" class="term-tag">';
            $html .= esc_html($title);
            $html .= '</a>';
        } else {
            $definition = $term['primary_translation']['definition'] ?? 
                         $term['current_translation']['definition'] ?? 
                         $term['translations'][0]['definition'] ?? '';
            
            $html .= '<div class="term-item">';
            $html .= '<h4><a href="/glossaire/' . esc_attr($term['category']['slug']) . '/' . esc_attr($term['slug']) . '/">' . esc_html($title) . '</a></h4>';
            if (!empty($definition)) {
                $html .= '<p>' . esc_html(wp_trim_words($definition, 15)) . '</p>';
            }
            
            // Badge essentiel
            if ($term['is_essential']) {
                $html .= '<span class="essential-badge">⭐ Essentiel</span>';
            }
            
            $html .= '</div>';
        }
    }
    
    $html .= '</div>';
    
    return $html;
}

function humari_glossary_render_categories_filter() {
    $categories = humari_glossary_get_categories();
    
    if (is_wp_error($categories) || empty($categories['results'])) {
        return ''; // Pas de filtre si pas de catégories
    }
    
    $html = '<div class="categories-filter">';
    $html .= '<label for="category-filter">Filtrer par catégorie :</label>';
    $html .= '<select id="category-filter" name="category">';
    $html .= '<option value="">Toutes les catégories</option>';
    
    foreach ($categories['results'] as $category) {
        $html .= '<option value="' . esc_attr($category['slug']) . '">' . esc_html($category['name']) . '</option>';
    }
    
    $html .= '</select>';
    $html .= '</div>';
    
    return $html;
}

function humari_glossary_search_javascript() {
    return '
    <script>
    document.addEventListener("DOMContentLoaded", function() {
        const searchInput = document.getElementById("glossary-search-input");
        const searchResults = document.getElementById("glossary-search-results");
        let searchTimeout;
        
        if (searchInput) {
            searchInput.addEventListener("input", function() {
                clearTimeout(searchTimeout);
                const query = this.value.trim();
                
                if (query.length < 2) {
                    searchResults.innerHTML = "";
                    return;
                }
                
                searchTimeout = setTimeout(function() {
                    performSearch(query);
                }, 300);
            });
        }
        
        function performSearch(query) {
            searchResults.innerHTML = "<div class=\\"loading\\">🔍 Recherche en cours...</div>";
            
            fetch(window.ajaxurl + "?action=humari_glossary_search&q=" + encodeURIComponent(query))
                .then(response => {
                    console.log("Response status:", response.status);
                    return response.json();
                })
                .then(data => {
                    console.log("API Response:", data);
                    
                    if (data.success && data.data && data.data.results) {
                        displayResults(data.data.results);
                    } else {
                        console.error("API Error:", data);
                        searchResults.innerHTML = "<div class=\\"error\\">❌ Erreur de recherche</div>";
                    }
                })
                .catch(error => {
                    console.error("Fetch error:", error);
                    searchResults.innerHTML = "<div class=\\"error\\">❌ Erreur de connexion: " + error.message + "</div>";
                });
        }
        
        function displayResults(results) {
            console.log("Displaying results:", results);
            
            if (!results || results.length === 0) {
                searchResults.innerHTML = "<div class=\\"no-results\\">🔍 Aucun résultat trouvé</div>";
                return;
            }
            
            let html = "<div class=\\"search-results-list\\">";
            html += "<h4>📝 " + results.length + " résultat(s) trouvé(s)</h4>";
            
            results.forEach(function(term) {
                // ✅ FIX: Utiliser primary_translation au lieu de current_translation
                const title = term.primary_translation ? term.primary_translation.title : "N/A";
                const definition = term.primary_translation ? term.primary_translation.definition : "";
                
                html += "<div class=\\"search-result-item\\">";
                html += "<h4><a href=\\"/glossaire/" + term.category.slug + "/" + term.slug + "/\\">" + title + "</a></h4>";
                
                if (definition) {
                    const shortDefinition = definition.length > 150 ? definition.substring(0, 150) + "..." : definition;
                    html += "<p class=\\"term-definition\\">" + shortDefinition + "</p>";
                }
                
                html += "<span class=\\"term-category\\">📂 " + term.category.name + "</span>";
                
                if (term.is_essential) {
                    html += "<span class=\\"essential-badge\\">⭐ Essentiel</span>";
                }
                
                html += "</div>";
            });
            
            html += "</div>";
            searchResults.innerHTML = html;
        }
    });
    </script>';
}