<?php

namespace OtomaticAi\Controllers\Linking;

use OtomaticAi\Controllers\Controller;
use OtomaticAi\Utils\Settings;
use OtomaticAi\Vendors\Illuminate\Validation\Rule;

class AutomaticPagesController extends Controller
{
    /**
     * Get the api settings
     *
     * @return void
     */
    public function index()
    {
        $this->verifyNonce();

        $this->response(Settings::get('linking.pages'));
    }

    /**
     * Update the api settings.
     * 
     * @return void
     */
    public function updateSettings()
    {
        $this->verifyNonce();

        $validated = $this->validate([
            "enabled" => ["boolean"],
            "length" => ["required", "integer", "min:0"],
            "sources.parent" => ["boolean"],
            "sources.children" => ["boolean"],
            "sources.sisters" => ["boolean"],
            "positions.top" => ["boolean"],
            "positions.inter_sections" => ["boolean"],
            "positions.bottom" => ["boolean"],
        ]);

        Settings::update($validated["enabled"], 'linking.pages.enabled');
        Settings::update($validated["length"], 'linking.pages.length');
        Settings::update($validated["sources"], 'linking.pages.sources');
        Settings::update($validated["positions"], 'linking.pages.positions');
        Settings::save();

        $this->emptyResponse();
    }

    public function updateTemplate()
    {
        $this->verifyNonce();

        $validated = $this->validate([
            "display_mode" => ["required", Rule::in(["inline", "grid"])],
            "title.node" => ["nullable", Rule::in("p", "h1", "h2", "h3", "h4", "h5")],
            "title.value" => ["nullable", "string"],
            "settings.grid.columns" => ["required_if:display_mode,grid", "integer", 'min:1', 'max:4'],
            "elements.thumbnail.enabled" => ["boolean"],
            "elements.title.enabled" => ["boolean"],
            "elements.excerpt.enabled" => ["boolean"],
            "elements.excerpt.length" => ["required_if:elements.excerpt.enabled,true", 'integer', 'min:0'],
            "theme.wrapper.padding" => ["nullable", "string"],
            "theme.wrapper.backgroundColor" => ["nullable", "hex_color"],
            "theme.title.color" => ["nullable", "hex_color"],
            "theme.excerpt.color" => ["nullable", "hex_color"],
        ]);

        Settings::update($validated, 'linking.pages.template');
        Settings::save();

        $this->emptyResponse();
    }
}
