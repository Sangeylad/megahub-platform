<?php

namespace OtomaticAi\Models;

use OtomaticAi\Models\WP\Post;
use OtomaticAi\Vendors\Illuminate\Database\Eloquent\Model;
use OtomaticAi\Vendors\Illuminate\Support\Collection;

class Linking extends Model
{
    protected $fillable = [
        "custom_url", "keywords", "max_links", "post_types", "is_blank", "is_follow", "is_obfuscated"
    ];

    protected $casts = [
        'keywords' => 'array',
        'post_types' => 'array',
        'is_blank' => 'boolean',
        'is_follow' => 'boolean',
        'is_obfuscated' => 'boolean',
    ];

    /**
     * The accessors to append to the model's array form.
     *
     * @var array
     */
    protected $appends = [
        'url',
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

        $this->table = $wpdb->prefix . 'otomatic_ai_linkings';
        parent::__construct($attributes);
    }

    /**
     * Get the wp post that owns the linking.
     */
    public function post()
    {
        return $this->belongsTo(Post::class, "post_id");
    }

    /**
     * Get the url of the link
     */
    public function getUrlAttribute()
    {
        if ($this->mode === "post") {
            return get_permalink($this->post_id);
        }

        return $this->custom_url;
    }


    static function byKeywords()
    {
        $keywords = new Collection();
        self::all()->each(function ($model) use (&$keywords) {
            foreach ($model->keywords as $keyword) {
                $keywords->put($keyword, $model);
            }
        });

        return $keywords;
    }
}
