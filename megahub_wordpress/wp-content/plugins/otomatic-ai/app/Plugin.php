<?php

namespace OtomaticAi;

use Exception;
use OtomaticAi\Database\Migrator;
use OtomaticAi\Jobs\CheckPublicationsJob;
use OtomaticAi\Jobs\PublishPublicationJob;
use OtomaticAi\Jobs\ProcessFailedScheduleJob;
use OtomaticAi\Jobs\RunAutopilotJob;
use OtomaticAi\Models\Publication;
use OtomaticAi\Utils\Auth;
use OtomaticAi\Utils\Language;
use OtomaticAi\Utils\Linking\Linking;
use OtomaticAi\Utils\Scheduler;
use OtomaticAi\Vendors\Illuminate\Database\Capsule\Manager as Database;
use OtomaticAi\Vendors\Illuminate\Support\Arr;
use OtomaticAi\Vendors\Illuminate\Support\Collection;
use OtomaticAi\Vendors\Illuminate\Support\Str;

class Plugin
{
    public function run()
    {
        $this->database();
        $this->macros();
        $this->schedules();

        if (function_exists("is_admin") && is_admin()) {
            $this->admin();
        } else {
            $this->public();
        }
    }

    private function admin()
    {
        // define menu
        add_action('admin_menu', function () {
            add_menu_page(
                'otomatic.ai',
                'otomatic.ai',
                'manage_options',
                OTOMATIC_AI_NAME,
                function () {
                    wp_enqueue_media();

                    $updates = get_plugin_updates();
                    $outdated = isset($updates[OTOMATIC_AI_NAME . "/" . OTOMATIC_AI_NAME . ".php"]);
                    $domain = null;
                    try {
                        $domain = Auth::domain();
                    } catch (Exception $e) {
                    }
                    $data = [
                        "domain" => $domain,
                        "ajaxurl" => admin_url('admin-ajax.php'),
                        "nonce" => wp_create_nonce(OTOMATIC_AI_NONCE),
                        "version" => ["number" => OTOMATIC_AI_VERSION, "outdated" => $outdated],
                        "public_path" => OTOMATIC_AI_ROOT_URL . 'public',
                        "admin_url" =>  admin_url(),
                        "authenticated" => Auth::check(),
                        "default_locale" => Language::findFromLocale()->key,
                    ];
                    wp_enqueue_script('otomatic-ai-app', OTOMATIC_AI_ROOT_URL . 'public/js/otomatic-ai.js', ['wp-i18n'], OTOMATIC_AI_VERSION, true);
                    wp_enqueue_style('otomatic-ai-app',  OTOMATIC_AI_ROOT_URL . 'public/css/otomatic-ai.css', [], OTOMATIC_AI_VERSION);
                    wp_set_script_translations('otomatic-ai-app', OTOMATIC_AI_NAME, OTOMATIC_AI_ROOT_PATH . 'languages/');
                    wp_add_inline_script('otomatic-ai-app', 'var otomatic_ai = ' . json_encode($data) . ';', "before");

                    echo "<div id='otomatic-ai-app' class='otomatic-ai-app'></div>";
                },
                OTOMATIC_AI_ROOT_URL . 'public/img/logo-sidebar.png',
                2,
            );

            if (defined("OTOMATIC_AI_TEST") && OTOMATIC_AI_TEST) {
                add_submenu_page(OTOMATIC_AI_NAME, "otomatic", 'test', "manage_options", OTOMATIC_AI_NAME . "-test", [$this, "test"]);
                add_submenu_page(OTOMATIC_AI_NAME, "otomatic", 'Run Publication', "manage_options", OTOMATIC_AI_NAME . "-run-publication", [$this, "runPublication"]);
            }
        });

        require_once plugin_dir_path(__FILE__) . '../routes/ajax.php';
    }

    private function public()
    {
        add_filter('the_content', [Linking::class, 'filter'], 1);
    }

