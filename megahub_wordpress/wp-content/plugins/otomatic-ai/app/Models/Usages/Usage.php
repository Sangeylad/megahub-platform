<?php

namespace OtomaticAi\Models\Usages;

use OtomaticAi\Vendors\Carbon\Carbon;
use OtomaticAi\Vendors\Illuminate\Database\Eloquent\Model;
use OtomaticAi\Vendors\Illuminate\Database\Eloquent\Builder;

class Usage extends Model
{
    protected $fillable = ["provider", "payload", "created_at"];

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

        $this->table = $wpdb->prefix . 'otomatic_ai_usages';
        parent::__construct($attributes);
    }
}
