<?php

namespace OtomaticAi\Content\Html;

use OtomaticAi\Content\Contracts\ShouldDisplay;
use OtomaticAi\Utils\Crawler;
use OtomaticAi\Vendors\Illuminate\Support\Arr;

class TableElement implements ShouldDisplay
{
    const KEY = "html-table-element";

    public $thead;
    public $tbody;
    public $tfoot;

    public function __construct($thead = [], $tbody = [], $tfoot = [])
    {
        $this->thead = $thead;
        $this->tbody = $tbody;
        $this->tfoot = $tfoot;
    }

    public function setThead($row)
    {
        $this->thead = $row;
    }

    public function setTfoot($row)
    {
        $this->tfoot = $row;
    }

    public function addTbody($row)
    {
        $this->tbody[] = $row;
    }

    public function display()
    {
        $html = [];

        $html[] = '<!-- wp:table -->';
        $html[] = '<figure class="wp-block-table">';
        $html[] = '<table>';
        if (count($this->thead) > 0) {
            $html[] = '<thead>';
            $html[] = '<tr>';
            foreach ($this->thead as $th) {
                $html[] = '<th>' . $th . '</th>';
            }
            $html[] = '</tr>';
            $html[] = '</thead>';
        }
        if (count($this->tbody) > 0) {
            $html[] = '<tbody>';
            foreach ($this->tbody as $tr) {
                $html[] = '<tr>';
                foreach ($tr as $td) {
                    $html[] = '<td>' . $td . '</td>';
                }
                $html[] = '</tr>';
            }
            $html[] = '</tbody>';
        }
        if (count($this->tfoot) > 0) {
            $html[] = '<tfoot>';
            $html[] = '<tr>';
            foreach ($this->tfoot as $th) {
                $html[] = '<td>' . $th . '</td>';
            }
            $html[] = '</tr>';
            $html[] = '</tfoot>';
        }
        $html[] = '</table>';
        $html[] = '</figure>';
        $html[] = '<!-- /wp:table -->';


        return implode("\n", $html);
    }

    public function toText()
    {
        $parts = [];

        foreach ($this->thead as $th) {
            $parts[] = $th;
        }

        foreach ($this->tbody as $tr) {
            foreach ($tr as $td) {
                $parts[] = $td;
            }
        }

        foreach ($this->tfoot as $th) {
            $parts[] = $th;
        }

        return implode("\n", $parts);
    }

    static public function make($html)
    {
        $crawler = new Crawler($html);

        if ($crawler->filter("table")->count() > 0) {
            $node = $crawler->filter("table")->first();

            $table = new self();

            if ($node->filter("thead,tbody,tfoot")->count() > 0) {
                if ($node->filter("thead")->count() > 0) {
                    $row = [];
                    foreach ($node->filter("thead th, thead td") as $th) {
                        $th = new Crawler($th);
                        $row[] = $th->html();
                    }
                    $table->setThead($row);
                }

                if ($node->filter("tbody")->count() > 0) {
                    $row = [];
                    foreach ($node->filter("tbody tr") as $tr) {
                        $row = [];
                        $tr = new Crawler($tr);
                        foreach ($tr->filter("th,td") as $td) {
                            $td = new Crawler($td);
                            $row[] = $td->html();
                        }
                        $table->addTbody($row);
                    }
                }

                if ($node->filter("tfoot")->count() > 0) {
                    $row = [];
                    foreach ($node->filter("tfoot td, tfoot td") as $td) {
                        $td = new Crawler($td);
                        $row[] = $td->html();
                    }
                    $table->setTfoot($row);
                }
            } else if ($node->filter("tr")->count() > 0) {
                $row = [];
                foreach ($node->filter("tr") as $tr) {
                    $row = [];
                    $tr = new Crawler($tr);
                    foreach ($tr->filter("th,td") as $td) {
                        $td = new Crawler($td);
                        $row[] = $td->html();
                    }
                    $table->addTbody($row);
                }
            }

            return $table;
        }

        return null;
    }

    public function toArray()
    {
        return [
            "key" => self::KEY ?? "",
            "thead" => $this->thead,
            "tbody" => $this->tbody,
            "tfoot" => $this->tfoot,
        ];
    }

    static public function fromArray($array)
    {
        return new self(Arr::get($array, "thead", []), Arr::get($array, "tbody", []), Arr::get($array, "tfoot", []));
    }
}
