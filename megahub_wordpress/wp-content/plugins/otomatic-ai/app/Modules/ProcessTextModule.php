<?php

namespace OtomaticAi\Modules;

use Exception;
use OtomaticAi\Content\Html\ParagraphElement;
use OtomaticAi\Content\Section;
use OtomaticAi\Content\SectionCollection;
use OtomaticAi\Modules\Contracts\Module as ModuleContract;
use OtomaticAi\Models\Publication;
use OtomaticAi\Models\Preset;
use OtomaticAi\Utils\GoogleNews;
use OtomaticAi\Utils\HtmlParser;
use OtomaticAi\Utils\RobotsTxt;
use OtomaticAi\Vendors\Illuminate\Support\Arr;
use OtomaticAi\Vendors\Illuminate\Support\Str;
use OtomaticAi\Vendors\andreskrey\Readability\Readability;
use OtomaticAi\Vendors\andreskrey\Readability\Configuration;

class ProcessTextModule implements ModuleContract
{
    /**
     * The publication
     *
     * @var Publication
     */
    private Publication $publication;

    private $persona;

    /**
     * Create a new job instance.
     *
     * @param Publication $publication
     */
    public function __construct(Publication $publication)
    {
        $this->publication = $publication;
    }

    /**
     * Execute the job.
     *
     * @return void
     * @throws Exception
     */
    public function handle(): void
    {
        // verify that the job is runnable
        if (!self::isRunnable($this->publication)) {
            return;
        }

        // log the start of the job
        $this->publication->addLog("Text module started.");

        // perform the correct text model
        if ($this->publication->project->type === "news" || $this->publication->project->type === "news-now") {
            $this->createNewsSections();
        } else if ($this->publication->project->type === "rss" || $this->publication->project->type === "rss-now") {
            $this->createRssSections();
        } else if ($this->publication->project->type === "sitemap") {
            $this->createSitemapSections();
        } else if ($this->publication->project->type === "url") {
            $this->createUrlSections();
        } else if (Arr::get($this->publication->project->modules, 'text.custom_preset.enabled', false)) {
            $this->createCustomPresetSections();
        } else {
            $this->createStructureSections();
        }

        // log the end of the job
        if ($this->publication->sections->isNotEmpty()) {
            $this->publication->addLog("Text module completed successfully.", "success");
        } else {
            $this->publication->addLog("Text module completed with errors. No content generated.", "error");
        }
    }

    /**
     * Generate news sections
     *
     * @return void
     * @throws Exception
     */
    private function createNewsSections()
    {
        // get the meta.url
        $url = Arr::get($this->publication->meta, 'url');
        if (empty($url)) {
            throw new Exception("News url is empty.");
        }

        $this->createScrapingSections($url);
    }

    /**
     * Generate rss sections
     *
     * @return void
     * @throws Exception
     */
    private function createRssSections()
    {
        // get the meta.url
        $url = Arr::get($this->publication->meta, 'url');
        if (empty($url)) {
            throw new Exception("Rss url is empty.");
        }

        $this->createScrapingSections($url);
    }

    /**
     * Generate sitemap sections
     *
     * @return void
     * @throws Exception
     */
    private function createSitemapSections()
    {
        // get the meta.url
        $url = Arr::get($this->publication->meta, 'url');
        if (empty($url)) {
            throw new Exception("Url is empty.");
        }

        $this->createScrapingSections($url);
    }

    /**
     * Generate url sections
     *
     * @return void
     * @throws Exception
     */
    private function createUrlSections()
    {
        // get the meta.url
        $url = Arr::get($this->publication->meta, 'url');
        if (empty($url)) {
            throw new Exception("Url is empty.");
        }

        $this->createScrapingSections($url);
    }

