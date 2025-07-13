<?php

namespace OtomaticAi\Models\WP;

use OtomaticAi\Vendors\Illuminate\Database\Eloquent\Model;

class TermTaxonomy extends Model
{
    protected $primaryKey = 'term_taxonomy_id';

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

        $this->table = $wpdb->term_taxonomy;
        parent::__construct($attributes);
    }

    /**
     * Get the term associated with the term taxonomy.
     */
    public function term()
    {
        return $this->hasOne(Term::class, "term_id", "term_id");
    }

    /**
     * Scope a query to only include tags taxonomy.
     *
     * @param  \Illuminate\Database\Eloquent\Builder  $query
     * @return \Illuminate\Database\Eloquent\Builder
     */
    public function scopeTags($query)
    {
        return $query->where('taxonomy', 'post_tag');
    }

    /**
     * Scope a query to only include categories taxonomy.
     *
     * @param  \Illuminate\Database\Eloquent\Builder  $query
     * @return \Illuminate\Database\Eloquent\Builder
     */
    public function scopeCategories($query)
    {
        return $query->where('taxonomy', 'category');
    }
}
