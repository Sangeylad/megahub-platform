<?php

namespace OtomaticAi\Modules;

use Exception;
use OtomaticAi\Api\OpenAi\PoolClient as OpenAiPoolClient;
use OtomaticAi\Api\StabilityAi\PoolClient as StabilityAiPoolClient;
use OtomaticAi\Api\Unsplash\Client as UnsplashClient;
use OtomaticAi\Api\Pexels\Client as PexelsClient;
use OtomaticAi\Api\Pixabay\Client as PixabayClient;
use OtomaticAi\Api\GoogleImage\Client as GoogleImageClient;
use OtomaticAi\Api\BingImage\Client as BingImageClient;
use OtomaticAi\Content\Image\BingImage;
use OtomaticAi\Content\Image\DallE;
use OtomaticAi\Content\Image\GoogleImage;
use OtomaticAi\Content\Image\Pexels;
use OtomaticAi\Content\Image\Pixabay;
use OtomaticAi\Content\Image\StableDiffusion;
use OtomaticAi\Content\Image\Unsplash;
use OtomaticAi\Models\Preset;
use OtomaticAi\Models\Publication;
use OtomaticAi\Modules\Contracts\Module as ModuleContract;
use OtomaticAi\Utils\Auth;
use OtomaticAi\Utils\Language;
use OtomaticAi\Vendors\Illuminate\Support\Arr;
use OtomaticAi\Vendors\Illuminate\Support\Str;

class ProcessImageModule implements ModuleContract
{
    /**
     * The publication
     *
     * @var Publication
     */
    private Publication $publication;

    /**
     * Array of used image urls
     *
     * @var array
     */
    private array $usedImages = [];

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

        // perform content images module
        $this->handleContentImages();