    private function createScrapingSections(string $url)
    {
        // verify robots txt
        if ($this->isDisabledByRobotsTxt($url)) {
            throw new Exception("Disabled by robots.txt.");
        }

        // scrap the meta.url content
        $response = wp_remote_get($url, [
            "headers" => [
                "User-Agent" => "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
            ]
        ]);

        // quit if the content is not usable
        if (is_wp_error($response) || empty($body = Arr::get($response, "body")) || strlen($body) < 200) {
            return;
        }

        $content = null;
        try {
            // remove boilerplate frop body
            $configuration = new Configuration([
                "articleByLine" => true,
                "summonCthulhu" => true,
                "normalizeEntities" => true,
            ]);
            $readability = new Readability($configuration);
            $readability->parse($body);
            $content = $readability->getContent();
        } catch (Exception $e) {
        }

        // quit if the content is empty
        if (empty($content)) {
            return;
        }

        // get the openai preset
        switch (self::getOpenAIModel($this->publication, 'text.model')) {
            case "mistral-large":
                $preset = Preset::findFromAPI("news_content_v3_mistral_large");
                break;
            case "gpt-4o":
                $preset = Preset::findFromAPI("news_content_v3_openai_gpt_4o");
                break;
            case "gpt-4":
            case "gpt-4-turbo":
                $preset = Preset::findFromAPI("news_content_v3_openai_gpt_4_turbo");
                break;
            default:
                $preset = Preset::findFromAPI("news_content_v3_openai_gpt_3_5_turbo");
        }

        // persona
        $persona = $this->getPersona();

        // buyer persona
        $buyerPersona = $this->getBuyerPersona();

        // custom instructions
        $customInstructions =  $this->getCustomInstructions();

        // writing style
        $writingStyle = $this->getWritingStyle();

        // external links
        $links = $this->getExternalLinks($this->publication->generation_title);
        $links = Arr::random($links, min(count($links), 10));
        $externalLinksLinks =  array_map(function ($item) {
            return $item["url"];
        }, $links);
        $externalLinksTitles = array_map(function ($item) {
            return $item["title"];
        }, $links);

        // rewrite the content
        $parser = $this->createContent($preset, [
            "language" => $this->publication->project->language->value,
            "request" => $this->publication->generation_title,
            "title" => $this->publication->generation_title,
            "content" => $content,
            "persona" => $persona,
            "has_persona" => !empty($persona),
            "buyer_persona" => $buyerPersona,
            "has_buyer_persona" => !empty($buyerPersona),
            "custom_instructions" => $customInstructions,
            "has_custom_instructions" => !empty($customInstructions),
            "has_external_links" => Arr::get($this->publication->project->modules, 'text.external_links.enabled', false) && count($links),
            "external_links_links" => implode("\n", $externalLinksLinks),
            "external_links_titles" => implode("\n", $externalLinksTitles),
            "writing_style" => $writingStyle,
            "has_writing_style" => !empty($writingStyle),
            "has_introduction" => Arr::get($this->publication->project->modules, 'text.options.introduction.enabled', false),
            "has_summary" => Arr::get($this->publication->project->modules, 'text.options.summary.enabled', false),
            "has_brief" => Arr::get($this->publication->project->modules, 'text.options.brief.enabled', false),
            "has_bold_words" => Arr::get($this->publication->project->modules, 'text.options.bold_words.enabled', false),
            "has_table" => Arr::get($this->publication->project->modules, 'text.options.table.enabled', false),
            "has_list" => Arr::get($this->publication->project->modules, 'text.options.list.enabled', false),
            "has_faq" => Arr::get($this->publication->project->modules, 'text.options.faq.enabled', false),
        ]);

        // save the publication sections
        if ($parser) {

            $sections = $parser->getSections([
                "blacklist_titles" => [$this->publication->generation_title]
            ]);

            if ($sections->isNotEmpty()) {

                // generate summary
                if (Arr::get($this->publication->project->modules, "text.options.summary.enabled", false)) {
                    $summary = $this->generateNewsSummary($sections->toText());
                    if (!empty($summary)) {
                        $section = new Section();
                        $section->addChild($summary->getSections([
                            "blacklist_titles" => [$this->publication->generation_title]
                        ]));
                        $sections->prepend($section);
                    }
                }

                // generate introduction
                $introduction = $this->generateNewsIntroduction($sections->toText());
                if (!empty($introduction)) {
                    $section = new Section();
                    $section->addChild($introduction->getSections([
                        "blacklist_titles" => [$this->publication->generation_title]
                    ]));
                    $sections->prepend($section);
                }

                // generate brief
                if (Arr::get($this->publication->project->modules, "text.options.brief.enabled", false)) {
                    $brief = $this->generateNewsBrief($sections->toText());
                    if (!empty($brief)) {
                        $section = new Section();
                        $section->addChild($brief->getSections([
                            "blacklist_titles" => [$this->publication->generation_title]
                        ]));
                        $sections->prepend($section);
                    }
                }

                // add sources
                if (Arr::get($this->publication->project->modules, "text.sources.enabled", false)) {
                    $s = $this->createSourcesSection([$url]);
                    if ($s !== null) {
                        $sections->push($s);
                    }
                }

                $this->publication->sections = $sections;
            }
        }
    }

