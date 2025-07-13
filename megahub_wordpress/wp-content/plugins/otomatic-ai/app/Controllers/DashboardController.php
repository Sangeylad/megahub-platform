<?php

namespace OtomaticAi\Controllers;

use OtomaticAi\Models\Project;
use OtomaticAi\Models\Publication;
use OtomaticAi\Vendors\Carbon\Carbon;

class DashboardController extends Controller
{
    public function globalMetrics()
    {
        $this->verifyNonce();

        $output = [
            "projects" => [
                "total" => Project::count(),
                "completed" => Project::completed()->count(),
            ],
            "publications" => [
                "published" => Publication::published()->count(),
                "idle" => Publication::idle()->count(),
            ],
        ];

        $this->response($output);
    }

    public function getLatestPublications()
    {
        $this->verifyNonce();

        return Publication::published()->orderBy("published_at", "desc")->limit(5)->get();
    }

    public function getNextPublications()
    {
        $this->verifyNonce();

        return Publication::idle()->where("published_at", ">", Carbon::now())->orderBy("published_at", "asc")->limit(5)->get();
    }

    public function latestPublications()
    {
        $this->verifyNonce();

        $publications = Publication::published()->orderBy("published_at", "desc")->limit(5)->get();

        $this->response($publications);
    }

    public function nextPublications()
    {
        $this->verifyNonce();

        $publications = Publication::idle()->where("published_at", ">", Carbon::now())->orderBy("published_at", "asc")->limit(5)->get();

        $this->response($publications);
    }
}
