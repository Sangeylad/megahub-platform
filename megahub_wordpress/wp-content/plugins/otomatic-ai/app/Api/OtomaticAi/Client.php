<?php

namespace OtomaticAi\Api\OtomaticAi;

use OtomaticAi\Api\OtomaticAi\Exceptions\NotFoundException;
use OtomaticAi\Api\OtomaticAi\Exceptions\PermissionDeniedException;
use OtomaticAi\Api\OtomaticAi\Exceptions\PresetNotFoundException;
use OtomaticAi\Api\OtomaticAi\Exceptions\UnauthorizedException;
use OtomaticAi\Api\OtomaticAi\Exceptions\ValidationException;
use OtomaticAi\Utils\Auth;
use OtomaticAi\Vendors\GuzzleHttp\Client as HttpClient;
use OtomaticAi\Vendors\GuzzleHttp\Exception\ClientException;
use OtomaticAi\Vendors\GuzzleHttp\Handler\CurlHandler;
use OtomaticAi\Vendors\GuzzleHttp\HandlerStack;
use OtomaticAi\Vendors\Illuminate\Support\Arr;
use OtomaticAi\Vendors\Psr\Http\Message\RequestInterface;

class Client
{
    /**
     * The GuzzleHttp client
     *
     * @var HttpClient
     */
    private HttpClient $client;

    /**
     * The api endpoint
     *
     * @var string
     */
    private string $endpoint = OTOMATIC_AI_API_ENDPOINT;

    /**
     * Create a new OtomaticAI Api client
     */
    public function __construct()
    {
        // add the auth token
        $handler = new CurlHandler();
        $stack = HandlerStack::create($handler);
        $stack->push(function (callable $handler) {
            return function (RequestInterface $request, array $options) use ($handler) {
                $token = Auth::token();
                if (!empty($token)) {
                    $request = $request->withHeader('Authorization', 'Bearer ' . $token);
                }

                return $handler($request, $options);
            };
        });

        // instantiate the http client
        $this->client = new HttpClient([
            'handler'  => $stack,
            "base_uri" => rtrim($this->endpoint, "/") . '/',
            'headers'  => [
                'Accept' => 'application/json',
                'Content-Type' => 'application/json',
            ]
        ]);
    }

    /**
     * Authenticate the user and get the auth token
     *
     * @param string $email
     * @param string $password
     * @param string $referer
     * @param string|null $version
     * @throws ClientException
     * @throws ValidationException
     * @return array
     */
    public function login(string $email, string $password, string $referer, string $version = null): array
    {
        return $this->request("POST", "auth/login", [
            "form_params" => [
                "email" => $email,
                "password" => $password,
                "referer" => $referer,
                "version" => $version,
            ]
        ]);
    }

    /**
     * Check the auth token validity
     *
     * @param string|null $version
     * @throws ClientException
     * @throws ValidationException
     * @return array
     */
    public function check(string $version = null): array
    {
        return $this->request("GET", "auth/check", [
            "query" => [
                "version" => $version
            ]
        ]);
    }

    /**
     * Get the authenticated domain
     *
     * @return array
     * @throws ClientException
     * @throws UnauthorizedException
     * @throws ValidationException
     */
    public function domain(): array
    {
        return $this->request("GET", "auth/domain");
    }

    /**
     * Try to set the authenticated domain to premium
     *
     * @return array
     * @throws ClientException
     * @throws UnauthorizedException
     * @throws ValidationException
     */
    public function enablePremium(): array
    {
        return $this->request("POST", "auth/enable-premium");
    }

    /**
     * Try to unset the authenticated domain from premium
     *
     * @return array
     * @throws ClientException
     * @throws UnauthorizedException
     * @throws ValidationException
     */
    public function disablePremium(): array
    {
        return $this->request("POST", "auth/disable-premium");
    }

    /**
     * Find a openai preset by role
     *
     * @param string $role
     * @return array
     * @throws ClientException
     * @throws UnauthorizedException
     * @throws ValidationException
     */
    public function findOpenAIPreset(string $role): array
    {
        try {
            return $this->request("GET", 'openai-presets/' . $role);
        } catch (NotFoundException $e) {
            throw new PresetNotFoundException($role);
        }
    }

