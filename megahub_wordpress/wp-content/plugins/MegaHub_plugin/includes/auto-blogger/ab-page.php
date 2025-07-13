<?php

function mega_hub_auto_blogger_page() {
    $admins = get_users(array('role' => 'administrator'));
    $currency = get_option('mega_hub_options_global', ['mega_hub_currency' => 'USD'])['mega_hub_currency'];

    // Insère uniquement la devise actuelle dans le HTML
    echo "<script type='text/javascript'>
        var currentCurrency = '{$currency}';
    </script>";
    ?>

    <div class="wrap auto-blogger-container">
        <h1><?php _e('Auto Blogger', 'mega-hub'); ?></h1>

        <h2 class="nav-tab-wrapper">
            <a href="?page=mega-hub-auto-blogger&tab=bulk-generation" class="nav-tab <?php echo (!isset($_GET['tab']) || $_GET['tab'] === 'bulk-generation') ? 'nav-tab-active' : ''; ?>"><?php _e('Bulk Generation', 'mega-hub'); ?></a>
            <a href="?page=mega-hub-auto-blogger&tab=make-it-an-article" class="nav-tab <?php echo (isset($_GET['tab']) && $_GET['tab'] === 'make-it-an-article') ? 'nav-tab-active' : ''; ?>"><?php _e('Make It an Article', 'mega-hub'); ?></a>
        </h2>

        <div id="bulk-generation" class="tab-content" style="<?php echo (!isset($_GET['tab']) || $_GET['tab'] === 'bulk-generation') ? '' : 'display: none;'; ?>">
            <form id="mega-hub-auto-blogger-form">

                <div class="section">
                        <div class="section-header">
                            <h2><?php _e('Titles', 'mega-hub'); ?></h2>
                        </div>
                        <div class="section-content">
                            <div class="input-group">
                                <label for="titles-input"><?php _e('Titles (one per line)', 'mega-hub'); ?></label>
                                <textarea id="titles-input" name="titles" placeholder="<?php esc_attr_e('Insert titles here...', 'mega-hub'); ?>" rows="10"></textarea>
                            </div>
                        </div>
                </div>

                <div class="section">
                    <div class="section-header">
                        <h2><?php _e('Model Selection', 'mega-hub'); ?></h2>
                    </div>
                    <div class="section-content">
                        <div class="input-group">
                            <label for="model-selection"><?php _e('Choose a Model:', 'mega-hub'); ?></label>
                            <?php mega_hub_auto_blogger_gpt_model_render('model-selection'); // Appelle ta fonction de rendu existante ?>
                            <p id="model-message" style="display: none;"></p> <!-- La mise en forme sera gérée par le JS -->
                        </div>
                    </div>
                </div>



                <script type="text/javascript">
                    var modelMessages = {
                        gpt_4_0125: "<?php echo esc_js(__('Better quality but might be incomplete due to token limits.', 'mega-hub')); ?>",
                        gpt_4_1106: "<?php echo esc_js(__('Most powerful with outdated data.', 'mega-hub')); ?>",
                        gpt_3_5_turbo: "<?php echo esc_js(__('Almost free to generate but low quality, not recommended.', 'mega-hub')); ?>",
                        gpt_4: "<?php echo esc_js(__('More expensive but ensures complete blog articles.', 'mega-hub')); ?>",
                        gemini: "<?php echo esc_js(__('Not recommended.', 'mega-hub')); ?>"
                    };
                </script>

                <div class="section">
                    <div class="section-header">
                        <h2><?php _e('Thumbnail Generation', 'mega-hub'); ?></h2>
                    </div>
                    <div class="section-content">
                        <div class="input-group">
                            <label for="generate-thumbnail"><?php _e('Generate Thumbnail:', 'mega-hub'); ?></label>
                            <select id="generate-thumbnail" name="generate_thumbnail">
                                <option value="yes"><?php _e('Yes', 'mega-hub'); ?></option>
                                <option value="no" selected><?php _e('No', 'mega-hub'); ?></option>
                            </select>
                        </div>
                        <div class="input-group">
                            <label for="thumbnail-instructions"><?php _e('Thumbnail Instructions:', 'mega-hub'); ?></label>
                            <textarea id="thumbnail-instructions" name="thumbnail_instructions" placeholder="<?php esc_attr_e('Provide any specific instructions here...', 'mega-hub'); ?>" rows="4"></textarea>
                        </div>
                    </div>
                </div>



                <div class="section">
                    <div class="section-header">
                        <h2><?php _e('Content Settings', 'mega-hub'); ?></h2>
                    </div>
                    <div class="section-content">
                        <div class="input-group">
                            <label for="include-faq">
                                <input type="checkbox" id="include-faq" name="include_faq">
                                <?php _e('Include FAQ', 'mega-hub'); ?>
                            </label>
                        </div>

                        <div class="input-group">
                            <label for="paragraphs-instructions"><?php _e('Custom Instructions for Paragraphs:', 'mega-hub'); ?></label>
                            <textarea id="paragraphs-instructions" name="paragraphs_instructions" placeholder="<?php esc_attr_e('Leave empty if no instructions. Max 200 characters.', 'mega-hub'); ?>" rows="4"></textarea>
                        </div>

                        <div class="input-group">
                            <label for="titles-instructions"><?php _e('Custom Instructions for Titles:', 'mega-hub'); ?></label>
                            <textarea id="titles-instructions" name="titles_instructions" placeholder="<?php esc_attr_e('Leave empty if no instructions. Max 200 characters.', 'mega-hub'); ?>" rows="4"></textarea>
                        </div>
                    </div>
                </div>

                <div class="section">
                    <div class="section-header">
                        <h2><?php _e('Publishing Options', 'mega-hub'); ?></h2>
                    </div>
                    <div class="section-content">
                        <div class="input-group">
                            <label for="post-status"><?php _e('Post Status:', 'mega-hub'); ?></label>
                            <select id="post-status" name="post_status">
                                <option value="publish"><?php _e('Publish', 'mega-hub'); ?></option>
                                <option value="draft"><?php _e('Draft', 'mega-hub'); ?></option>
                            </select>
                        </div>

                        <div class="input-group">
                            <label for="publish-frequency"><?php _e('Publish Frequency:', 'mega-hub'); ?></label>
                            <select id="publish-frequency" name="publish_frequency">
                                <option value="immediately"><?php _e('All at once', 'mega-hub'); ?></option>
                                <option value="6h"><?php _e('Every 6 hours', 'mega-hub'); ?></option>
                                <option value="12h"><?php _e('Every 12 hours', 'mega-hub'); ?></option>
                                <option value="24h"><?php _e('Every 24 hours', 'mega-hub'); ?></option>
                                <option value="2d"><?php _e('Every 2 days', 'mega-hub'); ?></option>
                                <option value="3d"><?php _e('Every 3 days', 'mega-hub'); ?></option>
                            </select>
                        </div>

                        <div class="input-group">
                            <label for="author"><?php _e('Author:', 'mega-hub'); ?></label>
                            <select id="author" name="author">
                                <?php foreach ($admins as $admin) : ?>
                                    <option value="<?php echo esc_attr($admin->ID); ?>">
                                        <?php echo esc_html($admin->display_name); ?>
                                    </option>
                                <?php endforeach; ?>
                            </select>
                        </div>
                    </div>
                </div>

                <div class="submit">
                    <button type="submit" class="button button-primary"><?php _e('Generate', 'mega-hub'); ?></button>
                </div>
                </form>
        </div>

        <div id="make-it-an-article" class="tab-content" style="<?php echo (isset($_GET['tab']) && $_GET['tab'] === 'make-it-an-article') ? '' : 'display: none;'; ?>">
            <h2><?php _e('Make It an Article', 'mega-hub'); ?></h2>
            <p><?php _e('Fill in the fields below with your article details. Leave fields empty where you want the AI to decide.', 'mega-hub'); ?></p>

            <form id="make-it-an-article-form">
            <?php
                // Récupère la valeur actuelle du modèle sélectionné depuis les options enregistrées
                $options = get_option('mega_hub_options_auto_blogger');
                $selected_model = isset($options['mega_hub_auto_blogger_gpt_model']) ? $options['mega_hub_auto_blogger_gpt_model'] : '';
                ?>

                <div class="section">
                    <div class="section-header">
                        <h2><?php _e('Model Selection', 'mega-hub'); ?></h2>
                    </div>
                    <div class="section-content">
                        <div class="input-group">
                            <label for="model-selection-article"><?php _e('Choose a Model:', 'mega-hub'); ?></label>
                            <select id="model-selection-article" class="model-selection" name="model_selection_article">
                                <option value="gpt-4-0125-preview" <?php selected($selected_model, 'gpt-4-0125-preview'); ?>>GPT-4-0125-Preview</option>
                                <option value="gpt-4-1106-preview" <?php selected($selected_model, 'gpt-4-1106-preview'); ?>>GPT-4-1106-Preview</option>
                                <option value="gpt-3.5-turbo-0125" <?php selected($selected_model, 'gpt-3.5-turbo-0125'); ?>>GPT-3.5-Turbo-0125</option>
                                <option value="gpt-4" <?php selected($selected_model, 'gpt-4'); ?>>GPT-4</option>
                                <option value="gemini-1.0" <?php selected($selected_model, 'gemini-1.0'); ?>>Gemini 1.0</option>
                            </select>
                            <p id="model-message-article" style="display: none;"></p> <!-- Le message sera affiché ici -->
                        </div>
                    </div>
                </div>


                <div class="section">
                    <div class="section-header">
                        <h2><?php _e('Article Details', 'mega-hub'); ?></h2>
                    </div>
                    <div class="section-content">
                        <p><?php _e('Please provide details for your article below. You can leave fields empty to let the AI fill in the gaps based on the context and information available.', 'mega-hub'); ?></p>
                        <div class="input-group">
                            <label for="article-title"><?php _e('Title:', 'mega-hub'); ?></label>
                            <input type="text" id="article-title" name="article_title" placeholder="<?php esc_attr_e('Your article title...', 'mega-hub'); ?>" class="regular-text" />
                        </div>

                        <div class="input-group">
                            <label for="article-outline"><?php _e('Outline/Plan:', 'mega-hub'); ?></label>
                            <textarea id="article-outline" name="article_outline" placeholder="<?php esc_attr_e('Outline or plan for the article...', 'mega-hub'); ?>" rows="6" class="large-text"></textarea>
                        </div>

                        <div class="input-group">
                            <label for="article-data"><?php _e('Data/Information to Include:', 'mega-hub'); ?></label>
                            <textarea id="article-data" name="article_data" placeholder="<?php esc_attr_e('Any specific data or information to include...', 'mega-hub'); ?>" rows="6" class="large-text"></textarea>
                        </div>
                    </div>
                </div>

                <div class="section">
                    <div class="section-header">
                        <h2><?php _e('Netlinking Options', 'mega-hub'); ?></h2>
                    </div>
                    <div class="section-content">
                        <div class="input-group">
                            <label for="internal-links"><?php _e('Internal Links:', 'mega-hub'); ?></label>
                            <select id="internal-links" name="internal_links">
                                <option value="yes"><?php _e('Yes', 'mega-hub'); ?></option>
                                <option value="no"><?php _e('No', 'mega-hub'); ?></option>
                            </select>
                            <p class="description"><?php _e('If "Yes", internal links specified below will be included instead of those configured in plugin settings.', 'mega-hub'); ?></p>
                        </div>

                        <div class="input-group">
                            <label for="internal-links-to-include"><?php _e('Internal Links to Include:', 'mega-hub'); ?></label>
                            <textarea id="internal-links-to-include" name="internal_links_to_include" placeholder="<?php esc_attr_e('List of internal links to include, one per line...', 'mega-hub'); ?>" rows="4" class="large-text"></textarea>
                        </div>

                        <div class="input-group">
                            <p><?php _e('Leave "Partner URL" empty if no netlinking is required.', 'mega-hub'); ?></p>
                            <label for="partner-url"><?php _e('Partner URL:', 'mega-hub'); ?></label>
                            <input type="url" id="partner-url" name="partner_url" placeholder="<?php esc_attr_e('https://example.com', 'mega-hub'); ?>" class="regular-text">
                        </div>

                        <div class="input-group">
                            <label for="service-description"><?php _e('Service Description:', 'mega-hub'); ?> <span class="required">*</span></label>
                            <textarea id="service-description" name="service_description" placeholder="<?php esc_attr_e('Short description of the partner\'s service (max 150 characters)...', 'mega-hub'); ?>" maxlength="150" rows="3" class="large-text"></textarea>
                        </div>
                    </div>
                </div>


                <script type="text/javascript">
                    document.getElementById('make-it-an-article-form').addEventListener('submit', function(event) {
                        var partnerUrl = document.getElementById('partner-url').value;
                        var serviceDescription = document.getElementById('service-description').value;

                        if (partnerUrl !== '' && serviceDescription === '') {
                            // Empêche la soumission du formulaire
                            event.preventDefault();
                            alert('<?php echo esc_js(__('Service Description is required when Partner URL is provided.', 'mega-hub')); ?>');
                        }
                    });
                </script>




                <div class="section">
                    <div class="section-header">
                        <h2><?php _e('Publishing Options', 'mega-hub'); ?></h2>
                    </div>
                    <div class="section-content">
                        <div class="input-group">
                            <label for="post-status"><?php _e('Post Status:', 'mega-hub'); ?></label>
                            <select id="post-status" name="post_status">
                                <option value="publish"><?php _e('Publish', 'mega-hub'); ?></option>
                                <option value="draft"><?php _e('Draft', 'mega-hub'); ?></option>
                            </select>
                        </div>

                        <div class="input-group">
                            <label for="author"><?php _e('Author:', 'mega-hub'); ?></label>
                            <select id="author" name="author">
                                <?php foreach ($admins as $admin) : ?>
                                    <option value="<?php echo esc_attr($admin->ID); ?>">
                                        <?php echo esc_html($admin->display_name); ?>
                                    </option>
                                <?php endforeach; ?>
                            </select>
                        </div>
                    </div>
                </div>

                

                <div class="submit">
                    <button type="submit" class="button button-primary"><?php _e('Submit', 'mega-hub'); ?></button>
                </div>
            </form>
        </div>


    </div>

    <?php
    // Le script JavaScript pour gérer la soumission du formulaire sera inclus ici
}
