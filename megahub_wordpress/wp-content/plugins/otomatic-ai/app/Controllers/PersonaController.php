<?php

namespace OtomaticAi\Controllers;

use Exception;
use OtomaticAi\Api\OpenAi\Client;
use OtomaticAi\Api\StabilityAi\Client as StabilityAiClient;
use OtomaticAi\Models\Persona;
use OtomaticAi\Models\Preset;
use OtomaticAi\Models\WP\User;
use OtomaticAi\Utils\Image;
use OtomaticAi\Utils\Language;
use OtomaticAi\Utils\Settings;
use OtomaticAi\Vendors\Illuminate\Support\Arr;
use OtomaticAi\Vendors\Illuminate\Support\Str;
use OtomaticAi\Vendors\Illuminate\Validation\Rule;
use Simple_Local_Avatars;

class PersonaController extends Controller
{
    public function index()
    {
        $this->verifyNonce();

        $personas = Persona::whereHas('user')->with("user")->get();
        $this->response($personas);
    }

    public function edit()
    {
        $this->verifyNonce();

        $this->validate([
            "id" => ["required"],
        ]);

        $persona = Persona::find($this->input("id"));

        if ($persona === null) {
            $this->response(["message" => "An error occurred", "error" => "Unable to find the persona #" . $this->input("id") . "."], 503);
        }

        $persona->load(["user"]);

        $this->response($persona);
    }

    public function store()
    {
        $this->verifyNonce();

        $this->validateLanguage();
        $this->validateUser();
        $this->validateProfil();
        $this->validateBiography();
        $this->validateAvatar();

        // create or get the user
        if ($this->input("mode") === "create") {
            $userId = wp_create_user($this->input("username"), $this->input("password"), $this->input("email", ""));
            if (is_wp_error($userId)) {
                $this->response(["message" => "An error occurred", "error" => "Unable to create the user.<br>" . $userId->get_error_message()], 503);
            }
            // set role
            if (!empty($this->input("role"))) {
                $user = get_user_by("ID", $userId);
                $user->set_role($this->input("role"));
            }

            // get model
            $user = User::find($userId);
        } else if ($this->input("mode") === "attach") {
            $user = User::find($this->input("user_id"));
        } else {
            $this->emptyResponse();
        }

        // update user_meta
        update_user_meta($user->ID, "first_name", $this->input("first_name"));
        update_user_meta($user->ID, "last_name", $this->input("last_name"));
        update_user_meta($user->ID, "description", $this->input("description"));

        // attach the avatar
        if (class_exists("Simple_Local_Avatars") && !empty($this->input("avatar.attachment_id"))) {
            try {
                $sla = new Simple_Local_Avatars();
                $sla->assign_new_user_avatar($this->input("avatar.attachment_id"), $user->ID);
            } catch (Exception $e) {
            }
        }

        // create the persona
        $persona = new Persona;
        $persona->user()->associate($user);

        $persona->language = $this->input("language");
        $persona->age = $this->input("age");
        $persona->job = $this->input("job");
        $persona->writing_style = $this->input("writing_style");
        $persona->save();

        if ($persona->save()) {
            $this->emptyResponse();
        } else {
            $this->response(["message" => "An error occurred", "error" => "Unable to create the persona."], 503);
        }
    }

    public function destroy()
    {
        $this->verifyNonce();

        $this->validate([
            "persona" => ["required", "integer"],
        ]);

        $persona = Persona::find($this->input('persona'));
        if ($persona) {
            $persona->delete();
        }

        $this->emptyResponse();
    }

    public function updateProfil()
    {
        $this->verifyNonce();

        $this->validate([
            "id" => ["required"],
        ]);
        $this->validateProfil();

        // get the persona
        $persona = Persona::find($this->input("id"));

        if ($persona === null) {
            $this->response(["message" => "An error occurred", "error" => "Unable to find the persona #" . $this->input("id") . "."], 503);
        }

        $persona->load(["user"]);

        // update user_meta
        update_user_meta($persona->user->ID, "first_name", $this->input("first_name"));
        update_user_meta($persona->user->ID, "last_name", $this->input("last_name"));

        // update persona
        $persona->age = $this->input("age");
        $persona->job = $this->input("job");
        $persona->writing_style = $this->input("writing_style");
        $persona->save();

        $this->emptyResponse();
    }

