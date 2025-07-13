<?php

namespace OtomaticAi\Controllers;

use Exception;
use OtomaticAi\Api\OpenAi\Client as OpenAiClient;
use OtomaticAi\Api\OtomaticAi\Client;
use OtomaticAi\Api\StabilityAi\Client as StabilityAiClient;
use OtomaticAi\Content\Image\StableDiffusion;
use OtomaticAi\Models\Preset;
use OtomaticAi\Utils\Auth;
use OtomaticAi\Utils\Image;
use OtomaticAi\Utils\Language;
use OtomaticAi\Vendors\Illuminate\Support\Arr;
use OtomaticAi\Vendors\Illuminate\Support\Str;
use OtomaticAi\Vendors\Illuminate\Validation\Rule;

class ImageGeneratorController extends Controller
{
    public function generate()
    {
        $this->verifyNonce();

        $this->validate([
            "provider" => ["required", Rule::in('dall_e', 'stable_diffusion')],
            "prompt" => ["required", "string"],
        ]);

        // refresh auth
        Auth::refreshDomain();

        if (!Auth::isPremium() && !Auth::isTrial()) {
            $this->response(["message" => "An error occurred", "error" => "This feature requires a premium subscription."], 503);
        }

        // save start event
        $this->collectEvent(
            "generate-image-start",
            [
                "provider" => $this->input("provider")
            ]
        );

        $prompt = $this->translatePrompt($this->input("prompt"));

        try {
            $response = null;
            switch ($this->input("provider")) {
                case "dall_e":
                    $api = new OpenAiClient();
                    $result = $api->image($prompt, [
                        "model" => "dall-e-3",
                        "quality" => "standard",
                        "size" => "1792x1024",
                    ]);
                    if (!empty(Arr::get($result, "data.0.b64_json"))) {
                        $path = $this->saveImageInTemp(Arr::get($result, "data.0.b64_json"));

                        if (!empty($path)) {
                            $response = [
                                "path" => $path,
                                "provider" => "dall_e",
                                "image" => [
                                    "base64" => Arr::get($result, "data.0.b64_json"),
                                    "width" => 1792,
                                    "height" => 1024,
                                ]
                            ];
                        }
                    }
                    break;
                case "stable_diffusion":

                    $api = new StabilityAiClient();

                    if ($this->input("settings.stable_diffusion.model", "stable_image_sd3") === "sdxl") {
                        // sdxl model
                        $payload = [
                            "text_prompts" => [
                                [
                                    "text" => $prompt,
                                    "weight" => 1
                                ]
                            ]
                        ];

                        $result = $api->textToImage($payload);

                        if (!empty(Arr::get($result, "artifacts.0.base64"))) {
                            $path = $this->saveImageInTemp(Arr::get($result, "artifacts.0.base64"));

                            if (!empty($path)) {
                                $response = [
                                    "path" => $path,
                                    "provider" => "stable_diffusion",
                                    "image" => [
                                        "base64" => Arr::get($result, "artifacts.0.base64"),
                                        "height" => 768,
                                        "width" => 1344,
                                    ]
                                ];
                            }
                        }
                    } else {
                        // others models
                        $payload = [
                            "prompt" => $prompt,
                        ];
                        switch ($this->input("settings.stable_diffusion.model", "stable_image_sd3")) {
                            case "stable_image_sd3_turbo":
                                $payload["model"] = "sd3-turbo";
                                break;
                            case "stable_image_sd3":
                                $payload["model"] = "sd3";
                                break;
                            default:
                                $payload["model"] = "core";
                        }

                        $result = $api->stableImageGenerate($payload);

                        if (!empty(Arr::get($result, "image"))) {
                            $path = $this->saveImageInTemp(Arr::get($result, "image"));

                            if (!empty($path)) {
                                $response = [
                                    "path" => $path,
                                    "provider" => "stable_diffusion",
                                    "image" => [
                                        "base64" => Arr::get($result, "image"),
                                        "height" => 768,
                                        "width" => 1344,
                                    ]
                                ];
                            }
                        }
                    }

                    break;
            }

            if (!empty($response)) {

                // refresh auth
                Auth::refreshDomain();

                // save end event
                $this->collectEvent("generate-image-end",  [
                    "provider" => $this->input("provider")
                ]);

                $this->response($response);
            }
        } catch (Exception $e) {

            $this->collectEvent("generate-image-failed",  [
                "provider" => $this->input("provider"),
                "message" => $e->getMessage(),
            ]);

            $this->response(["message" => "An error occurred", "error" => $e->getMessage()], 503);
        }
    }

    public function save()
    {
        $this->verifyNonce();

        $this->validate([
            "name" => ["nullable"],
            "description" => ["nullable"],
            "legend" => ["nullable"],
            "post_id" => ["nullable"],
            "path" => ["required", "string"],
        ]);

        $image = Image::fromPath($this->input("path"));
        if (($attachementId = $image->save($this->input("name"), $this->input("description"), $this->input("legend"))) !== null) {
            if (!empty($this->input("post_id"))) {
                if (set_post_thumbnail($this->input("post_id"), $attachementId) === false) {
                }
            }
        }

        $this->response([]);
    }

    /**
     * Generate an image description from title
     *
     */
    public function generateDescription()
    {
        $this->verifyNonce();

        $this->validate([
            "title" => ["required", "string"],
        ]);

        try {
            $preset = Preset::findFromAPI("alt_image");

            $response = $preset->process([
                "language" => Language::findFromLocale()->value,
                "request" => $this->input("title"),
            ]);

            // get the response content
            $response = json_decode(Arr::get($response, 'choices.0.message.content'), true, 512, JSON_THROW_ON_ERROR);
            $content = Arr::get($response, "value");
            $content = Str::clean($content);

            $this->response([
                "description" => Str::lower($content),
            ]);
        } catch (Exception $e) {
        }

        return $this->input("title");
    }

    /**
     * Translate the prompt in english
     *
     * @param string $prompt
     * @return string
     */
    private function translatePrompt(string $prompt): string
    {
        try {
            // get the openai preset
            $preset = Preset::findFromAPI("translate_content");

            // make payload
            $payload = [
                "language" => Language::find("en")->value,
                "content" => $prompt,
            ];


            // run the preset
            $response = $preset->process($payload);

            // get the response content
            $content = Arr::get($response, 'choices.0.message.content');
            $content = Str::clean($content);

            // return translated content
            if (!empty($content)) {
                return $content;
            }
        } catch (Exception $e) {
        }

        // return prompt if translation was incorrect
        return $prompt;
    }

    /**
     * save the base64 image to temp folder
     *
     * @param string $base64
     * @return string|null
     */
    private function saveImageInTemp(string $base64): ?string
    {
        $extension = "png";
        $name = uniqid();
        $path = get_temp_dir() . $name . '.' . $extension;

        $base64 = base64_decode($base64);

        if (file_put_contents($path, $base64) !== false) {
            return $path;
        }
    }

    private function collectEvent(string $key, array $payload = [])
    {
        $api = new Client;
        $api->collectEvent($key, $payload);
    }
}
