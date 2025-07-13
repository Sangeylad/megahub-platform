<?php

namespace OtomaticAi\Utils;

use OtomaticAi\Vendors\Illuminate\Support\Arr;

class Language
{
    public $key;
    public $name;
    public $value;
    public $google_trends;
    public $google_suggests;

    private static $languages = [
        "fr" => [
            "key" => "fr",
            "name" => "French",
            "value" => "français",
            "google_trends" => "FR",
            "google_suggests" => [
                'hl' => 'fr',
                'lr' => 'lang_fr',
                'gl' => 'FR',
            ]
        ],
        "en" => [
            "key" => "en",
            "name" => "English",
            "value" => "anglais",
            "google_trends" => "US",
            "google_suggests" => [
                'hl' => 'en',
                'lr' => 'lang_en',
                'gl' => 'US',
            ]
        ],
        "it" => [
            "key" => "it",
            "name" => "Italian",
            "value" => "italien",
            "google_trends" => "IT",
            "google_suggests" => [
                'hl' => 'it',
                'lr' => 'lang_it',
                'gl' => 'IT',
            ]
        ],
        "de" => [
            "key" => "de",
            "name" => "German",
            "value" => "allemand",
            "google_trends" => "DE",
            "google_suggests" => [
                'hl' => 'de',
                'lr' => 'lang_de',
                'gl' => 'DE',
            ]
        ],
        "es" => [
            "key" => "es",
            "name" => "Spanish",
            "value" => "espagnol",
            "google_trends" => "ES",
            "google_suggests" => [
                'hl' => 'es',
                'lr' => 'lang_es',
                'gl' => 'ES',
            ]
        ],
        "pt" => [
            "key" => "pt",
            "name" => "Portugais",
            "value" => "portugais",
            "google_trends" => "PT",
            "google_suggests" => [
                'hl' => 'pt',
                'lr' => 'lang_pt',
                'gl' => 'PT',
            ]
        ],
        "ru" => [
            "key" => "ru",
            "name" => "Russian",
            "value" => "russe",
            "google_trends" => "RU",
            "google_suggests" => [
                'hl' => 'ru',
                'lr' => 'lang_ru',
                'gl' => 'RU',
            ]
        ],
        "kr" => [
            "key" => "kr",
            "name" => "Korean",
            "value" => "coréen",
            "google_trends" => "KR",
            "google_suggests" => [
                'hl' => 'kr',
                'lr' => 'lang_kr',
                'gl' => 'KR',
            ]
        ],
        "tr" => [
            "key" => "tr",
            "name" => "Turkish",
            "value" => "Turkish",
            "google_trends" => "TR",
            "google_suggests" => [
                'hl' => 'tr',
                'lr' => 'lang_tr',
                'gl' => 'TR',
            ]
        ],
        "nl" => [
            "key" => "nl",
            "name" => "Dutch",
            "value" => "néerlandais",
            "google_trends" => "NL",
            "google_suggests" => [
                'hl' => 'nl',
                'lr' => 'lang_nl',
                'gl' => 'NL',
            ]
        ],
        "ja" => [
            "key" => "ja",
            "name" => "Japanese",
            "value" => "japonais",
            "google_trends" => "JP",
            "google_suggests" => [
                'hl' => 'jp',
                'lr' => 'lang_jp',
                'gl' => 'JP',
            ]
        ],
        "pl" => [
            "key" => "pl",
            "name" => "Polish",
            "value" => "polonais",
            "google_trends" => "PL",
            "google_suggests" => [
                'hl' => 'pl',
                'lr' => 'lang_pl',
                'gl' => 'PL',
            ]
        ],
        "ro" => [
            "key" => "ro",
            "name" => "Romanian",
            "value" => "roumain",
            "google_trends" => "RO",
            "google_suggests" => [
                'hl' => 'ro',
                'lr' => 'lang_ro',
                'gl' => 'RO',
            ]
        ],
        "zh" => [
            "key" => "zh",
            "name" => "Mandarin",
            "value" => "mandarin",
            "google_trends" => "US",
            "google_suggests" => [
                'hl' => 'en',
                'lr' => 'lang_en',
                'gl' => 'US',
            ]
        ],
        "gr" => [
            "key" => "gr",
            "name" => "Grec",
            "value" => "grec",
            "google_trends" => "US",
            "google_suggests" => [
                'hl' => 'en',
                'lr' => 'lang_en',
                'gl' => 'US',
            ]
        ],
        "hi" => [
            "key" => "hi",
            "name" => "Hindi",
            "value" => "hindi",
            "google_trends" => "US",
            "google_suggests" => [
                'hl' => 'en',
                'lr' => 'lang_en',
                'gl' => 'US',
            ]
        ],
        "id" => [
            "key" => "id",
            "name" => "Indonésien",
            "value" => "indonésien",
            "google_trends" => "US",
            "google_suggests" => [
                'hl' => 'en',
                'lr' => 'lang_en',
                'gl' => 'US',
            ]
        ],
        "vi" => [
            "key" => "vi",
            "name" => "Vietnamien",
            "value" => "vietnamien",
            "google_trends" => "US",
            "google_suggests" => [
                'hl' => 'en',
                'lr' => 'lang_en',
                'gl' => 'US',
            ]
        ],
        "th" => [
            "key" => "th",
            "name" => "Thaï",
            "value" => "thaï",
            "google_trends" => "US",
            "google_suggests" => [
                'hl' => 'en',
                'lr' => 'lang_en',
                'gl' => 'US',
            ]
        ],
        "sv" => [
            "key" => "sv",
            "name" => "Suédois",
            "value" => "suédois",
            "google_trends" => "US",
            "google_suggests" => [
                'hl' => 'en',
                'lr' => 'lang_en',
                'gl' => 'US',
            ]
        ],
        "no" => [
            "key" => "no",
            "name" => "Norvégien",
            "value" => "norvégien",
            "google_trends" => "US",
            "google_suggests" => [
                'hl' => 'en',
                'lr' => 'lang_en',
                'gl' => 'US',
            ]
        ],
        "da" => [
            "key" => "da",
            "name" => "Danois",
            "value" => "danois",
            "google_trends" => "US",
            "google_suggests" => [
                'hl' => 'en',
                'lr' => 'lang_en',
                'gl' => 'US',
            ]
        ],
        "hu" => [
            "key" => "hu",
            "name" => "Hongrois",
            "value" => "hongrois",
            "google_trends" => "US",
            "google_suggests" => [
                'hl' => 'en',
                'lr' => 'lang_en',
                'gl' => 'US',
            ]
        ],
        "uk" => [
            "key" => "uk",
            "name" => "Ukrainien",
            "value" => "ukrainien",
            "google_trends" => "US",
            "google_suggests" => [
                'hl' => 'en',
                'lr' => 'lang_en',
                'gl' => 'US',
            ]
        ],
        "ie" => [
            "key" => "ie",
            "name" => "Irlandais",
            "value" => "irlandais",
            "google_trends" => "US",
            "google_suggests" => [
                'hl' => 'en',
                'lr' => 'lang_en',
                'gl' => 'US',
            ]
        ],
        "ar" => [
            "key" => "ar",
            "name" => "Arabe",
            "value" => "arabe",
            "google_trends" => "US",
            "google_suggests" => [
                'hl' => 'en',
                'lr' => 'lang_en',
                'gl' => 'US',
            ]
        ],
        "pk" => [
            "key" => "pk",
            "name" => "Pakistanais",
            "value" => "pakistanais",
            "google_trends" => "US",
            "google_suggests" => [
                'hl' => 'en',
                'lr' => 'lang_en',
                'gl' => 'US',
            ]
        ],
        "pt-BR" => [
            "key" => "pt-BR",
            "name" => "Portugais",
            "value" => "portugais",
            "google_trends" => "US",
            "google_suggests" => [
                'hl' => 'en',
                'lr' => 'lang_en',
                'gl' => 'US',
            ]
        ],
        "zh-TW" => [
            "key" => "zh-TW",
            "name" => "Mandarin",
            "value" => "mandarin",
            "google_trends" => "US",
            "google_suggests" => [
                'hl' => 'en',
                'lr' => 'lang_en',
                'gl' => 'US',
            ]
        ],
    ];

    private static $fallback = "en";

    public function __construct($args)
    {
        $this->key = $args["key"];
        $this->name = $args["name"];
        $this->value = $args["value"];
        $this->google_trends = $args["google_trends"];
        $this->google_suggests = $args["google_suggests"];
    }

    static public function find($key = "en")
    {
        return new self(Arr::get(self::$languages, $key, Arr::get(self::$languages, self::$fallback)));
    }

    static public function findFromLocale()
    {
        $locale = get_locale();
        return self::find(explode("_", $locale)[0]);
    }
}