    public function updateAvatar()
    {
        $this->verifyNonce();

        $this->validate([
            "id" => ["required"],
        ]);

        $this->validateSimpleLocalAvatar();
        $this->validateAPIKeys();

        // get the persona
        $persona = Persona::find($this->input("id"));

        if ($persona === null) {
            $this->response(["message" => "An error occurred", "error" => "Unable to find the persona #" . $this->input("id") . "."], 503);
        }

        if (!class_exists("Simple_Local_Avatars")) {
            $this->response(["message" => "An error occurred", "error" => "Simple Local Avatars plugin is required."], 503);
        }

        $persona->load(["user"]);

        // attach the avatar
        try {
            $base64 = $this->makeAvatar($persona->language, $persona->user_first_name, $persona->age, $persona->job);

            if (!empty($base64)) {
                $avatar = Image::fromBase64($base64);
                $attachmentId = $avatar->save('user avatar');

                if ($attachmentId !== null) {
                    $sla = new Simple_Local_Avatars();
                    $sla->assign_new_user_avatar($attachmentId, $persona->user->ID);
                }
            }
        } catch (Exception $e) {
            $this->response(["message" => "An error occurred", "error" => $e->getMessage()], 503);
        }

        $this->response($persona->fresh());
    }

    public function updateBiography()
    {
        $this->verifyNonce();

        $this->validate([
            "id" => ["required"],
        ]);
        $this->validateBiography();

        // get the persona
        $persona = Persona::find($this->input("id"));

        if ($persona === null) {
            $this->response(["message" => "An error occurred", "error" => "Unable to find the persona #" . $this->input("id") . "."], 503);
        }

        $persona->load(["user"]);

        // update user_meta
        update_user_meta($persona->user->ID, "description", $this->input("description"));

        $this->emptyResponse();
    }

    public function validateLanguageStep()
    {
        $this->verifyNonce();

        $this->validateLanguage();

        $this->emptyResponse();
    }

    public function validateUserStep()
    {
        $this->verifyNonce();

        $this->validateUser();

        $this->emptyResponse();
    }

    public function validateProfilStep()
    {
        $this->verifyNonce();

        $this->validateProfil();

        $this->emptyResponse();
    }

    public function validateBiographyStep()
    {
        $this->verifyNonce();

        $this->validateBiography();

        $this->emptyResponse();
    }

    public function generateBiography()
    {
        $this->verifyNonce();

        $this->validateLanguage();
        $this->validateProfil();

        try {

            $preset = Preset::findFromAPI("user_biography");
            $response = $preset->process([
                "language" => Language::find($this->input("language", "en"))->value,
                "name" => $this->input("first_name", ''),
                "age" => $this->input("age", 30),
                "job" => $this->input("job", ''),
            ]);

            // get the response content
            $response = json_decode(Arr::get($response, 'choices.0.message.content'), true, 512, JSON_THROW_ON_ERROR);
            $content = Arr::get($response, "value");
            $content = Str::clean($content);

            $this->response([
                "description" => $content,
            ]);
        } catch (Exception $e) {
            $this->response(["message" => "An error occurred", "error" => $e->getMessage()], 503);
        }

        $this->emptyResponse();
    }

    public function generateAvatar()
    {
        $this->verifyNonce();

        $this->validateLanguage();
        $this->validateProfil();
        $this->validateSimpleLocalAvatar();
        $this->validateAPIKeys();

        try {
            $base64 = $this->makeAvatar($this->input('language'), $this->input("first_name", ''), $this->input("age", 30), $this->input("job", ''));

            if (!empty($base64)) {

                $avatar = Image::fromBase64($base64);
                $attachmentId = $avatar->save('user avatar');

                if ($attachmentId !== null) {
                    $this->response(
                        [
                            "avatar" => [
                                "attachment_id" => $attachmentId,
                                "url" => wp_get_attachment_url($attachmentId)
                            ]
                        ],
                    );
                }
            }
        } catch (Exception $e) {
            $this->response(["message" => "An error occurred", "error" => $e->getMessage()], 503);
        }

        $this->emptyResponse();
    }

    /**
     * Generate an avatar image in base64 for the provided parameters
     *
     * @param string $language
     * @param string $name
     * @param integer $age
     * @param string $job
     * @return string
     * @throws Exception
     */
    private function makeAvatar(string $language, string $name, int $age, string $job)
    {
        $avatar = null;

        // try with stable diffusion
        if (!empty(Settings::get("api.stability_ai.api_key"))) {
            $avatar = $this->makeStableDiffusionAvatar($language, $name, $age, $job);
        }

        if (empty($avatar) && !empty(Settings::get("api.openai.api_key"))) {
            $avatar = $this->makeDallEAvatar($language, $name, $age, $job);
        }

        return $avatar;
    }

