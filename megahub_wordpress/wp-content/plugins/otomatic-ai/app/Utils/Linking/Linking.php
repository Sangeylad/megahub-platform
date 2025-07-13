<?php

namespace OtomaticAi\Utils\Linking;

use OtomaticAi\Utils\Auth;
use WP_Post;

class Linking
{
    private AutomaticLinking $automatic;
    private ManualLinking $manual;

    public function __construct(WP_POST $post)
    {
        $this->automatic = new AutomaticLinking($post);
        $this->manual = new ManualLinking($post);
    }

    /**
     * add linking to the content
     *
     * @param string $content
     * @return string
     */
    public function run(string $content): string
    {
        // run manual linking
        $content = $this->manual->run($content);

        // run automatic linking
        $content = $this->automatic->run($content);

        return $content;
    }

    static public function filter(string $content): string
    {
        if (!Auth::isPremium() || !Auth::isTrial()) {
            return $content;
        }

        $post = get_post();
        if (!empty($post)) {
            $linking = new self($post);
            return $linking->run($content);
        }

        return $content;
    }
}
