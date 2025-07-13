<?php

namespace OtomaticAi\Models;

use OtomaticAi\Content\SectionCollection;
use OtomaticAi\Models\WP\Post;
use OtomaticAi\Observers\PublicationObserver;
use OtomaticAi\Vendors\Carbon\Carbon;
use OtomaticAi\Vendors\Illuminate\Database\Eloquent\Builder;
use OtomaticAi\Vendors\Illuminate\Database\Eloquent\Model;
use OtomaticAi\Vendors\Illuminate\Events\Dispatcher;
use OtomaticAi\Vendors\Illuminate\Support\Arr;

class Publication extends Model
{
    protected $fillable = ["title", "status", 'meta', "published_at"];

    protected $sections;
    protected $extras = [];

    /**
     * Create a new Eloquent model instance.
     *
     * @param  array  $attributes
     * @return void
     */
    public function __construct(array $attributes = [])
    {
        global $wpdb;

        $this->table = $wpdb->prefix . 'otomatic_ai_publications';

        parent::__construct($attributes);

        $this->sections = new SectionCollection();
    }

    /**
     * The accessors to append to the model's array form.
     *
     * @var array
     */
    protected $appends = ['edit_link', 'display_link'];

    protected $casts = [
        'published_at' => 'datetime',
        'meta' => 'array',
        'logs' => 'array',
    ];

    public static function boot()
    {
        parent::boot();

        static::setEventDispatcher(new Dispatcher());
        static::observe(new PublicationObserver());
    }

    /**
     * Get the project that owns the publication.
     */
    public function project()
    {
        return $this->belongsTo(Project::class);
    }

    /**
     * Get the children publications for the publication.
     */
    public function children()
    {
        return $this->hasMany(self::class, 'parent_id');
    }

    /**
     * Get the parent publication that owns the publication.
     */
    public function parent()
    {
        return $this->belongsTo(self::class, "parent_id");
    }

    /**
     * Get the wp post that owns the publication.
     */
    public function post()
    {
        return $this->belongsTo(Post::class, "post_id");
    }

    /**
     * Scope a query to only include published publications.
     */
    public function scopePublished(Builder $query): void
    {
        $query->where('status', 'success');
    }

    /**
     * Scope a query to only include idle publications.
     */
    public function scopeIdle(Builder $query): void
    {
        $query->where('status', 'idle');
    }

    /**
     * Scope a query to only include pending publications.
     */
    public function scopePending(Builder $query): void
    {
        $query->where('status', 'pending');
    }

    /**
     * Scope a query to only include failed publications.
     */
    public function scopeFailed(Builder $query): void
    {
        $query->where('status', 'failed');
    }

    /**
     * Get the wordpress edit link of the post publication.
     */
    public function getEditLinkAttribute()
    {
        if ($this->post_id !== null) {
            return get_edit_post_link($this->post_id, 'json');
        }

        return null;
    }

    /**
     * Get the wordpress display link of the post publication.
     */
    public function getDisplayLinkAttribute()
    {
        if ($this->post_id !== null) {
            return get_permalink($this->post_id);
        }

        return null;
    }

    public function getSectionsAttribute()
    {
        return $this->sections;
    }

    public function setSectionsAttribute($value)
    {
        $this->sections = $value;
    }

    public function getExtrasAttribute()
    {
        return $this->extras;
    }

    public function setExtrasAttribute($value)
    {
        $this->extras = $value;
    }

    public function getGenerationTitleAttribute()
    {
        if (!empty(Arr::get($this->meta, "base_title"))) {
            return Arr::get($this->meta, "base_title") . ' : ' . $this->title;
        }

        return $this->title;
    }

    public function clearLogs()
    {
        $this->logs = null;
        $this->save();
    }

    public function addLog($message, $type = "info", $extras = null)
    {
        $logs = $this->logs;
        if (!is_array($logs)) {
            $logs = [];
        }
        $logs[] = [
            "type" => $type,
            "message" => $message,
            "extras" => $extras,
            "created_at" => Carbon::now()
        ];
        $this->logs = $logs;
        $this->save();
    }
}
