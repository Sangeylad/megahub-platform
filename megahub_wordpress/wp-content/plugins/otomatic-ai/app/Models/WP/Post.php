<?php

namespace OtomaticAi\Models\WP;

use Exception;
use OtomaticAi\Vendors\Illuminate\Database\Eloquent\Model;
use OtomaticAi\Vendors\Illuminate\Database\Eloquent\Builder;

class Post extends Model
{
    protected $primaryKey = 'ID';

    public $timestamps = false;

    protected $casts = [
        'post_date' => 'datetime',
        'post_date_gmt' => 'datetime',
        'post_modified' => 'datetime',
        'post_modified_gmt' => 'datetime',
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

        $this->table = $wpdb->posts;
        parent::__construct($attributes);
    }

    /**
     * Get the author that owns the post.
     */
    public function author()
    {
        return $this->belongsTo(User::class, 'post_author');
    }

    /**
     * Get all of the categories term taxonomy for the post.
     */
    public function categories()
    {
        return $this->belongsToMany(TermTaxonomy::class, "term_relationships", "object_id", "term_taxonomy_id")->where("taxonomy", "category");
    }

    /**
     * Get all of the tags term taxonomy for the post.
     */
    public function tags()
    {
        return $this->belongsToMany(TermTaxonomy::class, "term_relationships", "object_id", "term_taxonomy_id")->where("taxonomy", "post_tag");
    }

    /**
     * Perform a model update operation.
     *
     * @param  \Illuminate\Database\Eloquent\Builder  $query
     * @return bool
     */
    protected function performUpdate(Builder $query)
    {
        // If the updating event returns false, we will cancel the update operation so
        // developers can hook Validation systems into their models and cancel this
        // operation if the model does not pass validation. Otherwise, we update.
        if ($this->fireModelEvent('updating') === \false) {
            return \false;
        }
        // First we need to create a fresh query instance and touch the creation and
        // update timestamp on the model which are maintained by us for developer
        // convenience. Then we will just continue saving the model instances.
        if ($this->usesTimestamps()) {
            $this->updateTimestamps();
        }
        // Once we have run the update operation, we will fire the "updated" event for
        // this model instance. This will allow developers to hook into these after
        // models are updated, giving them a chance to do any special processing.
        $dirty = $this->getDirty();
        if (\count($dirty) > 0) {
            $post = wp_insert_post($this->getAttributes(), true);
            if (is_wp_error($post)) {
                throw new Exception($post->get_error_message());
            }
            $this->syncChanges();
            $this->fireModelEvent('updated', \false);
        }
        return \true;
    }

    /**
     * Perform a model insert operation.
     *
     * @param  \Illuminate\Database\Eloquent\Builder  $query
     * @return bool
     */
    protected function performInsert(Builder $query)
    {
        if ($this->fireModelEvent('creating') === \false) {
            return \false;
        }
        // First we'll need to create a fresh query instance and touch the creation and
        // update timestamps on this model, which are maintained by us for developer
        // convenience. After, we will just continue saving these model instances.
        if ($this->usesTimestamps()) {
            $this->updateTimestamps();
        }
        // If the model has an incrementing key, we can use the "insertGetId" method on
        // the query builder, which will give us back the final inserted ID for this
        // table from the database. Not all tables have to be incrementing though.
        $attributes = $this->getAttributesForInsert();

        $post = wp_insert_post($attributes, true);
        if (is_wp_error($post)) {
            throw new Exception($post->get_error_message());
        }

        $keyName = $this->getKeyName();
        $this->setAttribute($keyName, $post);

        // We will go ahead and set the exists property to true, so that it is set when
        // the created event is fired, just in case the developer tries to update it
        // during the event. This will allow them to do so and run an update here.
        $this->exists = \true;
        $this->wasRecentlyCreated = \true;
        $this->fireModelEvent('created', \false);
        return \true;
    }
}