    /**
     * Generate custom preset sections
     *
     * @return void
     * @throws Exception
     */
    private function createCustomPresetSections()
    {
        // persona
        $persona = $this->getPersona();

        // buyer persona
        $buyerPersona = $this->getBuyerPersona();

        // custom instructions
        $customInstructions =  $this->getCustomInstructions();

        // writing style
        $writingStyle = $this->getWritingStyle();

        // create the generation title
        $generationTitle = $this->publication->generation_title;
        try {

            // get the preset
            $preset = Preset::findFromAPI("rewrite_subtitle");

            // run the preset
            $response = $preset->process([
                "language" => $this->publication->project->language->value,
                "request" => $this->publication->generation_title,
            ]);

            // get the response content
            $response = json_decode(Arr::get($response, 'choices.0.message.content'), true, 512, JSON_THROW_ON_ERROR);
            $content = Arr::get($response, "value");
            $content = Str::clean($content);

            if (!empty($content)) {
                $generationTitle = $content;
            }
        } catch (Exception $e) {
        }

        // get external links
        $links = $this->getExternalLinks($generationTitle);
        if (count($links) > 0) {
            $links = Arr::random($links, min(count($links), 10));
        }

        $externalLinksLinks =  array_map(function ($item) {
            return $item["url"];
        }, $links);
        $externalLinksTitles = array_map(function ($item) {
            return $item["title"];
        }, $links);

        // create the preset
        $userMessage = Arr::get($this->publication->project->modules, "text.custom_preset.prompt", "");
        $userMessage = $userMessage . implode("\n", [
            "",
            "[IF;HAS_EXTERNAL_LINKS]",
            "Si besoin voici une liste de liens à utiliser et à lier sur les mots clé ciblés dans le texte :",
            "[EXTERNAL_LINKS_LINKS]",
            "",
            "Evite les phrase du type : consulter l'article ou cet article, soit plus créatif.",
            "N'integre pas d'ancre de lien type : ce lien. ici.",
            "Les articles lié au liens ne sont pas nos article ou guide, mais des références externes.",
            "[ENDIF]",
        ]);

        $preset = Preset::make([
            "model" => $this->getOpenAIModel($this->publication),
            "messages" => [
                [
                    "role" => "user",
                    "content" => $userMessage
                ]
            ],
            "temperature" => Arr::get($this->publication->project->modules, "text.custom_preset.temperature", 1),
            "top_p" => Arr::get($this->publication->project->modules, "text.custom_preset.top_p", 1),
            "presence_penalty" => Arr::get($this->publication->project->modules, "text.custom_preset.presence_penalty", 0),
            "frequency_penalty" => Arr::get($this->publication->project->modules, "text.custom_preset.frequency_penalty", 0),
        ]);

        // create the content
        $parser = $this->createContent($preset, [
            "language" => $this->publication->project->language->value,
            "request" => $this->publication->generation_title,
            "persona" => $persona,
            "buyer_persona" => $buyerPersona,
            "custom_instructions" => "",
            "writing_style" => $writingStyle,
            "has_external_links" => Arr::get($this->publication->project->modules, 'text.external_links.enabled', false) && count($links),
            "external_links_links" => implode("\n", $externalLinksLinks),
            "external_links_titles" => implode("\n", $externalLinksTitles),
        ]);

        // save the publication sections
        if ($parser) {
            $this->publication->sections = $parser->getSections([
                "blacklist_titles" => [$this->publication->generation_title]
            ]);
        }
    }

