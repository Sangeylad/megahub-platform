<?php

namespace OtomaticAi\Controllers;

use OtomaticAi\Utils\Validator;
use OtomaticAi\Vendors\Illuminate\Support\Arr;
use OtomaticAi\Vendors\Illuminate\Validation\ValidationException;

class Controller
{
    /**
     * Data passed by POST
     *
     * @var array
     */
    protected $request = [];

    public function __construct()
    {
        $this->verifyNonce();

        if (!empty($_POST["payload"])) {
            $this->request = json_decode(stripcslashes($_POST["payload"]), true);
        }
    }

    /**
     * Send a JSON response back to an Ajax request.
     *
     * @param array $data
     * @param integer $status
     * @return void
     */
    protected function response($data = [], $status = 200)
    {
        wp_send_json($data, $status);
    }

    /**
     * Send an empty response back to an Ajax request
     *
     * @param integer $status
     * @return void
     */
    protected function emptyResponse($status = 200)
    {
        wp_die('', '', [
            'code' => $status,
        ]);
    }

    /**
     * Verify the nonce of an Ajax request
     *
     * @param string $key
     * @return void
     */
    protected function verifyNonce($key = "_ajax_nonce")
    {
        if (!isset($_POST[$key]) || !wp_verify_nonce($_POST[$key], OTOMATIC_AI_NONCE)) {
            $this->response(["message" => "Page expired.", "error" => "Refresh the page and retry."], 403);
        }
    }

    /**
     * Validate the data of an Ajax request
     *
     * @param string $key
     * @return void
     */
    protected function validate($rules, $messages = [], $customAttributes = [])
    {
        $validator = new Validator($this->request, $rules, $messages, $customAttributes);
        try {
            return $validator->validate();
        } catch (ValidationException $e) {
            $this->response(["message" => $e->getMessage(), "errors" => $e->validator->getMessageBag()], 422);
        }
    }

    /**
     * Get the data of an Ajax request
     *
     * @param string $key
     * @param mixed $default
     * @return mixed
     */
    protected function input(string $key = null, $default = null)
    {
        if (empty($key)) {
            return $this->request;
        }
        return Arr::get($this->request, $key, $default);
    }
}
