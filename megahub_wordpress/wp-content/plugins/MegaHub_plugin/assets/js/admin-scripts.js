jQuery(document).ready(function($) {
    // Cache toutes les sections de contenu d'onglet au début
    $('.tab-content').hide();

    // Gestion des clics sur les onglets
    $('a.nav-tab').click(function(e) {
        e.preventDefault();

        // Obtenir l'identifiant de l'onglet sélectionné à partir de l'attribut href
        var tab_id = $(this).attr('href').split('&tab=')[1];

        // Désactiver tous les onglets actifs et cacher leur contenu
        $('a.nav-tab').removeClass('nav-tab-active');
        $('.tab-content').hide();

        // Activer l'onglet sélectionné et afficher son contenu
        $(this).addClass('nav-tab-active');
        $('#' + tab_id).show();
    });

    // Sélectionner l'onglet basé sur l'URL lors du chargement de la page
    var currentTab = window.location.search.match(/tab=([^&]+)/);
    if (currentTab && $('#' + currentTab[1]).length) {
        $('a.nav-tab[href="?page=mega-hub-settings&tab=' + currentTab[1] + '"]').click();
    } else {
        // Si aucun onglet n'est spécifié dans l'URL, cliquer sur le premier onglet
        $('a.nav-tab:first').click();
    }
});


jQuery(document).ready(function($) {
            $('#mega-hub-dalle-submit').on('click', function() {
                var prompt = $('#mega-hub-dalle-prompt').val();
                var model = $('#mega-hub-dalle-model').val();
                var size = $('#mega-hub-dalle-size').val();

                // Appeler la fonction send_image_request_to_megahub avec les paramètres sélectionnés
                send_image_request_to_megahub(prompt, model, size).then(function(imageUrl) {
                    // Télécharger l'image sur WordPress et afficher dans la bibliothèque
                    // Utiliser une fonction telle que store_image_on_wordpress(imageUrl)
                    // puis afficher l'image dans #mega-hub-dalle-library
                });
            });
        });


document.addEventListener('DOMContentLoaded', function() {
    var modelSelectElements = document.querySelectorAll('.model-selection');

    modelSelectElements.forEach(function(selectElement) {
        showModelMessage(selectElement, selectElement.value);

        selectElement.addEventListener('change', function() {
            showModelMessage(selectElement, this.value);
        });
    });

    function showModelMessage(selectElement, model) {

        var messageElement = selectElement.nextElementSibling;
        var message = '';
        var color = '#31708f'; // Couleur par défaut
        // Définis les messages et les couleurs ici
        switch(model) {
            case 'gpt-4-0125-preview':
                message = 'Better quality but might be incomplete due to token limits.';
                color = '#8a6d3b';
                break;
            case 'gpt-4-1106-preview':
                message = 'Most powerful with outdated data.';
                color = '#3c763d';
                break;
            case 'gpt-3.5-turbo-0125':
                message = 'Almost free to generate but low quality, not recommended.';
                color = '#a94442';
                break;
            case 'gpt-4':
                message = 'More expensive but ensures complete blog articles.';
                color = '#31708f';
                break;
            case 'gemini-1.0':
                message = 'Not recommended.';
                color = '#a94442';
                break;
            default:
                message = '';
        }

        // Met à jour l'élément de message
        if (messageElement) {
            messageElement.textContent = message;
            messageElement.style.display = 'block';
            messageElement.style.color = color;
            messageElement.style.borderLeft = '5px solid ' + color;
            messageElement.style.padding = '10px';
            messageElement.style.marginTop = '10px';
            messageElement.style.backgroundColor = '#fcf8e3';
            messageElement.style.borderRadius = '5px';
        }
    }
});
        


document.addEventListener('DOMContentLoaded', function() {
    var form = document.getElementById('mega-hub-auto-blogger-form');
    
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();

            var titlesInput = document.getElementById('titles-input');
            if (!titlesInput.value.trim()) {
                alert('Error: No articles have been specified. Please enter at least one title.');
                return; // Arrête l'exécution si aucun titre n'est renseigné
            }

            var modelSelection = document.getElementById('model-selection').value;
            var numberOfArticles = titlesInput.value.split("\n").filter(line => line.trim()).length;

            // Définition des taux de conversion statiques pour chaque devise
            var conversionRates = {
                'USD': 1,
                'EUR': 0.93,
                'GBP': 0.82,
                'AUD': 1.39,
                'CAD': 1.27,
                'CHF': 0.91,
                'CNY': 6.36,
                'SEK': 9.11,
                'NZD': 1.47
            };

            // Définition des coûts par article pour chaque modèle
            var costPerArticle = {
                'gpt-4-0125-preview': 0.20,
                'gpt-4-1106-preview': 0.15,
                'gpt-3.5-turbo-0125': 0.01,
                'gpt-4': 0.40, 
                'gemini-1.0': 0.25,
            }[modelSelection] || 0.20; // Utilise un coût par défaut si le modèle n'est pas trouvé

            // Applique le taux de conversion pour la devise actuelle
            var totalCost = numberOfArticles * costPerArticle * (conversionRates[currentCurrency] || 1);

            var confirmationMessage = `You are about to generate ${numberOfArticles} articles using the ${modelSelection} model.\n` +
                                      `This process cannot be stopped once started and will cost approximately ${currentCurrency} ${totalCost.toFixed(2)}.\n` +
                                      `Do you want to proceed?`;

            if (confirm(confirmationMessage)) {
                document.getElementById('generator-results').textContent = 'Your request is being processed. You will be notified once the articles are ready.';
                document.getElementById('generator-results').style.display = 'block';

                jQuery.post(ajaxurl, {
                    action: 'handle_ab_form_submission',
                    titles: titlesInput.value,
                    model_selection: modelSelection,
                    // Ajoute les autres données du formulaire ici si nécessaire
                }, function(response) {
                    // Traite la réponse ici, par exemple en affichant un message de succès ou d'erreur
                });
            }
        });
    }
});


jQuery(document).ready(function($) {
    // Initialise le sélecteur de couleurs pour tous les éléments avec la classe 'color-picker'
    $('.color-picker').each(function() {
        $(this).wpColorPicker();
    });
});
