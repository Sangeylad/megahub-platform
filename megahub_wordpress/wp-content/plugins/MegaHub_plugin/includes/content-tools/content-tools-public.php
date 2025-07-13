<?php

/*
function init_content_tools_feature() {

    $options = get_option('mega_hub_content_tools_enable');

    // Vérifie si l'option 'mega_hub_auto_blogger_enable' est définie et différente de 'on'
    if (!isset($options['mega_hub_content_tools_enable']) || $options['mega_hub_content_tools_enable'] !== 'on') {
        return; // Sort de la fonction si Auto Blogger n'est pas activé
    }
*/
// Shortcode pour insérer l'année courante
add_shortcode('current_year', 'current_year_shortcode');
function current_year_shortcode() {
    return date('Y');
}

// Appliquer le shortcode dans le contenu, y compris le contenu d'Elementor et autres constructeurs de page
add_filter('the_content', 'do_shortcode');

// Appliquer le shortcode dans les titres de post/page
add_filter('the_title', 'do_shortcode');

// Appliquer le shortcode dans les meta titles et descriptions gérés par Yoast SEO
add_filter('wpseo_title', 'do_shortcode');
add_filter('wpseo_metadesc', 'do_shortcode');


function current_month_shortcode() {
    return date("F");
}
add_shortcode('current_month', 'current_month_shortcode');



add_shortcode('read_time', 'calculate_read_time');

function calculate_read_time($atts, $content = null) {
    // On extrait le contenu si nécessaire
    $content = !empty($content) ? $content : get_post_field('post_content', get_the_ID());

    // On compte le nombre de mots dans le contenu
    $word_count = str_word_count(strip_tags($content));

    // On calcule le temps de lecture en minutes
    $read_time = ceil($word_count / 180);

    // Préparation des chaînes de caractères pour la traduction
    $minute_singular = __('minute', 'mega-hub');
    $minute_plural = __('minutes', 'mega-hub');
    $estimated_read_time_text = __('Estimated reading time: ', 'mega-hub');

    // On crée le texte à afficher, avec gestion du pluriel pour "minute(s)" en fonction de la langue
    $read_time_text = $read_time . ' ' . _n($minute_singular, $minute_plural, $read_time, 'mega-hub');

    // On retourne le temps de lecture estimé avec un peu de mise en forme
    return '<span class="read-time">' . $estimated_read_time_text . $read_time_text . '</span>';
}


add_shortcode('highlight', 'highlight_text_shortcode');
function highlight_text_shortcode($atts, $content = null) {
    return '<span class="highlight">' . do_shortcode($content) . '</span>';
}

function collapsible_content_shortcode($atts, $content = null) {
    // Extraire les attributs du shortcode
    extract(shortcode_atts(array(
        'title' => 'Title',
        'tag'   => 'h2', // Définir une balise de titre par défaut
    ), $atts));

    // Créer le contenu du shortcode
    return '<div class="collapsible" style="border: 1px solid #ccc; margin-bottom: 20px;">' .
                '<' . $tag . ' class="collapsible-title" style="padding: 10px; background-color: #f7f7f7; cursor: pointer;">' . $title . '</' . $tag . '>' .
                '<div class="collapsible-content" style="padding: 10px; display: none;">' . do_shortcode($content) . '</div>' .
            '</div>';
}
add_shortcode('collapsible', 'collapsible_content_shortcode');




add_shortcode('tooltip', 'tooltip_shortcode');
function tooltip_shortcode($atts, $content = null) {
    extract(shortcode_atts(array(
        'text' => '',
    ), $atts));
    return '<span class="tooltip">' . $content . '<span class="tooltip-text">' . $text . '</span></span>';
}

add_shortcode('countdown', 'countdown_shortcode');
function countdown_shortcode($atts) {
    extract(shortcode_atts(array(
        'date' => '',
    ), $atts));
    
    // Le markup du compte à rebours
    $html = '<div id="countdown-timer" data-countdown="' . esc_attr($date) . '"></div>';

    // Le script JS pour le compte à rebours
    $html .= '<script type="text/javascript">
        document.addEventListener("DOMContentLoaded", function() {
            var countdownTimer = document.getElementById("countdown-timer");
            var countdownDate = new Date(countdownTimer.getAttribute("data-countdown")).getTime();

            var x = setInterval(function() {
                var now = new Date().getTime();
                var distance = countdownDate - now;

                var days = Math.floor(distance / (1000 * 60 * 60 * 24));
                var hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
                var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
                var seconds = Math.floor((distance % (1000 * 60)) / 1000);

                countdownTimer.innerHTML = days + "d " + hours + "h "
                + minutes + "m " + seconds + "s ";

                if (distance < 0) {
                    clearInterval(x);
                    countdownTimer.innerHTML = "EXPIRED";
                }
            }, 1000);
        });
    </script>';

    return $html;
}



