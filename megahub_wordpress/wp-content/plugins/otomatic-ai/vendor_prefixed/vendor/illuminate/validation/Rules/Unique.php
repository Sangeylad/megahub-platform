<?php

namespace OtomaticAi\Vendors\Illuminate\Validation\Rules;

use OtomaticAi\Vendors\Illuminate\Database\Eloquent\Model;
use OtomaticAi\Vendors\Illuminate\Support\Traits\Conditionable;
class Unique
{
    use Conditionable, DatabaseRule;
    /**
     * The ID that should be ignored.
     *
     * @var mixed
     */
    protected $ignore;
    /**
     * The name of the ID column.
     *
     * @var string
     */
    protected $idColumn = 'id';
    /**
     * Ignore the given ID during the unique check.
     *
     * @param  mixed  $id
     * @param  string|null  $idColumn
     * @return $this
     */
    public function ignore($id, $idColumn = null)
    {
        if ($id instanceof Model) {
            return $this->ignoreModel($id, $idColumn);
        }
        $this->ignore = $id;
        $this->idColumn = $idColumn ?? 'id';
        return $this;
    }
    /**
     * Ignore the given model during the unique check.
     *
     * @param  \Illuminate\Database\Eloquent\Model  $model
     * @param  string|null  $idColumn
     * @return $this
     */
    public function ignoreModel($model, $idColumn = null)
    {
        $this->idColumn = $idColumn ?? $model->getKeyName();
        $this->ignore = $model->{$this->idColumn};
        return $this;
    }
    /**
     * Ignore soft deleted models during the unique check.
     *
     * @param  string  $deletedAtColumn
     * @return $this
     */
    public function withoutTrashed($deletedAtColumn = 'deleted_at')
    {
        $this->whereNull($deletedAtColumn);
        return $this;
    }
    /**
     * Convert the rule to a validation string.
     *
     * @return string
     */
    public function __toString()
    {
        return \rtrim(\sprintf('unique:%s,%s,%s,%s,%s', $this->table, $this->column, $this->ignore ? '"' . \addslashes($this->ignore) . '"' : 'NULL', $this->idColumn, $this->formatWheres()), ',');
    }
}
