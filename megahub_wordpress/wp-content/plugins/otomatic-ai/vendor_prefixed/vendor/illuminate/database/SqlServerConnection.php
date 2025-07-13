<?php

namespace OtomaticAi\Vendors\Illuminate\Database;

use Closure;
use OtomaticAi\Vendors\Doctrine\DBAL\Driver\PDOSqlsrv\Driver as DoctrineDriver;
use OtomaticAi\Vendors\Doctrine\DBAL\Version;
use OtomaticAi\Vendors\Illuminate\Database\PDO\SqlServerDriver;
use OtomaticAi\Vendors\Illuminate\Database\Query\Grammars\SqlServerGrammar as QueryGrammar;
use OtomaticAi\Vendors\Illuminate\Database\Query\Processors\SqlServerProcessor;
use OtomaticAi\Vendors\Illuminate\Database\Schema\Grammars\SqlServerGrammar as SchemaGrammar;
use OtomaticAi\Vendors\Illuminate\Database\Schema\SqlServerBuilder;
use OtomaticAi\Vendors\Illuminate\Filesystem\Filesystem;
use RuntimeException;
use Throwable;
class SqlServerConnection extends Connection
{
    /**
     * Execute a Closure within a transaction.
     *
     * @param  \Closure  $callback
     * @param  int  $attempts
     * @return mixed
     *
     * @throws \Throwable
     */
    public function transaction(Closure $callback, $attempts = 1)
    {
        for ($a = 1; $a <= $attempts; $a++) {
            if ($this->getDriverName() === 'sqlsrv') {
                return parent::transaction($callback, $attempts);
            }
            $this->getPdo()->exec('BEGIN TRAN');
            // We'll simply execute the given callback within a try / catch block
            // and if we catch any exception we can rollback the transaction
            // so that none of the changes are persisted to the database.
            try {
                $result = $callback($this);
                $this->getPdo()->exec('COMMIT TRAN');
            } catch (Throwable $e) {
                $this->getPdo()->exec('ROLLBACK TRAN');
                throw $e;
            }
            return $result;
        }
    }
    /**
     * Get the default query grammar instance.
     *
     * @return \Illuminate\Database\Query\Grammars\SqlServerGrammar
     */
    protected function getDefaultQueryGrammar()
    {
        return $this->withTablePrefix(new QueryGrammar());
    }
    /**
     * Get a schema builder instance for the connection.
     *
     * @return \Illuminate\Database\Schema\SqlServerBuilder
     */
    public function getSchemaBuilder()
    {
        if (\is_null($this->schemaGrammar)) {
            $this->useDefaultSchemaGrammar();
        }
        return new SqlServerBuilder($this);
    }
    /**
     * Get the default schema grammar instance.
     *
     * @return \Illuminate\Database\Schema\Grammars\SqlServerGrammar
     */
    protected function getDefaultSchemaGrammar()
    {
        return $this->withTablePrefix(new SchemaGrammar());
    }
    /**
     * Get the schema state for the connection.
     *
     * @param  \Illuminate\Filesystem\Filesystem|null  $files
     * @param  callable|null  $processFactory
     *
     * @throws \RuntimeException
     */
    public function getSchemaState(Filesystem $files = null, callable $processFactory = null)
    {
        throw new RuntimeException('Schema dumping is not supported when using SQL Server.');
    }
    /**
     * Get the default post processor instance.
     *
     * @return \Illuminate\Database\Query\Processors\SqlServerProcessor
     */
    protected function getDefaultPostProcessor()
    {
        return new SqlServerProcessor();
    }
    /**
     * Get the Doctrine DBAL driver.
     *
     * @return \Doctrine\DBAL\Driver\PDOSqlsrv\Driver|\Illuminate\Database\PDO\SqlServerDriver
     */
    protected function getDoctrineDriver()
    {
        return \class_exists(Version::class) ? new DoctrineDriver() : new SqlServerDriver();
    }
}
