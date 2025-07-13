<?php

namespace OtomaticAi\Models;

use OtomaticAi\Vendors\Illuminate\Database\Eloquent\Model;

class Template extends Model
{
    protected $fillable = [
        "name", "plugin_version", "payload"
    ];

    protected $casts = [
        'payload' => 'array',
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

        $this->table = $wpdb->prefix . 'otomatic_ai_templates';
        parent::__construct($attributes);
    }
}
