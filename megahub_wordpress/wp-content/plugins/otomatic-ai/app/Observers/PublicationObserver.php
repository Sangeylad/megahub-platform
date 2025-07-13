<?php

namespace OtomaticAi\Observers;

use OtomaticAi\Models\Publication;

class PublicationObserver
{
    public function saved(Publication $model)
    {
        $model->project->refreshMetrics();
    }

    public function deleted(Publication $model)
    {
        $model->project->refreshMetrics();
    }
}
