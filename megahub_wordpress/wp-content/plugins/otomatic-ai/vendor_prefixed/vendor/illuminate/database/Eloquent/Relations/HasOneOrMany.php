<?php

namespace OtomaticAi\Vendors\Illuminate\Database\Eloquent\Relations;

use OtomaticAi\Vendors\Illuminate\Database\Eloquent\Builder;
use OtomaticAi\Vendors\Illuminate\Database\Eloquent\Collection;
use OtomaticAi\Vendors\Illuminate\Database\Eloquent\Model;
use OtomaticAi\Vendors\Illuminate\Database\Eloquent\Relations\Concerns\InteractsWithDictionary;
abstract class HasOneOrMany extends Relation
{
    use InteractsWithDictionary;
    /**
     * The foreign key of the parent model.
     *
     * @var string
     */
    protected $foreignKey;
    /**
     * The local key of the parent model.
     *
     * @var string
     */
    protected $localKey;
    /**
     * Create a new has one or many relationship instance.
     *
     * @param  \Illuminate\Database\Eloquent\Builder  $query
     * @param  \Illuminate\Database\Eloquent\Model  $parent
     * @param  string  $foreignKey
     * @param  string  $localKey
     * @return void
     */
    public function __construct(Builder $query, Model $parent, $foreignKey, $localKey)
    {
        $this->localKey = $localKey;
        $this->foreignKey = $foreignKey;
        parent::__construct($query, $parent);
    }
    /**
     * Create and return an un-saved instance of the related model.
     *
     * @param  array  $attributes
     * @return \Illuminate\Database\Eloquent\Model
     */
    public function make(array $attributes = [])
    {
        return \OtomaticAi\Vendors\tap($this->related->newInstance($attributes), function ($instance) {
            $this->setForeignAttributesForCreate($instance);
        });
    }
    /**
     * Create and return an un-saved instance of the related models.
     *
     * @param  iterable  $records
     * @return \Illuminate\Database\Eloquent\Collection
     */
    public function makeMany($records)
    {
        $instances = $this->related->newCollection();
        foreach ($records as $record) {
            $instances->push($this->make($record));
        }
        return $instances;
    }
    /**
     * Set the base constraints on the relation query.
     *
     * @return void
     */
    public function addConstraints()
    {
        if (static::$constraints) {
            $query = $this->getRelationQuery();
            $query->where($this->foreignKey, '=', $this->getParentKey());
            $query->whereNotNull($this->foreignKey);
        }
    }
    /**
     * Set the constraints for an eager load of the relation.
     *
     * @param  array  $models
     * @return void
     */
    public function addEagerConstraints(array $models)
    {
        $whereIn = $this->whereInMethod($this->parent, $this->localKey);
        $this->getRelationQuery()->{$whereIn}($this->foreignKey, $this->getKeys($models, $this->localKey));
    }
    /**
     * Match the eagerly loaded results to their single parents.
     *
     * @param  array  $models
     * @param  \Illuminate\Database\Eloquent\Collection  $results
     * @param  string  $relation
     * @return array
     */
    public function matchOne(array $models, Collection $results, $relation)
    {
        return $this->matchOneOrMany($models, $results, $relation, 'one');
    }
    /**
     * Match the eagerly loaded results to their many parents.
     *
     * @param  array  $models
     * @param  \Illuminate\Database\Eloquent\Collection  $results
     * @param  string  $relation
     * @return array
     */
    public function matchMany(array $models, Collection $results, $relation)
    {
        return $this->matchOneOrMany($models, $results, $relation, 'many');
    }
    /**
     * Match the eagerly loaded results to their many parents.
     *
     * @param  array  $models
     * @param  \Illuminate\Database\Eloquent\Collection  $results
     * @param  string  $relation
     * @param  string  $type
     * @return array
     */
    protected function matchOneOrMany(array $models, Collection $results, $relation, $type)
    {
        $dictionary = $this->buildDictionary($results);
        // Once we have the dictionary we can simply spin through the parent models to
        // link them up with their children using the keyed dictionary to make the
        // matching very convenient and easy work. Then we'll just return them.
        foreach ($models as $model) {
            if (isset($dictionary[$key = $this->getDictionaryKey($model->getAttribute($this->localKey))])) {
                $model->setRelation($relation, $this->getRelationValue($dictionary, $key, $type));
            }
        }
        return $models;
    }
    /**
     * Get the value of a relationship by one or many type.
     *
     * @param  array  $dictionary
     * @param  string  $key
     * @param  string  $type
     * @return mixed
     */
    protected function getRelationValue(array $dictionary, $key, $type)
    {
        $value = $dictionary[$key];
        return $type === 'one' ? \reset($value) : $this->related->newCollection($value);
    }
    /**
     * Build model dictionary keyed by the relation's foreign key.
     *
     * @param  \Illuminate\Database\Eloquent\Collection  $results
     * @return array
     */
    protected function buildDictionary(Collection $results)
    {
        $foreign = $this->getForeignKeyName();
        return $results->mapToDictionary(function ($result) use($foreign) {
            return [$this->getDictionaryKey($result->{$foreign}) => $result];
        })->all();
    }
    /**
     * Find a model by its primary key or return a new instance of the related model.
     *
     * @param  mixed  $id
     * @param  array  $columns
     * @return \Illuminate\Support\Collection|\Illuminate\Database\Eloquent\Model
     */
    public function findOrNew($id, $columns = ['*'])
    {
        if (\is_null($instance = $this->find($id, $columns))) {
            $instance = $this->related->newInstance();
            $this->setForeignAttributesForCreate($instance);
        }
        return $instance;
    }
    /**
     * Get the first related model record matching the attributes or instantiate it.
     *
     * @param  array  $attributes
     * @param  array  $values
     * @return \Illuminate\Database\Eloquent\Model
     */
    public function firstOrNew(array $attributes = [], array $values = [])
    {
        if (\is_null($instance = $this->where($attributes)->first())) {
            $instance = $this->related->newInstance(\array_merge($attributes, $values));
            $this->setForeignAttributesForCreate($instance);
        }
        return $instance;
    }
    /**
     * Get the first related record matching the attributes or create it.
     *
     * @param  array  $attributes
     * @param  array  $values
     * @return \Illuminate\Database\Eloquent\Model
     */
    public function firstOrCreate(array $attributes = [], array $values = [])
    {
        if (\is_null($instance = $this->where($attributes)->first())) {
            $instance = $this->create(\array_merge($attributes, $values));
        }
        return $instance;
    }
    /**
     * Create or update a related record matching the attributes, and fill it with values.
     *
     * @param  array  $attributes
     * @param  array  $values
     * @return \Illuminate\Database\Eloquent\Model
     */
    public function updateOrCreate(array $attributes, array $values = [])
    {
        return \OtomaticAi\Vendors\tap($this->firstOrNew($attributes), function ($instance) use($values) {
            $instance->fill($values);
            $instance->save();
        });
    }
    /**
     * Attach a model instance to the parent model.
     *
     * @param  \Illuminate\Database\Eloquent\Model  $model
     * @return \Illuminate\Database\Eloquent\Model|false
     */
    public function save(Model $model)
    {
        $this->setForeignAttributesForCreate($model);
        return $model->save() ? $model : \false;
    }
    /**
     * Attach a collection of models to the parent instance.
     *
     * @param  iterable  $models
     * @return iterable
     */
    public function saveMany($models)
    {
        foreach ($models as $model) {
            $this->save($model);
        }
        return $models;
    }
    /**
     * Create a new instance of the related model.
     *
     * @param  array  $attributes
     * @return \Illuminate\Database\Eloquent\Model
     */
    public function create(array $attributes = [])
    {
        return \OtomaticAi\Vendors\tap($this->related->newInstance($attributes), function ($instance) {
            $this->setForeignAttributesForCreate($instance);
            $instance->save();
        });
    }
    /**
     * Create a new instance of the related model. Allow mass-assignment.
     *
     * @param  array  $attributes
     * @return \Illuminate\Database\Eloquent\Model
     */
    public function forceCreate(array $attributes = [])
    {
        $attributes[$this->getForeignKeyName()] = $this->getParentKey();
        return $this->related->forceCreate($attributes);
    }
    /**
     * Create a Collection of new instances of the related model.
     *
     * @param  iterable  $records
     * @return \Illuminate\Database\Eloquent\Collection
     */
    public function createMany(iterable $records)
    {
        $instances = $this->related->newCollection();
        foreach ($records as $record) {
            $instances->push($this->create($record));
        }
        return $instances;
    }
    /**
     * Set the foreign ID for creating a related model.
     *
     * @param  \Illuminate\Database\Eloquent\Model  $model
     * @return void
     */
    protected function setForeignAttributesForCreate(Model $model)
    {
        $model->setAttribute($this->getForeignKeyName(), $this->getParentKey());
    }
    /**
     * Add the constraints for a relationship query.
     *
     * @param  \Illuminate\Database\Eloquent\Builder  $query
     * @param  \Illuminate\Database\Eloquent\Builder  $parentQuery
     * @param  array|mixed  $columns
     * @return \Illuminate\Database\Eloquent\Builder
     */
    public function getRelationExistenceQuery(Builder $query, Builder $parentQuery, $columns = ['*'])
    {
        if ($query->getQuery()->from == $parentQuery->getQuery()->from) {
            return $this->getRelationExistenceQueryForSelfRelation($query, $parentQuery, $columns);
        }
        return parent::getRelationExistenceQuery($query, $parentQuery, $columns);
    }
    /**
     * Add the constraints for a relationship query on the same table.
     *
     * @param  \Illuminate\Database\Eloquent\Builder  $query
     * @param  \Illuminate\Database\Eloquent\Builder  $parentQuery
     * @param  array|mixed  $columns
     * @return \Illuminate\Database\Eloquent\Builder
     */
    public function getRelationExistenceQueryForSelfRelation(Builder $query, Builder $parentQuery, $columns = ['*'])
    {
        $query->from($query->getModel()->getTable() . ' as ' . ($hash = $this->getRelationCountHash()));
        $query->getModel()->setTable($hash);
        return $query->select($columns)->whereColumn($this->getQualifiedParentKeyName(), '=', $hash . '.' . $this->getForeignKeyName());
    }
    /**
     * Get the key for comparing against the parent key in "has" query.
     *
     * @return string
     */
    public function getExistenceCompareKey()
    {
        return $this->getQualifiedForeignKeyName();
    }
    /**
     * Get the key value of the parent's local key.
     *
     * @return mixed
     */
    public function getParentKey()
    {
        return $this->parent->getAttribute($this->localKey);
    }
    /**
     * Get the fully qualified parent key name.
     *
     * @return string
     */
    public function getQualifiedParentKeyName()
    {
        return $this->parent->qualifyColumn($this->localKey);
    }
    /**
     * Get the plain foreign key.
     *
     * @return string
     */
    public function getForeignKeyName()
    {
        $segments = \explode('.', $this->getQualifiedForeignKeyName());
        return \end($segments);
    }
    /**
     * Get the foreign key for the relationship.
     *
     * @return string
     */
    public function getQualifiedForeignKeyName()
    {
        return $this->foreignKey;
    }
    /**
     * Get the local key for the relationship.
     *
     * @return string
     */
    public function getLocalKeyName()
    {
        return $this->localKey;
    }
}
