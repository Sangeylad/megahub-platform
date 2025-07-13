<?php


function mega_hub_content_tools_page() {
    ?>
    <div class="wrap">
    <h1><?php _e('Content Tools', 'mega-hub'); ?></h1>
    <p><?php _e('Use the following shortcodes to enhance your content:', 'mega-hub'); ?></p>
    
    <h2><?php _e('Available Shortcodes', 'mega-hub'); ?></h2>
    <table class="widefat">
        <thead>
            <tr>
                <th><?php _e('Shortcode', 'mega-hub'); ?></th>
                <th><?php _e('Description', 'mega-hub'); ?></th>
            </tr>
        </thead>
        <tbody>
            <!-- Informations générales -->
            <tr>
                <td><code>[current_year]</code></td>
                <td><?php _e('Displays the current year. Useful for copyright notices and Titles/meta-titles', 'mega-hub'); ?></td>
            </tr>
            <tr>
                <td><code>[read_time]</code></td>
                <td><?php _e('Estimates and displays the reading time for a post or page.', 'mega-hub'); ?></td>
            </tr>

            <!-- Contenu enrichi -->
            <tr>
                <td><code>[highlight]</code>...<code>[/highlight]</code></td>
                <td><?php _e('Highlights the enclosed text to draw attention. Example: [highlight]important[/highlight]', 'mega-hub'); ?></td>
            </tr>
            <tr>
                <td><code>[tooltip text="..."]</code>...<code>[/tooltip]</code></td>
                <td><?php _e('Adds a tooltip to the enclosed text. Example: [tooltip text="Extra info"]hover over me[/tooltip]', 'mega-hub'); ?></td>
            </tr>

            <!-- Interactivité -->
            <tr>
                <td><code>[collapsible title="Your Title" tag="h2"]...[/collapsible]</code></td>
                <td><?php _e('Creates a collapsible content block with a customizable title and SEO-friendly heading tag. The "title" attribute sets the section title, and the "tag" attribute allows you to choose the heading tag (e.g., h2, h3) for better SEO. Wrap your content within the shortcode to make it collapsible. Example: [collapsible title="View More" tag="h3"]Your content here[/collapsible]', 'mega-hub'); ?></td>
            </tr>

            <tr>
                <td><code>[countdown date="YYYY-MM-DD"]</code></td>
                <td><?php _e('Displays a countdown to a specific date. Example: [countdown date="2024-12-31"]', 'mega-hub'); ?></td>
            </tr>

            <!-- Outils visuels -->
            <tr>
                <td><code>[qr_code data="URL" size="150"]</code></td>
                <td><?php _e('Generates a QR code for the given URL. Example: [qr_code data="https://example.com" size="150"]', 'mega-hub'); ?></td>
            </tr>
            <tr>
                <td><code>[embed_pdf src="URL_DU_PDF" width="600" height="500"]</code></td>
                <td><?php _e('Embeds a PDF file into the content. Example: [embed_pdf src="http://example.com/file.pdf" width="600" height="500"]', 'mega-hub'); ?></td>
            </tr>

            <!-- Sécurité & Accès -->
            <tr>
                <td><code>[content_protector password="yourpassword"]</code>...<code>[/content_protector]</code></td>
                <td><?php _e('Protects the enclosed content with a password. Only users who enter the correct password can view the content. Example: [content_protector password="secret"]protected content[/content_protector]', 'mega-hub'); ?></td>
            </tr>
            <tr>
                <td><code>[for_logged_in]</code>...<code>[/for_logged_in]</code></td>
                <td><?php _e('Displays the enclosed content only to logged-in users. Use this shortcode to restrict certain content to members or registered users of your site.', 'mega-hub'); ?></td>
            </tr>
            <tr>
                <td><code>[for_guests]</code>...<code>[/for_guests]</code></td>
                <td><?php _e('Displays the enclosed content only to logged-out visitors. Ideal for presenting signup incentives or welcome messages to new visitors.', 'mega-hub'); ?></td>
            </tr>
            <tr>
                <td><code>[current_month]</code></td>
                <td><?php _e('Displays the current month. Ideal for monthly updates or to add a temporal touch to your content.', 'mega-hub'); ?></td>
            </tr>
            <tr>
                <td><code>[visitor_count]</code></td>
                <td><?php _e('Counts and displays the number of times the page has been visited during the current session. A simple way to indicate page or article popularity.', 'mega-hub'); ?></td>
            </tr>


        </tbody>
    </table>
</div>

    <?php
}



