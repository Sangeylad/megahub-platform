<?php

namespace OtomaticAi\Jobs;

use OtomaticAi\Models\Publication;
use OtomaticAi\Utils\Scheduler;
use OtomaticAi\Vendors\Carbon\Carbon;

class CheckPublicationsJob extends Job
{

    /**
     * Create a new job instance.
     */
    public function __construct()
    {
    }

    /**
     * Execute the job.
     */
    public function handle()
    {
        $publications = Publication::idle()
            ->whereRelation('project', 'enabled', true)
            ->where("published_at", "<=", Carbon::now())
            ->get();

        foreach ($publications as $publication) {
            Scheduler::single("publish_publication", [$publication->id]);
        }
    }
}
