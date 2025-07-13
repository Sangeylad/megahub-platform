<?php

namespace OtomaticAi\Jobs;

use ActionScheduler;
use ActionScheduler_Store;
use OtomaticAi\Models\Publication;
use OtomaticAi\Utils\Scheduler;
use OtomaticAi\Vendors\Illuminate\Support\Arr;

class ProcessFailedScheduleJob extends Job
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
        // get pending publications
        $publications = Publication::pending()
            ->get();

        foreach ($publications as $publication) {
            $actions = Scheduler::get(
                "publish_publication",
                [$publication->id],
                [
                    "status" => ActionScheduler_Store::STATUS_FAILED,
                    "date" => $publication->published_at,
                    "date_compare" => ">=",
                ]
            );

            if (!empty($actions)) {
                // find log
                $actionIds = array_keys($actions);
                $logger = ActionScheduler::logger();
                $logs = $logger->get_logs(Arr::last($actionIds));
                if (!empty($logs)) {
                    $log = Arr::last($logs);
                    $publication->addLog("Publication failed. " . $log->get_message(), "error");
                } else {
                    $publication->addLog("Publication failed. Unknown error occurred.", "error");
                }

                // set publication to failed
                $publication->status = "failed";
                $publication->save();
            }
        }
    }
}