    private function makeStableDiffusionAvatar(string $language, string $name, int $age, string $job)
    {
        // get the preset for generate the stable diffusion prompt
        $preset = Preset::findFromAPI("stable_diffusion_avatar_prompt");

        // process the preset
        $response = $preset->process([
            "language" => Language::find($language)->value,
            "name" => $name,
            "age" => $age,
            "job" => $job,
        ]);

        // get the response content
        $response = json_decode(Arr::get($response, 'choices.0.message.content'), true, 512, JSON_THROW_ON_ERROR);
        $prompt = Arr::get($response, "value");
        $prompt = Str::clean($prompt);

        // generate the stability ai image
        $api = new StabilityAiClient();
        $result = $api->textToImage([
            "steps" => 30,
            "width" => 1024,
            "height" => 1024,
            "text_prompts" => [
                [
                    "text" => $prompt,
                    "weight" => 1,
                ]
            ]
        ]);

        return Arr::get($result, "artifacts.0.base64");
    }
    private function makeDallEAvatar(string $language, string $name, int $age, string $job)
    {
        // get the preset for generate the dall-e prompt
        $preset = Preset::findFromAPI("dall_e_avatar_prompt");

        // process the preset
        $response = $preset->process([
            "language" => Language::find($language)->value,
            "name" => $name,
            "age" => $age,
            "job" => $job,
        ]);

        // get the response content
        $response = json_decode(Arr::get($response, 'choices.0.message.content'), true, 512, JSON_THROW_ON_ERROR);
        $prompt = Arr::get($response, "value");
        $prompt = Str::clean($prompt);

        // generate the dall-e 3 image
        $api = new Client();
        $result = $api->image($prompt, [
            "model" => "dall-e-3",
            "quality" => "hd",
            "size" => "1024x1024",
        ]);

        return Arr::get($result, "data.0.b64_json");
    }

    // validators
    private function validateLanguage()
    {
        $this->validate([
            "language" => ["required", "string"],
        ]);
    }

    private function validateUser()
    {
        $this->validate([
            "mode" => ["required", Rule::in(["create", "attach"])],
            "username" => [
                "required_if:mode,create", "string",
                function ($attribute, $value, $fail) {
                    if ($this->input("mode") === "create" && username_exists($value)) {
                        $fail('The ' . $attribute . ' field already exists.');
                    }
                }
            ],
            "password" => ["required_if:mode,create", "string"],
            "email" => ["nullable", "email", function ($attribute, $value, $fail) {
                if ($this->input("mode") === "create" && email_exists($value)) {
                    $fail('The ' . $attribute . ' field already exists.');
                }
            }],
            "role" => ["nullable", "string"],
            "user_id" => [
                "required_if:mode,attach",
                function ($attribute, $value, $fail) {

                    if ($this->input("mode") === "attach") {
                        $user = User::with("persona")->find($value);
                        if (!$user) {
                            $fail('The user does not exist.');
                            return;
                        }

                        if ($user->persona !== null) {
                            $fail('The user is already associated with a persona.');
                        }
                    }
                }
            ],
        ]);
    }

    private function validateProfil()
    {
        $this->validate([
            "first_name" => ["required", "string"],
            "last_name" => ["nullable", "string"],
            "age" => ["required", "numeric", "min:18", "max:99"],
            "job" => ["required", "string"],
            "writing_style" => ["nullable", "string"],
        ]);
    }

    private function validateBiography()
    {
        $this->validate([
            "description" => ["nullable", "string"],
        ]);
    }

    private function validateAvatar()
    {
        $this->validate([
            "avatar.attachment_id" => ["nullable"],
        ]);
    }

    public function validateSimpleLocalAvatar()
    {
        if (!class_exists("Simple_Local_Avatars")) {
            $this->response(["message" => "An error occurred", "error" => "This feature require the Simple Local Avatars plugin. It is available on the WordPress store."], 503);
        }
    }

    public function validateAPIKeys()
    {
        if (empty(Settings::get("api.stability_ai.api_key")) && empty(Settings::get("api.openai.api_key"))) {
            $this->response(["message" => "An error occurred", "error" => "Your OpenAI or Stability AI API Keys are not set."], 503);
        }
    }
}