    /**
     * Generate structure sections
     *
     * @return void
     * @throws Exception
     */
    private function createStructureSections()
    {
        // create the structure
        $structure = $this->createStructure();
        if (empty($structure)) {
            throw new Exception("Failed to create the structure.");
        }

        // get the openai preset
        switch (self::getOpenAIModel($this->publication)) {
            case "groq-llama3-8b":
                $preset = Preset::findFromAPI("structure_content_v4_groq_llama3_8b");
                break;
            case "groq-llama3-8b":
                $preset = Preset::findFromAPI("structure_content_v3_groq_llama3_8b");
                break;
            case "groq-llama3-70b":
                $preset = Preset::findFromAPI("structure_content_v4_groq_llama3_8b");
                break;
            case "mistral-medium":
                $preset = Preset::findFromAPI("structure_content_v4_mistral_medium");
                break;
            case "mistral-large":
                $preset = Preset::findFromAPI("structure_content_v4_mistral_large");
                break;
            case "gpt-4":
                $preset = Preset::findFromAPI("structure_content_v4_openai_gpt_4");
                break;
            case "gpt-4o":
                $preset = Preset::findFromAPI("structure_content_v4_openai_gpt_4o");
                break;
            case "gpt-4-turbo":
                $preset = Preset::findFromAPI("structure_content_v4_openai_gpt_4_turbo");
                break;
            default:
                $preset = Preset::findFromAPI("structure_content_v4_openai_gpt_3_5_turbo");
        }

        // create the content for each sections
        $sections = new SectionCollection();

        // persona
        $persona = $this->getPersona();

        // buyer persona
        $buyerPersona = $this->getBuyerPersona();

        // custom instructions
        $customInstructions =  $this->getCustomInstructions();

        // writing style
        $writingStyle = $this->getWritingStyle();

        // make payloads
        $payloads = [];
        foreach ($structure as $h2) {
            $linksIndex = 0;

            // get external links
            $links = $this->getExternalLinks($h2["title"]);
            $links = Arr::shuffle($links);
            $chunkLinks = Arr::partition($links, 1 + count(Arr::get($h2, "children", [])));

            // take links for the current h2
            $h2Links = Arr::random($chunkLinks[$linksIndex], min(count($chunkLinks[$linksIndex]), 10));
            $externalLinksLinks =  array_map(function ($item) {
                return $item["url"];
            }, $h2Links);
            $externalLinksTitles = array_map(function ($item) {
                return $item["title"];
            }, $h2Links);
            $linksIndex++;

            $payloads[] = [
                "language" => $this->publication->project->language->value,
                "title" => $this->publication->generation_title,
                "request" => $this->publication->generation_title,
                "h2_title" => $h2["title"],
                "h3_title" => '',
                "is_h2" => true,
                "is_h3" => false,
                "persona" => $persona,
                "has_persona" => !empty($persona),
                "buyer_persona" => $buyerPersona,
                "has_buyer_persona" => !empty($buyerPersona),
                "custom_instructions" => $customInstructions,
                "has_custom_instructions" => !empty($customInstructions),
                "writing_style" => $writingStyle,
                "has_writing_style" => !empty($writingStyle),
                "has_external_links" => Arr::get($this->publication->project->modules, 'text.external_links.enabled', false) && count($links),
                "external_links_links" => implode("\n", $externalLinksLinks),
                "external_links_titles" => implode("\n", $externalLinksTitles),
                "has_bold_words" => Arr::get($this->publication->project->modules, 'text.options.bold_words.enabled', false),
            ];

            foreach (Arr::get($h2, "children", []) as $h3) {

                // take links for the current h3
                $h3Links = Arr::random($chunkLinks[$linksIndex], min(count($chunkLinks[$linksIndex]), 10));
                $externalLinksLinks =  array_map(function ($item) {
                    return $item["url"];
                }, $h3Links);
                $externalLinksTitles = array_map(function ($item) {
                    return $item["title"];
                }, $h3Links);
                $linksIndex++;

                $payloads[] = [
                    "language" => $this->publication->project->language->value,
                    "title" => $this->publication->generation_title,
                    "request" => $this->publication->generation_title,
                    "h2_title" => $h2["title"],
                    "h3_title" => $h3["title"],
                    "persona" => $persona,
                    "is_h2" => false,
                    "is_h3" => true,
                    "has_persona" => !empty($persona),
                    "buyer_persona" => $buyerPersona,
                    "has_buyer_persona" => !empty($buyerPersona),
                    "custom_instructions" => $customInstructions,
                    "has_custom_instructions" => !empty($customInstructions),
                    "writing_style" => $writingStyle,
                    "has_writing_style" => !empty($writingStyle),
                    "has_external_links" => Arr::get($this->publication->project->modules, 'text.external_links.enabled', false) && count($links),
                    "external_links_links" => implode("\n", $externalLinksLinks),
                    "external_links_titles" => implode("\n", $externalLinksTitles),
                    "has_bold_words" => Arr::get($this->publication->project->modules, 'text.options.bold_words.enabled', false),
                ];
            }
        }

        // create the contents
        $parsers = $this->createMultiContent($preset, $payloads);

        // create the sections for contents
        $index = 0;
        foreach ($structure as $h2) {
            $h2Section = new Section($h2["title"]);
            $h2Section->addChild($parsers[$index]->getSections([
                "keep_titles" => false
            ]));

            $index++;

            foreach (Arr::get($h2, "children", []) as $h3) {
                if (!empty($parsers[$index])) {
                    $h3Section = new Section($h3["title"]);
                    $h3Section->addChild($parsers[$index]->getSections([
                        "keep_titles" => false
                    ]));
                    $h2Section->addChild($h3Section);
                }
                $index++;
            }

            $sections->push($h2Section);
        }

        if ($sections->isNotEmpty()) {

            // generate summary
            if (Arr::get($this->publication->project->modules, "text.options.summary.enabled", false)) {
                $summary = $this->generateSummary($sections->toText());
                if (!empty($summary)) {
                    $section = new Section();
                    $section->addChild($summary->getSections([
                        "blacklist_titles" => [$this->publication->generation_title]
                    ]));
                    $sections->prepend($section);
                }
            }

            // generate introduction
            if (Arr::get($this->publication->project->modules, "text.options.introduction.enabled", false)) {
                $introduction = $this->generateIntroduction($sections->toText());
                if (!empty($introduction)) {
                    $section = new Section();
                    $section->addChild($introduction->getSections([
                        "blacklist_titles" => [$this->publication->generation_title]
                    ]));
                    $sections->prepend($section);
                }
            }

            // generate brief
            if (Arr::get($this->publication->project->modules, "text.options.brief.enabled", false)) {
                $brief = $this->generateBrief($sections->toText());
                if (!empty($brief)) {
                    $section = new Section();
                    $section->addChild($brief->getSections([
                        "blacklist_titles" => [$this->publication->generation_title]
                    ]));
                    $sections->prepend($section);
                }
            }

            // generate table
            if (Arr::get($this->publication->project->modules, "text.options.table.enabled", false)) {
                $table = $this->generateTable($sections->toText());
                if (!empty($table)) {
                    $section = new Section();
                    $section->addChild($table->getSections([
                        "blacklist_titles" => [$this->publication->generation_title]
                    ]));
                    $sections->get(intval(floor(($sections->count() - 1) / 2)))->addChild($section);
                }
            }

            // generate list
            if (Arr::get($this->publication->project->modules, "text.options.list.enabled", false)) {
                $list = $this->generateList($sections->toText());
                if (!empty($list)) {
                    $section = new Section();
                    $section->addChild($list->getSections([
                        "blacklist_titles" => [$this->publication->generation_title]
                    ]));
                    $sections->get(intval(floor(($sections->count() - 1) / 2)))->addChild($section);
                }
            }

            // generate faq
            if (Arr::get($this->publication->project->modules, "text.options.faq.enabled", false)) {
                $faq = $this->generateFAQ($sections->toText());
                if (!empty($faq)) {
                    $section = new Section();
                    $section->addChild($faq->getSections([
                        "blacklist_titles" => [$this->publication->generation_title]
                    ]));
                    $sections->push($section);
                }
            }
        }

        // save the publication sections
        if ($sections->isNotEmpty()) {
            $this->publication->sections = $sections;
        }
    }

