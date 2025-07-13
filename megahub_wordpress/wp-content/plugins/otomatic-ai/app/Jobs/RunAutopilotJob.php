<?php

namespace OtomaticAi\Jobs;

use Exception;
use OtomaticAi\Models\Preset;
use OtomaticAi\Models\Project;
use OtomaticAi\Models\Publication;
use OtomaticAi\Utils\GoogleNews;
use OtomaticAi\Utils\RSS\Reader;
use OtomaticAi\Vendors\Carbon\Carbon;
use OtomaticAi\Vendors\Illuminate\Support\Arr;
use OtomaticAi\Vendors\Illuminate\Support\Str;

class RunAutopilotJob extends Job
{
    /**
     * Execute the job.
     */
    public function handle()
    {
        $now = Carbon::now();
        $projects = Project::where('enabled', true)
            ->whereIn("type", ["news", "rss"])
            ->whereRaw("JSON_UNQUOTE(JSON_EXTRACT(modules, '$.autopilot.planning.per_day')) > 0")
            ->get();

        foreach ($projects as $project) {
            $query = Arr::get($project->modules, "autopilot.query");
            $perDay = Arr::get($project->modules, "autopilot.planning.per_day", 1);

            if (empty($query)) {
                continue;
            }

            // count daily publication
            $publicationsCount = $project->publications()->whereBetween("published_at", [$now->copy()->startOfDay(), $now->copy()->endOfDay()])->count();

            // quit if perDay is exceeded
            if ($publicationsCount >= $perDay) {
                continue;
            }

            // calcul interval in minute between each publications
            $start = $now->copy()->startOfDay()->setHour(Arr::get($project->modules, "autopilot.planning.start_time.hours", 0))->setMinute(Arr::get($project->modules, "autopilot.planning.start_time.minutes", 0));
            $end = $now->copy()->startOfDay()->setHour(Arr::get($project->modules, "autopilot.planning.end_time.hours", 23))->setMinute(Arr::get($project->modules, "autopilot.planning.end_time.minutes", 59));
            $interval = $start->diffInMinutes($end);
            $interval = $perDay > 1 ? round($interval / ($perDay - 1)) : 0;

            // get the next date to publish
            $nextDate = $start->copy()->addMinutes($interval * $publicationsCount);

            // quit if the nextDate is in the future
            if ($now->lt($nextDate)) {
                continue;
            }

            switch ($project->type) {
                case "news":
                    $this->handleNewsAutopilot($project);
                    break;
                case "rss":
                    $this->handleRSSAutopilot($project);
                    break;
            }
        }
    }

    private function handleNewsAutopilot(Project $project)
    {
        $query = Arr::get($project->modules, "autopilot.query");

        try {

            $items = GoogleNews::search($query, $project->language);

            $selectedItem = null;
            foreach ($items as $item) {

                $title = $item["title"];
                $url = $item["url"];
                $guid = $item["url"];
                $guid = str_replace(["http://", "https://"], "", $guid);

                $pubDate = Arr::get($item, "pub_date");
                if (empty($pubDate)) {
                    continue;
                }

                $pubDate = Carbon::parse($pubDate);
                if ($pubDate->lt(Carbon::now()->subDays(2))) {
                    continue;
                }

                // check if guid is already inserted
                if (Publication::whereRaw("JSON_EXTRACT(meta, '$.guid') = ?", [$guid])->count() > 0) {
                    continue;
                };

                $selectedItem = [
                    "title" => $title,
                    "meta" => [
                        "url" => $url,
                        "guid" => $guid,
                    ]
                ];

                break;
            }

            // rewrite item title
            if ($selectedItem !== null) {

                // get the openai preset
                $preset = Preset::findFromAPI("requests_news_rewrite");

                // make payload
                $payload = [
                    "language" => $project->language->value,
                    "request" => $selectedItem["title"],
                ];

                // run the preset
                $response = $preset->process($payload);

                // get the response content
                $response = json_decode(Arr::get($response, 'choices.0.message.content'), true, 512, JSON_THROW_ON_ERROR);
                $value = Arr::get($response, "value");
                $value = Str::clean($value);
                if (!empty($value)) {
                    $selectedItem["title"] = $value;
                }

                // create the new publication
                $publication = new Publication([
                    "title" => $selectedItem["title"],
                    "meta" => $selectedItem["meta"],
                    "published_at" => Carbon::now(),
                ]);
                $publication->project()->associate($project);
                $publication->save();
            }
        } catch (Exception $e) {
        }
    }

    private function handleRSSAutopilot(Project $project)
    {
        $query = Arr::get($project->modules, "autopilot.query");

        try {
            $rss = Reader::load($query);

            $selectedItem = null;
            foreach ($rss->items as $item) {

                $url = (string) $item->url;
                $title = (string) $item->title;
                $guid = (string) $item->guid;
                if (strlen($guid) < 0) {
                    $guid = str_replace(["http://", "https://"], "", $url);
                }
                $guid = str_replace(["http://", "https://"], "", $guid);

                $pubDate = (string) $item->pubDate;
                if (empty($pubDate)) {
                    continue;
                }

                $pubDate = Carbon::parse($pubDate);
                if ($pubDate->lt(Carbon::now()->subDays(1))) {
                    continue;
                }

                // check if guid is already inserted
                if (Publication::whereRaw("JSON_EXTRACT(meta, '$.guid') = ?", [$guid])->count() > 0) {
                    continue;
                };

                $selectedItem = [
                    "title" => $title,
                    "meta" => [
                        "url" => $url,
                        "guid" => $guid,
                    ]
                ];

                break;
            }

            // rewrite item title
            if ($selectedItem !== null) {

                // get the openai preset
                $preset = Preset::findFromAPI("requests_informative_rewrite");

                // make payload
                $payload = [
                    "language" => $project->language->value,
                    "request" => $selectedItem["title"],
                ];

                // run the preset
                $response = $preset->process($payload);

                // get the response content
                $response = json_decode(Arr::get($response, 'choices.0.message.content'), true, 512, JSON_THROW_ON_ERROR);
                $value = Arr::get($response, "value");
                $value = Str::clean($value);
                if (!empty($value)) {
                    $selectedItem["title"] = $value;
                }

                // create the new publication
                $publication = new Publication([
                    "title" => $selectedItem["title"],
                    "meta" => $selectedItem["meta"],
                    "published_at" => Carbon::now(),
                ]);
                $publication->project()->associate($project);
                $publication->save();
            }
        } catch (Exception $e) {
        }
    }
}
