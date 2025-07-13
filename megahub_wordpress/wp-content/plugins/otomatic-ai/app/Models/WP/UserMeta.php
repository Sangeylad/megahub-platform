<?php

namespace OtomaticAi\Models\WP;

use OtomaticAi\Models\Persona;
use OtomaticAi\Vendors\Illuminate\Database\Eloquent\Model;

class UserMeta extends Model
{
    protected $primaryKey = 'umeta_id';

    public $timestamps = false;

    /**
     * Create a new Eloquent model instance.
     *
     * @param  array  $attributes
     * @return void
     */
    public function __construct(array $attributes = [])
    {
        global $wpdb;

        $this->table = $wpdb->usermeta;
        parent::__construct($attributes);
    }

    /**
     * Get the posts for user.
     */
    public function user()
    {
        return $this->belongsTo(User::class, 'user_id');
    }

    /**
     * Get the persona for user.
     */
    public function persona()
    {
        return $this->hasOne(Persona::class, 'user_id');
    }

    public function getUserMetaAttribute()
    {
        return get_user_meta($this->ID);
    }
}