    private function generateIntroduction(string $content)
    {
        try {
            // get the openai preset
            $preset = Preset::findFromAPI("introduction_openai_gpt_3_5_turbo");

            // persona
            $persona = $this->getPersona();

            // buyer persona
            $buyerPersona = $this->getBuyerPersona();

            // writing style
            $writingStyle = $this->getWritingStyle();

            // run the preset
            $response = $preset->process([
                "language" => $this->publication->project->language->value,
                "request" => $this->publication->generation_title,
                "title" => $this->publication->generation_title,
                "persona" => $persona,
                "has_persona" => !empty($persona),
                "buyer_persona" => $buyerPersona,
                "has_buyer_persona" => !empty($buyerPersona),
                "writing_style" => $writingStyle,
                "has_writing_style" => !empty($writingStyle),
            ]);

            // get the response content
            $content = Arr::get($response, 'choices.0.message.content');
            if ($content) {
                // parse content
                return new HtmlParser($content);
            }
        } catch (Exception $e) {
        }
    }

    private function generateSummary(string $content)
    {
        try {
            $preset = Preset::findFromAPI("summary_openai_gpt_3_5_turbo");

            // persona
            $persona = $this->getPersona();

            // buyer persona
            $buyerPersona = $this->getBuyerPersona();

            // writing style
            $writingStyle = $this->getWritingStyle();

            // run the preset
            $response = $preset->process([
                "language" => $this->publication->project->language->value,
                "title" => $this->publication->generation_title,
                "request" => $this->publication->generation_title,
                "content" => $content,
                "persona" => $persona,
                "has_persona" => !empty($persona),
                "buyer_persona" => $buyerPersona,
                "has_buyer_persona" => !empty($buyerPersona),
                "writing_style" => $writingStyle,
                "has_writing_style" => !empty($writingStyle),
            ]);

            // get the response content
            $content = Arr::get($response, 'choices.0.message.content');
            if ($content) {
                // parse content
                return new HtmlParser($content);
            }
        } catch (Exception $e) {
        }
    }

    private function generateBrief(string $content)
    {
        try {
            $preset = Preset::findFromAPI("brief_openai_gpt_3_5_turbo");

            // persona
            $persona = $this->getPersona();

            // buyer persona
            $buyerPersona = $this->getBuyerPersona();

            // writing style
            $writingStyle = $this->getWritingStyle();

            // run the preset
            $response = $preset->process([
                "language" => $this->publication->project->language->value,
                "title" => $this->publication->generation_title,
                "request" => $this->publication->generation_title,
                "content" => $content,
                "persona" => $persona,
                "has_persona" => !empty($persona),
                "buyer_persona" => $buyerPersona,
                "has_buyer_persona" => !empty($buyerPersona),
                "writing_style" => $writingStyle,
                "has_writing_style" => !empty($writingStyle),
            ]);

            // get the response content
            $content = Arr::get($response, 'choices.0.message.content');
            if ($content) {
                // parse content
                return new HtmlParser($content);
            }
        } catch (Exception $e) {
        }
    }

