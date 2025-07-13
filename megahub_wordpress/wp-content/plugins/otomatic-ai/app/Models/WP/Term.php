<?php

namespace OtomaticAi\Models\WP;

use OtomaticAi\Vendors\Illuminate\Database\Eloquent\Model;
use OtomaticAi\Vendors\Illuminate\Database\Eloquent\Builder;

class Term extends Model
{
    protected $primaryKey = 'term_id';

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

        $this->table = $wpdb->terms;
        parent::__construct($attributes);
    }

    /**
     * Get the term taxonomy associated with the term.
     */
    public function term_taxonomy()
    {
        return $this->hasOne(TermTaxonomy::class, "term_id", "term_id");
    }

    /**
     * Scope a query to only include tags taxonomy.
     *
     * @param  \Illuminate\Database\Eloquent\Builder  $query
     * @return \Illuminate\Database\Eloquent\Builder
     */
    public function scopeTags($query)
    {
        return $query->whereRelation('term_taxonomy', function (Builder $query) {
            $query->tags();
        });
    }

    /**
     * Scope a query to only include categories taxonomy.
     *
     * @param  \Illuminate\Database\Eloquent\Builder  $query
     * @return \Illuminate\Database\Eloquent\Builder
     */
    public function scopeCategories($query)
    {
        return $query->whereRelation('term_taxonomy', function (Builder $query) {
            $query->categories();
        });
    }
}
