<?php

namespace OtomaticAi\Vendors\Illuminate\Database\Eloquent\Relations;

use BadMethodCallException;
use OtomaticAi\Vendors\Illuminate\Database\Eloquent\Builder;
use OtomaticAi\Vendors\Illuminate\Database\Eloquent\Collection;
use OtomaticAi\Vendors\Illuminate\Database\Eloquent\Model;
use OtomaticAi\Vendors\Illuminate\Database\Eloquent\Relations\Concerns\InteractsWithDictionary;
class MorphTo extends BelongsTo
{
    use InteractsWithDictionary;
    /**
     * The type of the polymorphic relation.
     *
     * @var string
     */
    protected $morphType;
    /**
     * The models whose relations are being eager loaded.
     *
     * @var \Illuminate\Database\Eloquent\Collection
     */
    protected $models;
    /**
     * All of the models keyed by ID.
     *
     * @var array
     */
    protected $dictionary = [];
    /**
     * A buffer of dynamic calls to query macros.
     *
     * @var array
     */
    protected $macroBuffer = [];
    /**
     * A map of relations to load for each individual morph type.
     *
     * @var array
     */
    protected $morphableEagerLoads = [];
    /**
     * A map of relationship counts to load for each individual morph type.
     *
     * @var array
     */
    protected $morphableEagerLoadCounts = [];
    /**
     * A map of constraints to apply for each individual morph type.
     *
     * @var array
     */
    protected $morphableConstraints = [];
    /**
     * Create a new morph to relationship instance.
     *
     * @param  \Illuminate\Database\Eloquent\Builder  $query
     * @param  \Illuminate\Database\Eloquent\Model  $parent
     * @param  string  $foreignKey
     * @param  string  $ownerKey
     * @param  string  $type
     * @param  string  $relation
     * @return void
     */
    public function __construct(Builder $query, Model $parent, $foreignKey, $ownerKey, $type, $relation)
    {
        $this->morphType = $type;
        parent::__construct($query, $parent, $foreignKey, $ownerKey, $relation);
    }
    /**
     * Set the constraints for an eager load of the relation.
     *
     * @param  array  $models
     * @return void
     */
    public function addEagerConstraints(array $models)
    {
        $this->buildDictionary($this->models = Collection::make($models));
    }
    /**
     * Build a dictionary with the models.
     *
     * @param  \Illuminate\Database\Eloquent\Collection  $models
     * @return void
     */
    protected function buildDictionary(Collection $models)
    {
        foreach ($models as $model) {
            if ($model->{$this->morphType}) {
                $morphTypeKey = $this->getDictionaryKey($model->{$this->morphType});
                $foreignKeyKey = $this->getDictionaryKey($model->{$this->foreignKey});
                $this->dictionary[$morphTypeKey][$foreignKeyKey][] = $model;
            }
        }
    }
    /**
     * Get the results of the relationship.
     *
     * Called via eager load method of Eloquent query builder.
     *
     * @return mixed
     */
    public function getEager()
    {
        foreach (\array_keys($this->dictionary) as $type) {
            $this->matchToMorphParents($type, $this->getResultsByType($type));
        }
        return $this->models;
    }
    /**
     * Get all of the relation results for a type.
     *
     * @param  string  $type
     * @return \Illuminate\Database\Eloquent\Collection
     */
    protected function getResultsByType($type)
    {
        $instance = $this->createModelByType($type);
        $ownerKey = $this->ownerKey ?? $instance->getKeyName();
        $query = $this->replayMacros($instance->newQuery())->mergeConstraintsFrom($this->getQuery())->with(\array_merge($this->getQuery()->getEagerLoads(), (array) ($this->morphableEagerLoads[\get_class($instance)] ?? [])))->withCount((array) ($this->morphableEagerLoadCounts[\get_class($instance)] ?? []));
        if ($callback = $this->morphableConstraints[\get_class($instance)] ?? null) {
            $callback($query);
        }
        $whereIn = $this->whereInMethod($instance, $ownerKey);
        return $query->{$whereIn}($instance->getTable() . '.' . $ownerKey, $this->gatherKeysByType($type, $instance->getKeyType()))->get();
    }
    /**
     * Gather all of the foreign keys for a given type.
     *
     * @param  string  $type
     * @param  string  $keyType
     * @return array
     */
    protected function gatherKeysByType($type, $keyType)
    {
        return $keyType !== 'string' ? \array_keys($this->dictionary[$type]) : \array_map(function ($modelId) {
            return (string) $modelId;
        }, \array_filter(\array_keys($this->dictionary[$type])));
    }
    /**
     * Create a new model instance by type.
     *
     * @param  string  $type
     * @return \Illuminate\Database\Eloquent\Model
     */
    public function createModelByType($type)
    {
        $class = Model::getActualClassNameForMorph($type);
        return \OtomaticAi\Vendors\tap(new $class(), function ($instance) {
            if (!$instance->getConnectionName()) {
                $instance->setConnection($this->getConnection()->getName());
            }
        });
    }
    /**
     * Match the eagerly loaded results to their parents.
     *
     * @param  array  $models
     * @param  \Illuminate\Database\Eloquent\Collection  $results
     * @param  string  $relation
     * @return array
     */
    public function match(array $models, Collection $results, $relation)
    {
        return $models;
    }
    /**
     * Match the results for a given type to their parents.
     *
     * @param  string  $type
     * @param  \Illuminate\Database\Eloquent\Collection  $results
     * @return void
     */
    protected function matchToMorphParents($type, Collection $results)
    {
        foreach ($results as $result) {
            $ownerKey = !\is_null($this->ownerKey) ? $this->getDictionaryKey($result->{$this->ownerKey}) : $result->getKey();
            if (isset($this->dictionary[$type][$ownerKey])) {
                foreach ($this->dictionary[$type][$ownerKey] as $model) {
                    $model->setRelation($this->relationName, $result);
                }
            }
        }
    }
    /**
     * Associate the model instance to the given parent.
     *
     * @param  \Illuminate\Database\Eloquent\Model  $model
     * @return \Illuminate\Database\Eloquent\Model
     */
    public function associate($model)
    {
        if ($model instanceof Model) {
            $foreignKey = $this->ownerKey && $model->{$this->ownerKey} ? $this->ownerKey : $model->getKeyName();
        }
        $this->parent->setAttribute($this->foreignKey, $model instanceof Model ? $model->{$foreignKey} : null);
        $this->parent->setAttribute($this->morphType, $model instanceof Model ? $model->getMorphClass() : null);
        return $this->parent->setRelation($this->relationName, $model);
    }
    /**
     * Dissociate previously associated model from the given parent.
     *
     * @return \Illuminate\Database\Eloquent\Model
     */
    public function dissociate()
    {
        $this->parent->setAttribute($this->foreignKey, null);
        $this->parent->setAttribute($this->morphType, null);
        return $this->parent->setRelation($this->relationName, null);
    }
    /**
     * Touch all of the related models for the relationship.
     *
     * @return void
     */
    public function touch()
    {
        if (!\is_null($this->child->{$this->foreignKey})) {
            parent::touch();
        }
    }
    /**
     * Make a new related instance for the given model.
     *
     * @param  \Illuminate\Database\Eloquent\Model  $parent
     * @return \Illuminate\Database\Eloquent\Model
     */
    protected function newRelatedInstanceFor(Model $parent)
    {
        return $parent->{$this->getRelationName()}()->getRelated()->newInstance();
    }
    /**
     * Get the foreign key "type" name.
     *
     * @return string
     */
    public function getMorphType()
    {
        return $this->morphType;
    }
    /**
     * Get the dictionary used by the relationship.
     *
     * @return array
     */
    public function getDictionary()
    {
        return $this->dictionary;
    }
    /**
     * Specify which relations to load for a given morph type.
     *
     * @param  array  $with
     * @return \Illuminate\Database\Eloquent\Relations\MorphTo
     */
    public function morphWith(array $with)
    {
        $this->morphableEagerLoads = \array_merge($this->morphableEagerLoads, $with);
        return $this;
    }
    /**
     * Specify which relationship counts to load for a given morph type.
     *
     * @param  array  $withCount
     * @return \Illuminate\Database\Eloquent\Relations\MorphTo
     */
    public function morphWithCount(array $withCount)
    {
        $this->morphableEagerLoadCounts = \array_merge($this->morphableEagerLoadCounts, $withCount);
        return $this;
    }
    /**
     * Specify constraints on the query for a given morph type.
     *
     * @param  array  $callbacks
     * @return \Illuminate\Database\Eloquent\Relations\MorphTo
     */
    public function constrain(array $callbacks)
    {
        $this->morphableConstraints = \array_merge($this->morphableConstraints, $callbacks);
        return $this;
    }
    /**
     * Replay stored macro calls on the actual related instance.
     *
     * @param  \Illuminate\Database\Eloquent\Builder  $query
     * @return \Illuminate\Database\Eloquent\Builder
     */
    protected function replayMacros(Builder $query)
    {
        foreach ($this->macroBuffer as $macro) {
            $query->{$macro['method']}(...$macro['parameters']);
        }
        return $query;
    }
    /**
     * Handle dynamic method calls to the relationship.
     *
     * @param  string  $method
     * @param  array  $parameters
     * @return mixed
     */
    public function __call($method, $parameters)
    {
        try {
            $result = parent::__call($method, $parameters);
            if (\in_array($method, ['select', 'selectRaw', 'selectSub', 'addSelect', 'withoutGlobalScopes'])) {
                $this->macroBuffer[] = \compact('method', 'parameters');
            }
            return $result;
        } catch (BadMethodCallException $e) {
            $this->macroBuffer[] = \compact('method', 'parameters');
            return $this;
        }
    }
}