    private function generateNewsIntroduction(string $content)
    {
        try {
            // get the openai preset
            $preset = Preset::findFromAPI("introduction_news_openai_gpt_3_5_turbo");

            // persona
            $persona = $this->getPersona();

            // buyer persona
            $buyerPersona = $this->getBuyerPersona();

            // writing style
            $writingStyle = $this->getWritingStyle();

            // run the preset
            $response = $preset->process([
                "language" => $this->publication->project->language->value,
                "title" => $this->publication->generation_title,
                "request" => $this->publication->generation_title,
                "content" => $content,
                "persona" => $persona,
                "has_persona" => !empty($persona),
                "buyer_persona" => $buyerPersona,
                "has_buyer_persona" => !empty($buyerPersona),
                "writing_style" => $writingStyle,
                "has_writing_style" => !empty($writingStyle),
            ]);

            // get the response content
            $content = Arr::get($response, 'choices.0.message.content');
            if ($content) {
                // parse content
                return new HtmlParser($content);
            }
        } catch (Exception $e) {
        }
    }

    private function generateNewsSummary(string $content)
    {
        try {
            $preset = Preset::findFromAPI("summary_news_openai_gpt_3_5_turbo");

            // persona
            $persona = $this->getPersona();

            // buyer persona
            $buyerPersona = $this->getBuyerPersona();

            // writing style
            $writingStyle = $this->getWritingStyle();

            // run the preset
            $response = $preset->process([
                "language" => $this->publication->project->language->value,
                "title" => $this->publication->generation_title,
                "request" => $this->publication->generation_title,
                "content" => $content,
                "persona" => $persona,
                "has_persona" => !empty($persona),
                "buyer_persona" => $buyerPersona,
                "has_buyer_persona" => !empty($buyerPersona),
                "writing_style" => $writingStyle,
                "has_writing_style" => !empty($writingStyle),
            ]);

            // get the response content
            $content = Arr::get($response, 'choices.0.message.content');
            if ($content) {
                // parse content
                return new HtmlParser($content);
            }
        } catch (Exception $e) {
        }
    }

    private function generateNewsBrief(string $content)
    {
        try {
            $preset = Preset::findFromAPI("brief_news_openai_gpt_3_5_turbo");

            // persona
            $persona = $this->getPersona();

            // buyer persona
            $buyerPersona = $this->getBuyerPersona();

            // writing style
            $writingStyle = $this->getWritingStyle();

            // run the preset
            $response = $preset->process([
                "language" => $this->publication->project->language->value,
                "title" => $this->publication->generation_title,
                "request" => $this->publication->generation_title,
                "content" => $content,
                "persona" => $persona,
                "has_persona" => !empty($persona),
                "buyer_persona" => $buyerPersona,
                "has_buyer_persona" => !empty($buyerPersona),
                "writing_style" => $writingStyle,
                "has_writing_style" => !empty($writingStyle),
            ]);

            // get the response content
            $content = Arr::get($response, 'choices.0.message.content');
            if ($content) {
                // parse content
                return new HtmlParser($content);
            }
        } catch (Exception $e) {
        }
    }

    private function generateFAQ(string $content)
    {
        try {
            $preset = Preset::findFromAPI("faq_openai_gpt_3_5_turbo");

            // persona
            $persona = $this->getPersona();

            // buyer persona
            $buyerPersona = $this->getBuyerPersona();

            // writing style
            $writingStyle = $this->getWritingStyle();

            // run the preset
            $response = $preset->process([
                "language" => $this->publication->project->language->value,
                "title" => $this->publication->generation_title,
                "request" => $this->publication->generation_title,
                "content" => $content,
                "persona" => $persona,
                "has_persona" => !empty($persona),
                "buyer_persona" => $buyerPersona,
                "has_buyer_persona" => !empty($buyerPersona),
                "writing_style" => $writingStyle,
                "has_writing_style" => !empty($writingStyle),
            ]);

            // get the response content
            $content = Arr::get($response, 'choices.0.message.content');
            if ($content) {
                // parse content
                return new HtmlParser($content);
            }
        } catch (Exception $e) {
        }
    }

