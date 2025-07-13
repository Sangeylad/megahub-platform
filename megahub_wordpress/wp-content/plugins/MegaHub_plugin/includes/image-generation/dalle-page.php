<?php


function mega_hub_dalle_image_generator_page() {
    ?>
    <div class="wrap">
        <h1><?php _e('Dalle Image Generator', 'mega-hub'); ?></h1>
        <div style="display: flex;">
            <div style="flex-grow: 1; margin-right: 20px;">
                <textarea id="mega-hub-dalle-prompt" rows="4" style="width: 85%;" placeholder="<?php _e('Enter your prompt here...', 'mega-hub'); ?>"></textarea>
            </div>
            <div style="display: flex; flex-direction: column; justify-content: space-between;">
                <select id="mega-hub-dalle-model" style="margin-bottom: 10px;">
                    <option value="dall-e-3"><?php _e('Dall-E 3', 'mega-hub'); ?></option>
                    <option value="dall-e-2"><?php _e('Dall-E 2', 'mega-hub'); ?></option>
                </select>
                <select id="mega-hub-dalle-size" style="margin-bottom: 10px;">
                    <option value="1024x1024">1024x1024</option>
                    <option value="1024x1792">1024x1792</option>
                    <option value="1792x1024">1792x1024</option>
                </select>
                <button type="button" id="mega-hub-dalle-submit" class="button-primary" style="align-self: flex-start;">Generate</button>
            </div>
        </div>
        <!-- Section pour afficher la bibliothèque d'images générées -->
        <div id="mega-hub-dalle-library">
            <!-- Les images générées seront affichées ici -->
        </div>
    </div>
    <?php
}