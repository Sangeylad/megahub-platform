<?php

namespace OtomaticAi\Controllers;

use OtomaticAi\Models\Project;
use OtomaticAi\Models\Publication;
use OtomaticAi\Vendors\Carbon\Carbon;
use OtomaticAi\Vendors\Illuminate\Database\Eloquent\Builder;
use OtomaticAi\Vendors\Illuminate\Support\Str;
use OtomaticAi\Vendors\Illuminate\Validation\Rule;

class PublicationController extends Controller
{
    public function index()
    {
        $this->verifyNonce();

        $this->validate([
            "project" => ["required", "integer"],
            "page" => ["nullable", "integer"],
            "sort_order" => ["nullable", "string"],
            "sort_direction" => ["nullable", "string", Rule::in(["asc", "desc"])],
            "search" => ["nullable", "string"],
        ]);

        $project = Project::with('persona')->find($this->input("project"));

        $publications = $this->makeQuery($project);
        $publications = $publications->paginate(20, ['*'], 'page', $this->input('page', 1))->onEachSide(1);

        $this->response([
            "project" => $project,
            "publications" => $publications
        ]);
    }

    public function publish()
    {
        $this->verifyNonce();

        $this->validate([
            "publication" => ["required", "integer"],
        ]);

        $publication = Publication::idle()->find($this->input('publication'));
        if ($publication) {
            $publication->published_at = Carbon::now();
            $publication->save();
        }

        $this->emptyResponse();
    }

    public function bulkPublish()
    {
        $this->verifyNonce();

        $this->validate([
            "publications" => ["required", "array"],
        ]);

        $ids = $this->input('publications', []);
        if (count($ids) > 0) {
            Publication::idle()->whereIn("id", $ids)->update([
                "published_at" => Carbon::now(),
            ]);
        }

        $this->emptyResponse();
    }

    public function retry()
    {
        $this->verifyNonce();

        $this->validate([
            "publication" => ["required", "integer"],
        ]);

        $publication = Publication::failed()->find($this->input('publication'));
        if ($publication) {
            $publication->status = 'idle';
            $publication->published_at = Carbon::now();
            $publication->save();
        }

        $this->emptyResponse();
    }

    public function regenerate()
    {
        $this->verifyNonce();

        $this->validate([
            "publication" => ["required", "integer"],
        ]);

        $publication = Publication::published()->find($this->input('publication'));
        if ($publication) {
            $publication->status = 'idle';
            $publication->published_at = Carbon::now();
            $publication->save();
        }

        $this->emptyResponse();
    }

    public function bulkRegenerate()
    {
        $this->verifyNonce();

        $this->validate([
            "publications" => ["required", "array"],
        ]);

        $ids = $this->input('publications', []);
        $projectsIds = Publication::select('project_id')->whereIn("id", $ids)->get();
        $now = Carbon::now();
        if (count($ids) > 0) {
            Publication::whereIn("id", $ids)->where(function (Builder $query) {
                return $query->published()->orWhere->failed();
            })->update([
                "status" => "idle",
                "published_at" => $now,
            ]);

            // refresh project metrics
            if ($projectsIds->count() > 0) {
                $projects = Project::where('id', $projectsIds->pluck('project_id')->toArray())->get();
                foreach ($projects as $project) {
                    $project->refreshMetrics();
                }
            }
        }

        $this->emptyResponse();
    }

    public function destroy()
    {
        $this->verifyNonce();

        $this->validate([
            "publication" => ["required", "integer"],
        ]);

        $publication = Publication::find($this->input('publication'));
        if ($publication) {
            $publication->delete();
        }

        $this->emptyResponse();
    }

    public function bulkDestroy()
    {
        $this->verifyNonce();

        $this->validate([
            "publications" => ["required", "array"],
        ]);

        $ids = $this->input('publications', []);
        $projectsIds = Publication::select('project_id')->whereIn("id", $ids)->get();
        if (count($ids) > 0) {
            Publication::whereIn("id", $ids)->delete();

            // refresh project metrics
            if ($projectsIds->count() > 0) {
                $projects = Project::where('id', $projectsIds->pluck('project_id')->toArray())->get();
                foreach ($projects as $project) {
                    $project->refreshMetrics();
                }
            }
        }


        $this->emptyResponse();
    }

    private function makeQuery($project)
    {
        $publications = $project->publications();

        // sort 
        if (!empty($sortOrder = $this->input('sort_order', ''))) {
            $publications->orderBy($sortOrder, $this->input('sort_direction', 'desc'));
        } else {
            $publications->orderBy("id", "desc");
        }

        // filters
        if (!empty($search = $this->input('search', ''))) {
            $publications->where("title", 'like', '%' . Str::lower($search) . '%');
        }
        if (!empty($status = $this->input('status', ''))) {
            $publications->where("status", $status);
        }

        return $publications;
    }
}