        // perform thumbnail image module
        $this->handleThumbnailImage();
    }

    /**
     * Generate content images
     *
     * @return void
     * @throws Exception
     */
    private function handleContentImages(): void
    {
        // verify that the content images module is enabled
        if (!Arr::get($this->publication->project->modules, "image.content.enabled", false)) {
            return;
        }

        // log the start of the job
        $this->publication->addLog("Content image module started.");

        // get publication sections
        $sections = $this->publication->sections;

        // get number of image to get
        $length = intval(max(0, min(Arr::get($this->publication->project->modules, "image.content.length", 3), $sections->count() - 1)));
        if ($length === 0) {
            $this->publication->addLog("Content image module ended. No image slots available.", "warning");
        }

        // generate images
        $images = [];
        switch (Arr::get($this->publication->project->modules, "image.service")) {
            case "stable_diffusion":
                $images = $this->getStableDiffusionImage($this->publication->generation_title, $length);
                break;
            case "dall_e":
                $images = $this->getDallEImage($this->publication->generation_title, $length);
                break;
            case "unsplash":
                $images = $this->getUnsplashImage($this->publication->generation_title, $length);
                break;
            case "pexels":
                $images = $this->getPexelsImage($this->publication->generation_title, $length);
                break;
            case "pixabay":
                $images = $this->getPixabayImage($this->publication->generation_title, $length);
                break;
            case "google_image":
                $images = $this->getGoogleImage($this->publication->generation_title, $length);
                break;
            case "bing_image":
                $images = $this->getBingImage($this->publication->generation_title, $length);
                break;
        }

        $initialLength = $length;
        $successfulGenerations = 0;

        // add images to sections
        if (!empty($images)) {
            $successfulGenerations = count($images);

            $first = true;
            $sections->transform(function ($section) use (&$first, &$images) {
                if ($first) {
                    $first = false;
                    return $section;
                }

                $image = array_shift($images);
                if (!empty($image)) {
                    $section->addElement($image, false);
                }

                return $section;
            });

            // update publication sections
            $this->publication->sections = $sections;
        }

        // log the end of the job
        if ($successfulGenerations === $initialLength) {
            $this->publication->addLog("Content images module completed successfully.", "success");
        } else {
            $this->publication->addLog("Content images module completed with errors. " . $successfulGenerations . " on " . $initialLength . " images generated.", "warning");
        }
    }

    /**
     * Generate thumbnail image
     *
     * @return void
     * @throws Exception
     */
    private function handleThumbnailImage(): void
    {
        // verify that the thumbnail image module is enabled
        if (!Arr::get($this->publication->project->modules, "image.thumbnail.enabled", false)) {
            return;
        }

        // log the start of the job
        $this->publication->addLog("Thumbnail image module started.");

        // generate images
        $images = [];
        switch (Arr::get($this->publication->project->modules, "image.service")) {
            case "stable_diffusion":
                $images = $this->getStableDiffusionImage($this->publication->generation_title);
                break;
            case "dall_e":
                $images = $this->getDallEImage($this->publication->generation_title);
                break;
            case "unsplash":
                $images = $this->getUnsplashImage($this->publication->generation_title);
                break;
            case "pexels":
                $images = $this->getPexelsImage($this->publication->generation_title);
                break;
            case "pixabay":
                $images = $this->getPixabayImage($this->publication->generation_title);
                break;
            case "google_image":
                $images = $this->getGoogleImage($this->publication->generation_title);
                break;
            case "bing_image":
                $images = $this->getBingImage($this->publication->generation_title);
                break;
        }

        // add the image to publication extras and
        // log the end of the job
        if (!empty($images)) {
            $extras = $this->publication->extras;
            $extras["thumbnail"] = $images[0]->toArray();
            $this->publication->extras = $extras;

            $this->publication->addLog("Thumbnail image module completed successfully.", "success");
        } else {
            $this->publication->addLog("Thumbnail image module completed with errors.", "warning");
        }
    }

    /**
     * Generate a stable diffusion image for the provided search
     *
     * @param string $search
     * @param int $length
     * @return StableDiffusion|StableDiffusion[]|null
     */
    private function getStableDiffusionImage(string $search, int $length = 1)
    {
        // log the image generation
        $this->publication->addLog("Image generation with Stable Diffusion started.");

        try {
            // make the prompt for stable diffusion
            $prompt = $this->makeStableDiffusionPrompt($search);

            // make the pool settings
            $payloads = [];
            for ($i = 0; $i < $length; $i++) {

                if (Arr::get($this->publication->project->modules, "image.settings.stable_diffusion.model") === "sdxl") {
                    // sdxl model
                    $payload = [
                        "text_prompts" => [
                            [
                                "text" => $prompt,
                                "weight" => 1
                            ]
                        ]
                    ];
                } else {
                    // others models
                    $payload = [
                        "prompt" => $prompt,
                    ];

                    switch (Arr::get($this->publication->project->modules, "image.settings.stable_diffusion.model")) {
                        case "stable_image_sd3_turbo":
                            $payload["model"] = "sd3-turbo";
                            break;
                        case "stable_image_sd3":
                            $payload["model"] = "sd3";
                            break;
                        default:
                            $payload["model"] = "core";
                    }
                }
                $payloads[] = $payload;
            }

            // call the stability ai api
            $api = new StabilityAiPoolClient();
            if (Arr::get($this->publication->project->modules, "image.settings.stable_diffusion.model") === "sdxl") {
                // sdxl model
                $result = [];
                foreach ($api->textToImage($payloads) as $artifact) {
                    if (Arr::get($artifact, "artifacts.0.finishReason") === "SUCCESS") {
                        $result[] = [
                            "image" => Arr::get($artifact, "artifacts.0.base64")
                        ];
                    }
                }
            } else {
                // others models
                $result = $api->stableImageGenerate($payloads);
            }

            // make the Stable Diffusion Images
            $images = [];
            foreach ($result as $res) {

                if (!empty(Arr::get($res, "image", null))) {
                    // description
                    $description = $this->makeImageDescription($search);

                    // legend
                    $legend = null;
                    if (Arr::get($this->publication->project->modules, "image.copyright.enabled", false)) {
                        switch ($this->publication->project->language->key) {
                            case "fr":
                                $legend = "Image générée par Stable Diffusion";
                                break;
                            case "it":
                                $legend = "Immagine generata da Stable Diffusion";
                                break;
                            case "de":
                                $legend = "Bild erstellt von Stable Diffusion";
                                break;
                            case "es":
                                $legend = "Imagen generada por Stable Diffusion";
                                break;
                            case "pt":
                                $legend = "Imagem gerada por Stable Diffusion";
                                break;
                            case "ru":
                                $legend = "Изображение создано Stable Diffusion";
                                break;
                            case "kr":
                                $legend = "Stable Diffusion 에서 생성된 이미지";
                                break;
                            case "tr":
                                $legend = "Resim Stable Diffusion tarafından oluşturulmuştur";
                                break;
                            case "nl":
                                $legend = "Afbeelding gegenereerd door Stable Diffusion";
                                break;
                            case "ja":
                                $legend = "Stable Diffusion で生成された画像";
                                break;
                            case "pl":
                                $legend = "Obraz wygenerowany przez Stable Diffusion";
                                break;
                            case "ro":
                                $legend = "Imagine generată de Stable Diffusion";
                                break;
                            case "en":
                            default:
                                $legend = "Image generated by Stable Diffusion";
                                break;
                        }
                    }

                    $images[] = new StableDiffusion(Arr::get($res, "image"), $search, $description, $legend);
                }
            }
            return $images;
        } catch (Exception $e) {
            $this->publication->addLog("Image generation failed. " . $e->getMessage(), "warning");
        }
    }

    /**
     * Generate a dall-e image for the provided search
     *
     * @param string $search
     * @param int $length
     * @return DallE|DallE[]|null
     */
    private function getDallEImage(string $search, int $length = 1)
    {
        // log the image generation
        $this->publication->addLog("Image generation with Dall-E started.");

        try {
            // make the prompt for dall e
            $prompt = $this->makeDallEPrompt($search);

            // make the pool settings
            $settings = [
                "prompts" => [],
                "settings" => [],
            ];
            for ($i = 0; $i < $length; $i++) {
                $settings["prompts"][] = $prompt;
                $model = Arr::get($this->publication->project->modules, "image.settings.dall_e.model", "dall-e-2");
                $settings["settings"][] = [
                    "model" => $model,
                    "quality" => Arr::get($this->publication->project->modules, "image.settings.dall_e.quality", "standard"),
                    "size" => $model === "dall-e-3" ? "1792x1024" : "1024x1024",
                ];
            }

            // call the openai api
            $api = new OpenAiPoolClient();
            $result = $api->image($settings["prompts"], $settings["settings"]);

            // make the DallE Images
            $images = [];
            foreach ($result as $res) {

                // description
                $description = $this->makeImageDescription($search);

                // legend
                $legend = null;
                if (Arr::get($this->publication->project->modules, "image.copyright.enabled", false)) {
                    switch ($this->publication->project->language->key) {
                        case "fr":
                            $legend = "Image générée par DALL·E";
                            break;
                        case "it":
                            $legend = "Immagine generata da DALL·E";
                            break;
                        case "de":
                            $legend = "Bild erstellt von DALL·E";
                            break;
                        case "es":
                            $legend = "Imagen generada por DALL·E";
                            break;
                        case "pt":
                            $legend = "Imagem gerada por DALL·E";
                            break;
                        case "ru":
                            $legend = "Изображение создано DALL·E";
                            break;
                        case "kr":
                            $legend = "DALL·E 에서 생성된 이미지";
                            break;
                        case "tr":
                            $legend = "Resim DALL·E tarafından oluşturulmuştur";
                            break;
                        case "nl":
                            $legend = "Afbeelding gegenereerd door DALL·E";
                            break;
                        case "ja":
                            $legend = "DALL·Eで生成された画像";
                            break;
                        case "pl":
                            $legend = "Obraz wygenerowany przez DALL·E";
                            break;
                        case "ro":
                            $legend = "Imagine generată de DALL·E";
                            break;
                        case "en":
                        default:
                            $legend = "Image generated by DALL·E";
                            break;
                    }
                }

                $images[] = new DallE(Arr::get($res, "data.0.b64_json"), $search, $description, $legend);
            }
            return $images;
        } catch (Exception $e) {
            $this->publication->addLog("Image generation failed. " . $e->getMessage(), "warning");
        }
    }

    /**
     * Generate an Unsplash image for the provided search
     *
     * @param string $search
     * @param int $length
     * @return Unsplash|Unsplash[]|null
     */
    private function getUnsplashImage(string $search, int $length = 1)
    {
        // log the image generation
        $this->publication->addLog("Image generation with Unsplash started.");

        try {

            // make the search for unsplash
            $search = $this->makeUnsplashSearch($search);

            // call unsplash api
            $api = new UnsplashClient;
            $response = $api->searchPhotos([
                "query" => $search,
                "per_page" => 20,
            ]);

            // get a random image
            $result = Arr::get($response, "results", []);

            // filter to remove used images
            $result = array_filter($result, function ($image) {
                return !in_array($image["urls"]["full"], $this->usedImages);
            });
            $result = array_values($result);

            if (!empty($result)) {

                $images = [];
                $result = Arr::random($result, min(count($result), $length));

                foreach ($result as $res) {

                    // description
                    $description = $this->makeImageDescription($search);

                    // legend
                    $legend = null;
                    if (Arr::get($this->publication->project->modules, "image.copyright.enabled", false)) {
                        $author = Arr::get($res, "user.name");
                        if (!empty($author)) {
                            switch ($this->publication->project->language->key) {
                                case "fr":
                                    $legend = "Image réalisée par " . $author . " - Unsplash";
                                    break;
                                case "it":
                                    $legend = "Immagine creata da " . $author . " - Unsplash";
                                    break;
                                case "de":
                                    $legend = "Bild erstellt von " . $author . " - Unsplash";
                                    break;
                                case "es":
                                    $legend = "Imagen creada por " . $author . " - Unsplash";
                                    break;
                                case "pt":
                                    $legend = "Imagem criada por " . $author . " - Unsplash";
                                    break;
                                case "ru":
                                    $legend = "Изображение создано " . $author . " - Unsplash";
                                    break;
                                case "kr":
                                    $legend = $author . " 가 만든 이미지 - Unsplash";
                                    break;
                                case "tr":
                                    $legend = "Resim " . $author . " tarafından oluşturuldu - Unsplash";
                                    break;
                                case "nl":
                                    $legend = "Afbeelding gemaakt door " . $author . " - Unsplash";
                                    break;
                                case "ja":
                                    $legend = "画像作成者: " . $author . " - Unsplash";
                                    break;
                                case "pl":
                                    $legend = "Obraz stworzony przez " . $author . " - Unsplash";
                                    break;
                                case "ro":
                                    $legend = "Imagine creată de " . $author . " - Unsplash";
                                    break;
                                case "en":
                                default:
                                    $legend = "Image created by " . $author . " - Unsplash";
                                    break;
                            }
                        }
                    }

                    // add image to used images
                    $this->usedImages[] = $res["urls"]["full"];

                    $images[] = new Unsplash($res["urls"]["full"], $search, $description, $legend);
                }

                return $images;
            } else {
                $this->publication->addLog("Image generation failed. No images found.", "warning");
            }
        } catch (Exception $e) {
            $this->publication->addLog("Image generation failed. " . $e->getMessage(), "warning");
        }
    }

    /**
     * Generate an Pexels image for the provided search
     *
     * @param string $search
     * @param int $length
     * @return Pexel|Pexel[]|null
     */
    private function getPexelsImage(string $search, int $length = 1)
    {
        // log the image generation
        $this->publication->addLog("Image generation with Pexels started.");

        try {

            // make the search for pexels
            $search = $this->makePexelsSearch($search);

            // call pexels api
            $api = new PexelsClient();
            $response = $api->searchPhotos([
                "query" => $search,
                "per_page" => 20,
            ]);

            // get a random image
            $result = Arr::get($response, "photos", []);

            // filter to remove used images
            $result = array_filter($result, function ($image) {
                return !in_array($image["src"]["landscape"], $this->usedImages);
            });
            $result = array_values($result);

            if (!empty($result)) {

                $images = [];
                $result = Arr::random($result, min(count($result), $length));
                foreach ($result as $res) {

                    // description
                    $description = $this->makeImageDescription($search);

                    // legend
                    $legend = null;
                    if (Arr::get($this->publication->project->modules, "image.copyright.enabled", false)) {
                        $author = Arr::get($res, "photographer");
                        if (!empty($author)) {
                            switch ($this->publication->project->language->key) {
                                case "fr":
                                    $legend = "Image réalisée par " . $author . " - Pexels";
                                    break;
                                case "it":
                                    $legend = "Immagine creata da " . $author . " - Pexels";
                                    break;
                                case "de":
                                    $legend = "Bild erstellt von " . $author . " - Pexels";
                                    break;
                                case "es":
                                    $legend = "Imagen creada por " . $author . " - Pexels";
                                    break;
                                case "pt":
                                    $legend = "Imagem criada por " . $author . " - Pexels";
                                    break;
                                case "ru":
                                    $legend = "Изображение создано " . $author . " - Pexels";
                                    break;
                                case "kr":
                                    $legend = $author . " 가 만든 이미지 - Pexels";
                                    break;
                                case "tr":
                                    $legend = "Resim " . $author . " tarafından oluşturuldu - Pexels";
                                    break;
                                case "nl":
                                    $legend = "Afbeelding gemaakt door " . $author . " - Pexels";
                                    break;
                                case "ja":
                                    $legend = "画像作成者: " . $author . " - Pexels";
                                    break;
                                case "pl":
                                    $legend = "Obraz stworzony przez " . $author . " - Pexels";
                                    break;
                                case "ro":
                                    $legend = "Imagine creată de " . $author . " - Pexels";
                                    break;
                                case "en":
                                default:
                                    $legend = "Image created by " . $author . " - Pexels";
                                    break;
                            }
                        }
                    }

                    // add image to used images
                    $this->usedImages[] = $res["src"]["landscape"];

                    $images[] = new Pexels($res["src"]["landscape"], $search, $description, $legend);
                }

                return $images;
            } else {
                $this->publication->addLog("Image generation failed. No images found.", "warning");
            }
        } catch (Exception $e) {
            $this->publication->addLog("Image generation failed. " . $e->getMessage(), "warning");
        }
    }

    /**
     * Generate an Pixabay image for the provided search
     *
     * @param string $search
     * @param int $length
     * @return Pixabay|Pixabay[]|null
     */
    private function getPixabayImage(string $search, int $length = 1)
    {
        // log the image generation
        $this->publication->addLog("Image generation with Pixabay started.");

        try {

            // make the search for pixabay
            $search = $this->makePixabaySearch($search);

            // call pixabay api
            $api = new PixabayClient();
            $response = $api->images([
                "q" => $search,
            ]);

            // get a random image
            $result = Arr::get($response, "hits", []);

            // filter to remove used images
            $result = array_filter($result, function ($image) {
                return !in_array($image["largeImageURL"], $this->usedImages);
            });
            $result = array_values($result);

            if (!empty($result)) {

                $images = [];
                $result = Arr::random($result, min(count($result), $length));
                foreach ($result as $res) {

                    // description
                    $description = $this->makeImageDescription($search);

                    // legend
                    $legend = null;
                    if (Arr::get($this->publication->project->modules, "image.copyright.enabled", false)) {
                        $author = Arr::get($res, "user");
                        if (!empty($author)) {
                            switch ($this->publication->project->language->key) {
                                case "fr":
                                    $legend = "Image réalisée par " . $author . " - Pixabay";
                                    break;
                                case "it":
                                    $legend = "Immagine creata da " . $author . " - Pixabay";
                                    break;
                                case "de":
                                    $legend = "Bild erstellt von " . $author . " - Pixabay";
                                    break;
                                case "es":
                                    $legend = "Imagen creada por " . $author . " - Pixabay";
                                    break;
                                case "pt":
                                    $legend = "Imagem criada por " . $author . " - Pixabay";
                                    break;
                                case "ru":
                                    $legend = "Изображение создано " . $author . " - Pixabay";
                                    break;
                                case "kr":
                                    $legend = $author . " 가 만든 이미지 - Pixabay";
                                    break;
                                case "tr":
                                    $legend = "Resim " . $author . " tarafından oluşturuldu - Pixabay";
                                    break;
                                case "nl":
                                    $legend = "Afbeelding gemaakt door " . $author . " - Pixabay";
                                    break;
                                case "ja":
                                    $legend = "画像作成者: " . $author . " - Pixabay";
                                    break;
                                case "pl":
                                    $legend = "Obraz stworzony przez " . $author . " - Pixabay";
                                    break;
                                case "ro":
                                    $legend = "Imagine creată de " . $author . " - Pixabay";
                                    break;
                                case "en":
                                default:
                                    $legend = "Image created by " . $author . " - Pixabay";
                                    break;
                            }
                        }
                    }

                    // add image to used images
                    $this->usedImages[] = $res["largeImageURL"];

                    $images[] = new Pixabay($res["largeImageURL"], $search, $description, $legend);
                }

                return $images;
            } else {
                $this->publication->addLog("Image generation failed. No images found.", "warning");
            }
        } catch (Exception $e) {
            $this->publication->addLog("Image generation failed. " . $e->getMessage(), "warning");
        }
    }

    /**
     * Generate an Google image for the provided search
     *
     * @param string $search
     * @param int $length
     * @return GoogleImage|GoogleImage[]|null
     */
    private function getGoogleImage(string $search, int $length = 1)
    {
        // log the image generation
        $this->publication->addLog("Image generation with Google Image started.");

        try {

            // make the search for google image
            $search = $this->makeGoogleImageSearch($search);

            // call google image api
            $api = new GoogleImageClient();
            $result = $api->images([
                "q" => $search,
            ]);

            // filter to remove used images
            $result = array_filter($result, function ($url) {
                return !in_array($url, $this->usedImages);
            });
            $result = array_values($result);

            // get a random image
            if (!empty($result)) {

                $images = [];
                $result = Arr::random($result, min(count($result), $length));
                foreach ($result as $res) {

                    // description
                    $description = $this->makeImageDescription($search);

                    // legend
                    $legend = null;
                    if (Arr::get($this->publication->project->modules, "image.copyright.enabled", false)) {
                        switch ($this->publication->project->language->key) {
                            default:
                                $legend = "Google Image";
                                break;
                        }
                    }

                    // add image to used images
                    $this->usedImages[] = $res;

                    $images[] = new GoogleImage($res, $search, $description, $legend);
                }

                return $images;
            } else {
                $this->publication->addLog("Image generation failed. No images found.", "warning");
            }
        } catch (Exception $e) {
            $this->publication->addLog("Image generation failed. " . $e->getMessage(), "warning");
        }
    }

    /**
     * Generate an Bing image for the provided search
     *
     * @param string $search
     * @param int $length
     * @return BingImage|BingImage[]|null
     */
    private function getBingImage(string $search, int $length = 1)
    {
        // log the image generation
        $this->publication->addLog("Image generation with Bing Image started.");

        try {

            // make the search for bing image
            $search = $this->makeBingImageSearch($search);

            // call google image api
            $api = new BingImageClient();
            $result = $api->images([
                "q" => $search,
            ]);

            // filter to remove used images
            $result = array_filter($result, function ($url) {
                return !in_array($url, $this->usedImages);
            });
            $result = array_values($result);

            // get a random image
            if (!empty($result)) {

                $images = [];
                $result = Arr::random($result, min(count($result), $length));
                foreach ($result as $res) {

                    // description
                    $description = $this->makeImageDescription($search);

                    // legend
                    $legend = null;
                    if (Arr::get($this->publication->project->modules, "image.copyright.enabled", false)) {
                        switch ($this->publication->project->language->key) {
                            default:
                                $legend = "Bing Image";
                                break;
                        }
                    }

                    // add image to used images
                    $this->usedImages[] = $res;

                    $images[] = new BingImage($res, $search, $description, $legend);
                }

                return $images;
            } else {
                $this->publication->addLog("Image generation failed. No images found.", "warning");
            }
        } catch (Exception $e) {
            $this->publication->addLog("Image generation failed. " . $e->getMessage(), "warning");
        }
    }

    /**
     * Generate the stable diffusion prompt for the provided search
     *
     * @param string $search
     * @return string
     * @throws Exception
     */
    private function makeStableDiffusionPrompt(string $search): string
    {
        $search = Str::lower($search);
        $customInstructions = $this->getCustomInstructions();

        $preset = Preset::findFromAPI("stable_diffusion_prompt_v2");

        $response = $preset->process([
            "request" => $search,
            "has_custom_instructions" => !empty($customInstructions),
            "custom_instructions" => $customInstructions,
        ]);

        $response = json_decode(Arr::get($response, 'choices.0.message.content'), true, 512, JSON_THROW_ON_ERROR);
        $content = Arr::get($response, "value");
        $content = Str::clean($content);

        if (!empty($content)) {
            return $content;
        }

        return $search;
    }

    /**
     * Generate the dall-e prompt for the provided search
     *
     * @param string $search
     * @return string
     * @throws Exception
     */
    private function makeDallEPrompt(string $search): string
    {
        $search = Str::lower($search);

        $preset = Preset::findFromAPI("dall_e_prompt");

        $response = $preset->process([
            "language" => $this->publication->project->language->value,
            "request" => $search,
        ]);

        // get the response content
        $response = json_decode(Arr::get($response, 'choices.0.message.content'), true, 512, JSON_THROW_ON_ERROR);
        $content = Arr::get($response, "value");
        $content = Str::clean($content);

        // custom instructions
        $customInstructions =  $this->getCustomInstructions();
        if (!empty($customInstructions)) {
            $content = $content . " " . $customInstructions;
        }

        return Str::lower($content);
    }

    /**
     * Make the Unsplash search terms for the provided search
     *
     * @param string $search
     * @return string
     * @throws Exception
     */
    private function makeUnsplashSearch(string $search): string
    {
        $search = Str::lower($search);

        $preset = Preset::findFromAPI("main_keyword");

        $response = $preset->process([
            "language" => Language::find("en")->value,
            "request" => $search,
        ]);

        // get the response content
        $response = json_decode(Arr::get($response, 'choices.0.message.content'), true, 512, JSON_THROW_ON_ERROR);
        $content = Arr::get($response, "value");
        $content = Str::clean($content);

        return Str::lower($content);
    }

    /**
     * Make the Pexels search terms for the provided search
     *
     * @param string $search
     * @return string
     * @throws Exception
     */
    private function makePexelsSearch(string $search): string
    {
        $search = Str::lower($search);

        $preset = Preset::findFromAPI("main_keyword");

        $response = $preset->process([
            "language" => Language::find("en")->value,
            "request" => $search,
        ]);

        // get the response content
        $response = json_decode(Arr::get($response, 'choices.0.message.content'), true, 512, JSON_THROW_ON_ERROR);
        $content = Arr::get($response, "value");
        $content = Str::clean($content);

        return Str::lower($content);
    }

    /**
     * Make the Pixabay search terms for the provided search
     *
     * @param string $search
     * @return string
     * @throws Exception
     */
    private function makePixabaySearch(string $search): string
    {
        $search = Str::lower($search);

        $preset = Preset::findFromAPI("main_keyword");

        $response = $preset->process([
            "language" => Language::find("en")->value,
            "request" => $search,
        ]);

        // get the response content
        $response = json_decode(Arr::get($response, 'choices.0.message.content'), true, 512, JSON_THROW_ON_ERROR);
        $content = Arr::get($response, "value");
        $content = Str::clean($content);

        return Str::lower($content);
    }

    /**
     * Make the Google Image search terms for the provided search
     *
     * @param string $search
     * @return string
     * @throws Exception
     */
    private function makeGoogleImageSearch(string $search): string
    {
        $search = Str::lower($search);

        $preset = Preset::findFromAPI("shorten_title");

        $response = $preset->process([
            "language" => $this->publication->project->language->value,
            "request" => $search,
        ]);

        // get the response content
        $response = json_decode(Arr::get($response, 'choices.0.message.content'), true, 512, JSON_THROW_ON_ERROR);
        $content = Arr::get($response, "value");
        $content = Str::clean($content);

        return Str::lower($content);
    }

    /**
     * Make the Bong Image search terms for the provided search
     *
     * @param string $search
     * @return string
     * @throws Exception
     */
    private function makeBingImageSearch(string $search): string
    {
        $search = Str::lower($search);

        $preset = Preset::findFromAPI("shorten_title");

        $response = $preset->process([
            "language" => $this->publication->project->language->value,
            "request" => $search,
        ]);

        // get the response content
        $response = json_decode(Arr::get($response, 'choices.0.message.content'), true, 512, JSON_THROW_ON_ERROR);
        $content = Arr::get($response, "value");
        $content = Str::clean($content);

        return Str::lower($content);
    }

    /**
     * Generate an image description from the title
     *
     * @param string $title
     * @return string
     * @throws Exception
     */
    private function makeImageDescription(string $title): string
    {
        $preset = Preset::findFromAPI("alt_image");

        $response = $preset->process([
            "language" => $this->publication->project->language->value,
            "request" => $title,
        ]);

        // get the response content
        $response = json_decode(Arr::get($response, 'choices.0.message.content'), true, 512, JSON_THROW_ON_ERROR);
        $content = Arr::get($response, "value");
        $content = Str::clean($content);

        return Str::lower($content);
    }

    /**
     * Get custom instructions
     *
     * @return string
     */
    private function getCustomInstructions()
    {
        return Arr::get($this->publication->project->modules, "image.custom_instructions", "");
    }

    /**
     * Determine if the module is enabled
     *
     * @param Publication $publication
     * @return boolean
     */
    static public function isEnabled(Publication $publication): bool
    {
        return Arr::get($publication->project->modules, "image.content.enabled", false) || Arr::get($publication->project->modules, "image.thumbnail.enabled", false);
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

        // publication sections must not be empty
        if ($publication->sections->isEmpty()) {
            return false;
        }

        return true;
    }
}
