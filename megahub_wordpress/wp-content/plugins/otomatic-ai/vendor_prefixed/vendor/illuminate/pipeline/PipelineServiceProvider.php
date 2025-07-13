<?php

namespace OtomaticAi\Vendors\Illuminate\Pipeline;

use OtomaticAi\Vendors\Illuminate\Contracts\Pipeline\Hub as PipelineHubContract;
use OtomaticAi\Vendors\Illuminate\Contracts\Support\DeferrableProvider;
use OtomaticAi\Vendors\Illuminate\Support\ServiceProvider;
class PipelineServiceProvider extends ServiceProvider implements DeferrableProvider
{
    /**
     * Register the service provider.
     *
     * @return void
     */
    public function register()
    {
        $this->app->singleton(PipelineHubContract::class, Hub::class);
    }
    /**
     * Get the services provided by the provider.
     *
     * @return array
     */
    public function provides()
    {
        return [PipelineHubContract::class];
    }
}