    private function macros()
    {
        /**
         * Clean a string text
         * 
         * @param  string  $str
         * @return string
         */
        Str::macro('clean', function ($str) {

            if (is_array($str)) {
                $str = implode(" ", Arr::flatten($str));
            }
            $str = explode("\n", $str);
            $str = array_map(function ($line) {
                $line = strip_tags($line);
                $line = trim($line, " \"'\)\]\}\(\[\{\t\n\r\0\x0B");
                $line = preg_replace('/^[\d\.\-\#]+/', '', $line);
                $line = trim($line, " \"'\)\]\}\(\[\{\t\n\r\0\x0B");
                return $line;
            }, $str);

            return implode("\n", $str);
        });

        /**
         * Key an associative array by a field or using a callback.
         *
         * @param  array  $array
         * @param  callable|array|string  $keyBy
         * @return array
         */
        Arr::macro('keyBy', function ($array, $keyBy) {
            return Collection::make($array)->keyBy($keyBy)->all();
        });

        /**
         * Key an associative array by a field or using a callback.
         *
         * @param  array  $array
         * @param  callable|array|string  $keyBy
         * @return array
         */
        Arr::macro('partition', function ($array, $length) {
            $listLength = count($array);
            $partLength = floor($listLength / $length);
            $partrem = $listLength % $length;
            $partition = array();
            $mark = 0;

            for ($px = 0; $px < $length; $px++) {
                $incr = ($px < $partrem) ? $partLength + 1 : $partLength;
                $partition[$px] = array_slice($array, $mark, $incr);
                $mark += $incr;
            }

            return $partition;
        });
    }

    private function database()
    {
        global $wpdb;

        // database manager
        $database = new Database();
        $hostParts = explode(":", DB_HOST);
        $database->addConnection([
            'driver' => 'mysql',
            'host' =>  Arr::get($hostParts, 0),
            'port' => Arr::get($hostParts, 1, "3306"),
            'database' => DB_NAME,
            'username' => DB_USER,
            'password' => DB_PASSWORD,
            'charset' => defined("DB_CHARSET") ? DB_CHARSET : 'utf8',
            'collation' => defined("DB_COLLATE") && strlen(DB_COLLATE) > 0 ? DB_COLLATE : null
        ]);
        $database->setAsGlobal();
        $database->bootEloquent();
    }

    public function activate()
    {
        Migrator::run();
    }

    private function schedules()
    {
        // init
        Scheduler::init();

        // register
        Scheduler::register("run_autopilot_job", function () {
            $job = new RunAutopilotJob;
            $job->handle();
        });
        Scheduler::register("check_publications_to_publish", function () {
            $job = new CheckPublicationsJob;
            $job->handle();
        });
        Scheduler::register("process_failed_shedules", function () {
            $job = new ProcessFailedScheduleJob;
            $job->handle();
        });
        Scheduler::register("publish_publication", function ($publication) {
            $publication = Publication::find($publication);
            if ($publication) {
                $job = new PublishPublicationJob($publication);
                $job->handle();
            }
        });

        // run
        Scheduler::schedule("run_autopilot_job", Scheduler::EVERY_HOURS);
        Scheduler::schedule("check_publications_to_publish", Scheduler::EVERY_MINUTES);
        Scheduler::schedule("process_failed_shedules", Scheduler::EVERY_MINUTES);
    }

    public function test()
    {
        echo "<pre>";
        echo "</pre>";
    }

    public function runPublication()
    {
        $id = Arr::get($_GET, 'publication');
        if (!empty($id)) {
            $publication = Publication::find($id);
            $publication->status = "idle";
            $publication->save();
            echo "<pre>";
            $job = new PublishPublicationJob($publication);
            $job->handle();
            echo "</pre>";
        }
?>
        <form method="GET">
            <label for="publication">Publication ID</label>
            <input id="publication" name="publication" type="text" value="<?php echo $id; ?>" />
            <input name="page" type="hidden" value="<?php echo $_GET["page"]; ?>" />
            <button tupe="submit">Run</button>
        </form>
<?php

    }
}