    /**
     * Call the google search api endpoint
     *
     * @param string $search
     * @param string $lang
     * @return array
     * @throws ClientException
     * @throws UnauthorizedException
     * @throws ValidationException
     */
    public function googleSearch(string $search, string $lang = "en"): array
    {
        return $this->request("GET", "search/google-search", [
            "query" => [
                "search" => $search,
                "lang" => $lang,
            ]
        ]);
    }

    /**
     * Call the twitter api endpoint
     *
     * @param string $search
     * @param string $lang
     * @return array
     * @throws ClientException
     * @throws UnauthorizedException
     * @throws ValidationException
     */
    public function twitter(string $search, string $lang = "en"): array
    {
        return $this->request("GET", "search/twitter", [
            "query" => [
                "search" => $search,
                "lang" => $lang,
            ]
        ]);
    }

    /**
     * Call the facebook api endpoint
     *
     * @param string $search
     * @param string $lang
     * @return array
     * @throws ClientException
     * @throws UnauthorizedException
     * @throws ValidationException
     */
    public function facebook($search, $lang = "en"): array
    {
        return $this->request("GET", "search/facebook", [
            "query" => [
                "search" => $search,
                "lang" => $lang,
            ]
        ]);
    }

    /**
     * Call the instagram api endpoint
     *
     * @param string $search
     * @param string $lang
     * @return array
     * @throws ClientException
     * @throws UnauthorizedException
     * @throws ValidationException
     */
    public function instagram($search, $lang = "en"): array
    {
        return $this->request("GET", "search/instagram", [
            "query" => [
                "search" => $search,
                "lang" => $lang,
            ]
        ]);
    }

    /**
     * Call the tiktok api endpoint
     *
     * @param string $search
     * @param string $lang
     * @return array
     * @throws ClientException
     * @throws UnauthorizedException
     * @throws ValidationException
     */
    public function tiktok($search, $lang = "en"): array
    {
        return $this->request("GET", "search/tiktok", [
            "query" => [
                "search" => $search,
                "lang" => $lang,
            ]
        ]);
    }

    /**
     * Call the youtube api endpoint
     *
     * @param string $search
     * @param string $lang
     * @return array
     * @throws ClientException
     * @throws UnauthorizedException
     * @throws ValidationException
     */
    public function youtube($search, $lang = "en"): array
    {
        return $this->request("GET", "search/youtube", [
            "query" => [
                "search" => $search,
                "lang" => $lang,
            ]
        ]);
    }

    /**
     * Call the help center api endpoint
     *
     * @return array
     * @throws ClientException
     * @throws UnauthorizedException
     * @throws ValidationException
     */
    public function helpCenter(): array
    {
        return $this->request("GET", "help-center");
    }

    /**
     * Call the pricing plans api endpoint
     *
     * @return array
     * @throws ClientException
     * @throws UnauthorizedException
     * @throws ValidationException
     */
    public function pricingPlans(): array
    {
        return $this->request("GET", "pricing-plans");
    }

    /**
     * Call the collect events api endpoint
     *
     * @param string $key
     * @param array $payload
     * @return array
     * @throws ClientException
     * @throws UnauthorizedException
     * @throws ValidationException
     */
    public function collectEvent(string $key, array $payload = []): array
    {
        return $this->request("POST", "events/collect", [
            "form_params" => [
                "key" => $key,
                "payload" => $payload,
            ]
        ]);
    }

    /**
     * Call an API request
     *
     * @param string $method
     * @param string $uri
     * @param array $options
     * @return array
     */
    private function request(string $method, $uri = '', array $options = []): array
    {
        try {
            $response = $this->client->request($method, $uri, $options);
            $response = $response->getBody()->getContents();
            $response = json_decode($response, true);
            return $response;
        } catch (ClientException $e) {
            if ($e->getCode() === 401) {
                throw new UnauthorizedException();
            } else if ($e->getCode() === 403) {
                throw new PermissionDeniedException();
            } else if ($e->getCode() === 404) {
                throw new NotFoundException();
            } else if ($e->getCode() === 422) {
                $response = $e->getResponse()->getBody()->getContents();
                $response = json_decode($response, true);
                throw new ValidationException(Arr::get($response, "message", ""), Arr::get($response, "errors", []));
            }
            throw $e;
        }
    }
}
