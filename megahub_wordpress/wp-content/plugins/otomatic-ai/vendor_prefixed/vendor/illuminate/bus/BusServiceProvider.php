<?php

namespace OtomaticAi\Vendors\Illuminate\Bus;

use OtomaticAi\Vendors\Illuminate\Contracts\Bus\Dispatcher as DispatcherContract;
use OtomaticAi\Vendors\Illuminate\Contracts\Bus\QueueingDispatcher as QueueingDispatcherContract;
use OtomaticAi\Vendors\Illuminate\Contracts\Queue\Factory as QueueFactoryContract;
use OtomaticAi\Vendors\Illuminate\Contracts\Support\DeferrableProvider;
use OtomaticAi\Vendors\Illuminate\Support\ServiceProvider;
class BusServiceProvider extends ServiceProvider implements DeferrableProvider
{
    /**
     * Register the service provider.
     *
     * @return void
     */
    public function register()
    {
        $this->app->singleton(Dispatcher::class, function ($app) {
            return new Dispatcher($app, function ($connection = null) use($app) {
                return $app[QueueFactoryContract::class]->connection($connection);
            });
        });
        $this->registerBatchServices();
        $this->app->alias(Dispatcher::class, DispatcherContract::class);
        $this->app->alias(Dispatcher::class, QueueingDispatcherContract::class);
    }
    /**
     * Register the batch handling services.
     *
     * @return void
     */
    protected function registerBatchServices()
    {
        $this->app->singleton(BatchRepository::class, DatabaseBatchRepository::class);
        $this->app->singleton(DatabaseBatchRepository::class, function ($app) {
            return new DatabaseBatchRepository($app->make(BatchFactory::class), $app->make('db')->connection($app->config->get('queue.batching.database')), $app->config->get('queue.batching.table', 'job_batches'));
        });
    }
    /**
     * Get the services provided by the provider.
     *
     * @return array
     */
    public function provides()
    {
        return [Dispatcher::class, DispatcherContract::class, QueueingDispatcherContract::class, BatchRepository::class];
    }
}