    private function generateTable(string $content)
    {
        try {
            $preset = Preset::findFromAPI("table_openai_gpt_3_5_turbo");

            // persona
            $persona = $this->getPersona();

            // buyer persona
            $buyerPersona = $this->getBuyerPersona();

            // writing style
            $writingStyle = $this->getWritingStyle();

            // run the preset
            $response = $preset->process([
                "language" => $this->publication->project->language->value,
                "title" => $this->publication->generation_title,
                "request" => $this->publication->generation_title,
                "content" => $content,
                "persona" => $persona,
                "has_persona" => !empty($persona),
                "buyer_persona" => $buyerPersona,
                "has_buyer_persona" => !empty($buyerPersona),
                "writing_style" => $writingStyle,
                "has_writing_style" => !empty($writingStyle),
            ]);

            // get the response content
            $content = Arr::get($response, 'choices.0.message.content');
            if ($content) {
                // parse content
                return new HtmlParser($content);
            }
        } catch (Exception $e) {
        }
    }

    private function generateList(string $content)
    {
        try {
            $preset = Preset::findFromAPI("list_openai_gpt_3_5_turbo");

            // persona
            $persona = $this->getPersona();

            // buyer persona
            $buyerPersona = $this->getBuyerPersona();

            // writing style
            $writingStyle = $this->getWritingStyle();

            // run the preset
            $response = $preset->process([
                "language" => $this->publication->project->language->value,
                "title" => $this->publication->generation_title,
                "request" => $this->publication->generation_title,
                "content" => $content,
                "persona" => $persona,
                "has_persona" => !empty($persona),
                "buyer_persona" => $buyerPersona,
                "has_buyer_persona" => !empty($buyerPersona),
                "writing_style" => $writingStyle,
                "has_writing_style" => !empty($writingStyle),
            ]);

            // get the response content
            $content = Arr::get($response, 'choices.0.message.content');
            if ($content) {
                // parse content
                return new HtmlParser($content);
            }
        } catch (Exception $e) {
        }
    }

    /**
     * Generate the main keyword of a string
     *
     * @param string $string
     * @return string
     */
    private function generateMainKeyword(string $title): string
    {
        try {
            $preset = Preset::findFromAPI("main_keyword");

            $response = $preset->process([
                "language" => $this->publication->project->language->value,
                "request" => $title,
            ]);

            // get the response content
            $response = json_decode(Arr::get($response, 'choices.0.message.content'), true, 512, JSON_THROW_ON_ERROR);
            $content = Arr::get($response, "value");
            $content = Str::clean($content);

            if (!empty($content)) {
                return $content;
            }
        } catch (Exception $e) {
        }

        return $title;
    }

    /**
     * Generate and return a structure
     *
     * @return array
     * @throws Exception
     */
    private function createStructure()
    {
        $structure = Arr::get($this->publication->project->modules, "text.structure", []);

        if (!empty($structure)) {
            return $structure;
        } else {

            // generate the structure
            $preset = Preset::findFromAPI("structure_v3_openai_gpt_3_5_turbo");

            // get the length
            $h2Length = 4;
            $h3Length = 4;
            switch (Arr::get($this->publication->project->modules, 'text.length', 'short')) {
                case "short":
                    $h2Length = 2;
                    $h3Length = 3;
                    break;
                case "medium":
                    $h2Length = 4;
                    $h3Length = 3;
                    break;
                case "long":
                    $h2Length = 6;
                    $h3Length = 3;
                    break;
                case "custom":
                    $h2Length = Arr::get($this->publication->project->modules, 'text.h2_length', 3);
                    $h3Length = Arr::get($this->publication->project->modules, 'text.h3_length', 3);
                    break;
            }

            // run the preset
            $response = $preset->process([
                "language" => $this->publication->project->language->value,
                "title" => $this->publication->generation_title,
                "request" => $this->publication->generation_title,
                "h2_length" => $h2Length,
                "h3_length" => $h3Length,
            ]);

            // get the response content
            $structure = json_decode(Arr::get($response, 'choices.0.message.content'), true, 512, JSON_THROW_ON_ERROR);
            return Arr::get($structure, "sections", []);
        }

        return $structure;
    }

    /**
     * Create a content from preset and payload
     *
     * @param OpenAIPreset $preset
     * @param array $payload
     * @return HtmlParser|null
     * @throws Exception
     */
    private function createContent(Preset $preset, array $payload = [])
    {
        // run the preset
        $response = $preset->process($payload);

        // get the response content
        $content = Arr::get($response, 'choices.0.message.content');
        if ($content) {
            // parse content
            return new HtmlParser($content);
        }
    }

