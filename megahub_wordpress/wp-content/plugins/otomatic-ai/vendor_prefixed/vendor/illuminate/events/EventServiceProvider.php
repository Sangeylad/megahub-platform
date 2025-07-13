<?php

namespace OtomaticAi\Vendors\Illuminate\Events;

use OtomaticAi\Vendors\Illuminate\Contracts\Queue\Factory as QueueFactoryContract;
use OtomaticAi\Vendors\Illuminate\Support\ServiceProvider;
class EventServiceProvider extends ServiceProvider
{
    /**
     * Register the service provider.
     *
     * @return void
     */
    public function register()
    {
        $this->app->singleton('events', function ($app) {
            return (new Dispatcher($app))->setQueueResolver(function () use($app) {
                return $app->make(QueueFactoryContract::class);
            });
        });
    }
}
