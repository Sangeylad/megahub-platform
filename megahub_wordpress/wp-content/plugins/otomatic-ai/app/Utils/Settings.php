<?php

namespace OtomaticAi\Utils;

use OtomaticAi\Vendors\Illuminate\Support\Arr;

abstract class Settings
{
    const OPTION_NAME = "otomatic_ai_settings";

    static private $data;
    static private $initialized = false;

    static private $defaults = [
        "api" => [
            "openai" => [
                "api_key" => "",
                "organization" => "",
            ],
            "mistral_ai" => [
                "api_key" => "",
            ],
            "stability_ai" => [
                "api_key" => "",
            ],
            "unsplash" => [
                "api_key" => ""
            ],
            "pexels" => [
                "api_key" => ""
            ],
            "pixabay" => [
                "api_key" => ""
            ],
            "haloscan" => [
                "api_key" => ""
            ],
            "groq" => [
                "api_key" => ""
            ]
        ],
        "linking" => [
            "posts" => [
                "enabled" => false,
                "sources" => [
                    "categories" => true,
                    "tags" => true,
                ],
                "length" => 8,
                "orderby" => "date",
                "positions" => [
                    "top" => false,
                    "inter_sections" => true,
                    "bottom" => true,
                ],
                "template" => [
                    "title" => [
                        "node" => "h3",
                        "value" => null,
                    ],
                    "display_mode" => "grid",
                    "settings" => [
                        "grid" => [
                            "columns" => 3,
                        ]
                    ],
                    "elements" => [
                        "thumbnail" => [
                            "enabled" => true,
                        ],
                        "title" => [
                            "enabled" => true,
                        ],
                        "excerpt" => [
                            "enabled" => true,
                            "length" => 40,
                        ],
                    ],
                    "theme" => [
                        "wrapper" => [
                            "padding" => null,
                            "backgroundColor" => null,
                        ],
                        "title" => [
                            "color" => null,
                        ],
                        "excerpt" => [
                            "color" => null,
                        ]
                    ]
                ]
            ],
            "pages" => [
                "enabled" => false,
                "sources" => [
                    "parent" => false,
                    "children" => true,
                    "sisters" => true,
                ],
                "length" => 0,
                "positions" => [
                    "top" => false,
                    "inter_sections" => true,
                    "bottom" => true,
                ],
                "template" => [
                    "title" => [
                        "node" => "h3",
                        "value" => null,
                    ],
                    "display_mode" => "grid",
                    "settings" => [
                        "grid" => [
                            "columns" => 3,
                        ]
                    ],
                    "elements" => [
                        "thumbnail" => [
                            "enabled" => true,
                        ],
                        "title" => [
                            "enabled" => true,
                        ],
                        "excerpt" => [
                            "enabled" => true,
                            "length" => 40,
                        ],
                    ],
                    "theme" => [
                        "wrapper" => [
                            "padding" => null,
                            "backgroundColor" => null,
                        ],
                        "title" => [
                            "color" => null,
                        ],
                        "excerpt" => [
                            "color" => null,
                        ]
                    ]
                ]
            ],
        ]
    ];

    static public function get($key = null, $default = null)
    {
        if (!self::$initialized) {
            self::$data = get_option(self::OPTION_NAME, []);
            self::$data = array_replace_recursive(self::$defaults, self::$data);
            self::$initialized = true;
        }

        if ($key === null) {
            return self::$data;
        }
        return Arr::get(self::$data, $key, $default);
    }

    static public function update($value, $key = null)
    {
        $data = self::get();
        if ($key === null) {
            $data = $value;
        }
        Arr::set($data, $key, $value);

        self::$data = $data;

        return self::$data;
    }

    static public function save()
    {
        return update_option(self::OPTION_NAME, self::get(), true);
    }
}
