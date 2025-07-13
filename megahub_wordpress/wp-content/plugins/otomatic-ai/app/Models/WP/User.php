<?php

namespace OtomaticAi\Models\WP;

use OtomaticAi\Models\Persona;
use OtomaticAi\Vendors\Illuminate\Database\Eloquent\Model;

class User extends Model
{
    protected $primaryKey = 'ID';

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

        $this->table = $wpdb->users;
        parent::__construct($attributes);
    }

    /**
     * The accessors to append to the model's array form.
     *
     * @var array
     */
    protected $appends = ['user_meta'];

    protected $casts = [
        'user_registered' => 'datetime',
    ];

    /**
     * Get the posts for user.
     */
    public function posts()
    {
        return $this->hasMany(Post::class, 'post_author');
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