    /**
     * Create multiple contents from preset and payloads
     *
     * @param OpenAIPreset $preset
     * @param array $payloads
     * @return array
     * @throws Exception
     */
    private function createMultiContent(Preset $preset, array $payloads = [])
    {
        $output = [];

        // run the pool preset
        $responses = $preset->processPool($payloads);

        // get the response content
        foreach ($responses as $index => $response) {
            $content = Arr::get($response, 'choices.0.message.content');

            if ($content) {
                // parse content
                $output[$index] = new HtmlParser($content);
            }
        }

        return $output;
    }

    private function getExternalLinks(string $search)
    {
        if (!Arr::get($this->publication->project->modules, 'text.external_links.enabled', false)) {
            return [];
        }

        // retrieve google news rss
        try {
            return GoogleNews::search($search, $this->publication->project->language);
        } catch (Exception $e) {
            return [];
        }
    }

    /**
     * Get the persona system message form selected, or generate one
     *
     * @return string
     * @throws Exception
     */
    private function getPersona()
    {
        if ($this->publication->project->persona) {
            return $this->publication->project->persona->openai_system_message;
        }

        $this->persona = $this->createPersona();

        return $this->persona;
    }

    /**
     * Get the buyer persona
     *
     * @return string
     */
    private function getBuyerPersona()
    {
        return Arr::get($this->publication->project->modules, "text.buyer_persona.description", "");
    }

    /**
     * Get the writing style
     *
     * @return string
     */
    private function getWritingStyle()
    {
        switch (Arr::get($this->publication->project->modules, "text.writing_style")) {
            case "narrative";
                return "Narratif";
                break;
            case "descriptive";
                return "Descriptif";
                break;
            case "objective":
                return "Objectif";
                break;
            case "poetic":
                return "Poétique";
                break;
            case "persuasive":
                return "Persuasif";
                break;
            case "expository":
                return "Expositoire";
                break;
            case "creative":
                return "Créatif";
                break;
            case "technical":
                return "Technique";
                break;
            case "entertaining":
                return "Divertissant";
                break;
            case "subjective":
                return "Subjectif";
                break;
        }

        return "";
    }

    /**
     * Get custom instructions
     *
     * @return string
     */
    private function getCustomInstructions()
    {
        return Arr::get($this->publication->project->modules, "text.custom_instructions", "");
    }

    /**
     * Create an automatic persona
     *
     * @return string
     * @throws Exception
     */
    private function createPersona()
    {
        // get the persona preset
        $preset = Preset::findFromAPI("persona");

        // run the preset
        $response = $preset->process([
            "language" => $this->publication->project->language->value,
            "request" => $this->publication->generation_title,
        ]);

        // get the response content
        $response = json_decode(Arr::get($response, 'choices.0.message.content'), true, 512, JSON_THROW_ON_ERROR);
        $content = Arr::get($response, "value");

        return Str::clean($content);
    }

    /**
     * Create the sources sections
     *
     * @param array $urls
     * @return Section|null
     */
    private function createSourcesSection(array $urls = []): ?Section
    {

        $elts = [];
        foreach ($urls as $url) {
            $host = parse_url($url, PHP_URL_HOST);
            if (!empty($host)) {

                // create the link and attributes
                $attributes = ["href" =>  $url];
                if (!Arr::get($this->publication->project->modules, "text.sources.is_follow", false)) {
                    $attributes["rel"] = "nofollow";
                }
                $attributes = implode(" ", array_map(function ($val, $key) {
                    return $key . "=" . '"' . $val . '"';
                }, array_values($attributes), array_keys($attributes)));

                $elts[] = '<a ' . $attributes . '>' . $host . '</a>';
            }
        }

        if (!empty($urls)) {

            $section = new Section();

            $el = new ParagraphElement("Source: " . $elts[0]);

            $section->addElement($el);

            return $section;
        }

        return null;
    }

    /**
     * Determine if the scrap is disabled by the robots.txt
     *
     * @param string $url
     * @return boolean
     */
    private function isDisabledByRobotsTxt(string $url)
    {
        $robots = RobotsTxt::fromUrl($url);
        return !empty($robots->getRules("otomaticAI"));
    }

    /**
     * return the openai model key to use
     *
     * @param Publication $publication
     * @param string $key
     * @return string
     */
    static public function getOpenAIModel(Publication $publication): string
    {
        return Arr::get($publication->project->modules, "text.model", 'gpt-3.5-turbo');
    }

    /**
     * Determine if the module is enabled
     *
     * @param Publication $publication
     * @return boolean
     */
    static public function isEnabled(Publication $publication): bool
    {
        return Arr::get($publication->project->modules, "text.enabled", false);
    }

    /**
     * Determine if the module is runnable
     *
     * @param Publication $publication
     * @return boolean
     */
    static public function isRunnable(Publication $publication): bool
    {
        // must be enabled
        if (!self::isEnabled($publication)) {
            return false;
        }

        return true;
    }
}
