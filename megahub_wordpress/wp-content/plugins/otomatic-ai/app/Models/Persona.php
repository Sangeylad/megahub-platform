<?php

namespace OtomaticAi\Models;

use OtomaticAi\Models\WP\User;
use OtomaticAi\Vendors\Illuminate\Database\Eloquent\Model;
use OtomaticAi\Vendors\Illuminate\Support\Arr;
use OtomaticAi\Vendors\Illuminate\Support\Str;

class Persona extends Model
{
    protected $fillable = [
        "age", "job", "writing_style"
    ];

    protected $casts = [
        'messages' => 'array',
    ];

    /**
     * The accessors to append to the model's array form.
     *
     * @var array
     */
    protected $appends = [
        'openai_system_message',
        'user_avatar',
        'user_avatar_url',
        'user_large_avatar_url',
        'user_description',
        'user_full_name',
        'user_first_name',
        'user_last_name'
    ];

    /**
     * Create a new Eloquent model instance.
     *
     * @param  array  $attributes
     * @return void
     */
    public function __construct(array $attributes = [])
    {
        global $wpdb;

        $this->table = $wpdb->prefix . 'otomatic_ai_personas';
        parent::__construct($attributes);
    }

    /**
     * Get the user that owns the persona.
     */
    public function user()
    {
        return $this->belongsTo(User::class, 'user_id');
    }

    /**
     * Get the user avatar for the persona.
     */
    public function getUserAvatarAttribute()
    {
        return get_avatar_data($this->user_id);
    }

    /**
     * Get the user avatar url for the persona.
     */
    public function getUserAvatarUrlAttribute()
    {
        return get_avatar_url($this->user_id);
    }

    /**
     * Get the user avatar url for the persona.
     */
    public function getUserLargeAvatarUrlAttribute()
    {
        return get_avatar_url($this->user_id, [
            "size" => 192
        ]);
    }

    /**
     * Get the user full name for the persona.
     */
    public function getUserFullNameAttribute()
    {
        return $this->user_first_name . ' ' . $this->user_last_name;
    }

    /**
     * Get the user first name for the persona.
     */
    public function getUserFirstNameAttribute()
    {
        if ($this->user_data !== false) {
            return $this->user_data->first_name;
        }
    }

    /**
     * Get the user last name for the persona.
     */
    public function getUserLastNameAttribute()
    {
        if ($this->user_data !== false) {
            return $this->user_data->last_name;
        }
    }

    /**
     * Get the user description for the persona.
     */
    public function getUserDescriptionAttribute()
    {
        if ($this->user_data !== false) {
            return $this->user_data->description;
        }
    }

    /**
     * Get the user data for the persona
     *
     * @return void
     */
    public function getUserDataAttribute()
    {
        return get_userdata($this->user_id);
    }

    /**
     * Get the openai syteme message for the persona.
     */
    public function getOpenaiSystemMessageAttribute()
    {
        $lines = [];

        // name
        $name = Str::of(Arr::get($this->user ? $this->user->user_meta : [], 'first_name.0'))->trim();
        if ($name->isNotEmpty()) {
            $lines[] = "Tu t'appelles " . $name . ".";
        }

        // age
        $age = Str::of($this->age)->trim();
        if ($age->isNotEmpty()) {
            $lines[] = "Tu as " . $age . " ans.";
        }

        // job
        $job = Str::of($this->job)->trim();
        if ($job->isNotEmpty()) {
            $lines[] = "Ton metier ou ton hobby : " . $job . ".";
        }

        // writing style
        $writingStyle = null;;
        switch ($this->writing_style) {
            case "courteous";
                $writingStyle = "Courtois";
                break;
            case "creative";
                $writingStyle = "Créatif";
                break;
            case "curious":
                $writingStyle = "Curieux";
                break;
            case "dynamic":
                $writingStyle = "Dynamique";
                break;
            case "funny":
                $writingStyle = "Drôle";
                break;
            case "effective":
                $writingStyle = "Efficace";
                break;
            case "empathetic":
                $writingStyle = "Empathique";
                break;
            case "enthusiastic":
                $writingStyle = "Enthousiaste";
                break;
            case "jovial":
                $writingStyle = "Jovial";
                break;
            case "methodical":
                $writingStyle = "Méthodique";
                break;
            case "motivated":
                $writingStyle = "Motivé";
                break;
            case "organized":
                $writingStyle = "Organisé";
                break;
            case "versatile":
                $writingStyle = "Polyvalent";
                break;
            case "professional":
                $writingStyle = "Professionnel";
                break;
            case "sensitive":
                $writingStyle = "Sensible";
                break;
            case "sociable":
                $writingStyle = "Sociable";
                break;
        }
        if (!empty($writingStyle)) {
            $lines[] = "Ton style est " . $writingStyle . ".";
        }

        return implode("\n", $lines);
    }
}