function generate_qr_code_shortcode($atts) {
    // Extrais les attributs du shortcode
    $atts = shortcode_atts(array(
        'data' => 'https://www.exemple.com',
        'size' => '150', // Taille du QR Code en pixels
    ), $atts, 'qr_code');

    // Génère un ID unique pour chaque QR Code pour éviter les conflits
    $qr_id = uniqid('qr_code_');

    // Prépare le HTML avec un conteneur pour le QR Code
    $html = "<div id='{$qr_id}'></div>";

    // Ajoute le script JS pour générer le QR Code
    $html .= "<script type='text/javascript'>
                new QRCode(document.getElementById('{$qr_id}'), {
                    text: '{$atts['data']}',
                    width: {$atts['size']},
                    height: {$atts['size']}
                });
              </script>";

    return $html;
}
add_shortcode('qr_code', 'generate_qr_code_shortcode');



function protected_content_shortcode($atts, $content = null) {
    // Attributs du shortcode
    $atts = shortcode_atts(array(
        'password' => 'defaultpassword', // Mot de passe par défaut
    ), $atts);

    // Démarre la session si ce n'est pas déjà fait
    if(session_status() == PHP_SESSION_NONE) {
        session_start();
    }

    // Vérifie si le bon mot de passe a été saisi
    $correct_password_entered = isset($_SESSION['shortcode_password']) && $_SESSION['shortcode_password'] == $atts['password'];

    // Formulaire de saisie du mot de passe
    $form = '<form action="" method="post">
                <label for="shortcode_password">Entrez le mot de passe pour voir le contenu :</label>
                <input type="password" id="shortcode_password" name="shortcode_password" required>
                <input type="submit" value="Voir le contenu">
             </form>';

    // Vérifie la saisie du mot de passe
    if(isset($_POST['shortcode_password'])) {
        if($_POST['shortcode_password'] == $atts['password']) {
            $_SESSION['shortcode_password'] = $_POST['shortcode_password'];
            $correct_password_entered = true;
        } else {
            $form .= '<p>Mot de passe incorrect. Veuillez réessayer.</p>';
        }
    }

    // Retourne le contenu protégé si le bon mot de passe est entré, sinon affiche le formulaire
    return $correct_password_entered ? do_shortcode($content) : $form;
}
add_shortcode('content_protector', 'protected_content_shortcode');


function embed_pdf_shortcode($atts) {
    $atts = shortcode_atts(array('width' => '600', 'height' => '500', 'src' => ''), $atts);
    return '<iframe src="' . $atts['src'] . '" width="' . $atts['width'] . '" height="' . $atts['height'] . '"></iframe>';
}
add_shortcode('embed_pdf', 'embed_pdf_shortcode');


function content_for_logged_in_shortcode($atts, $content = null) {
    if (is_user_logged_in()) {
        return do_shortcode($content);
    } else {
        return '<p style="background-color: #f8d7da; color: #721c24; padding: 20px; border-radius: 5px; border: 1px solid #f5c6cb;">Ce contenu est uniquement disponible pour les utilisateurs connectés.</p>';
    }
}
add_shortcode('for_logged_in', 'content_for_logged_in_shortcode');

function content_for_guests_shortcode($atts, $content = null) {
    if (!is_user_logged_in()) {
        return do_shortcode($content);
    } else {
        return '<p style="background-color: #cce5ff; color: #004085; padding: 20px; border-radius: 5px; border: 1px solid #b8daff;">Ce contenu est uniquement disponible pour les visiteurs non connectés.</p>';
    }
}
add_shortcode('for_guests', 'content_for_guests_shortcode');


function visitor_count_shortcode() {
    if (!isset($_SESSION['visitor_count'])) {
        $_SESSION['visitor_count'] = 0;
    }
    $_SESSION['visitor_count']++;
    return "Nombre de visites sur cette page : " . $_SESSION['visitor_count'];
}
add_shortcode('visitor_count', 'visitor_count_shortcode');

/*

}


add_action('init', 'init_content_tools_feature');

*/



/* ----------------- A partir d'ici ça charge même si la fonctionnalité est désactivée ----------------------- */