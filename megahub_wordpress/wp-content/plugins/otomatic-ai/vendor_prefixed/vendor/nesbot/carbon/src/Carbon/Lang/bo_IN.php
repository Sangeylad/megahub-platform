<?php

namespace OtomaticAi\Vendors;

/**
 * This file is part of the Carbon package.
 *
 * (c) Brian Nesbitt <brian@nesbot.com>
 *
 * For the full copyright and license information, please view the LICENSE
 * file that was distributed with this source code.
 */
return \array_replace_recursive(require __DIR__ . '/bo.php', ['meridiem' => ['སྔ་དྲོ་', 'ཕྱི་དྲོ་'], 'weekdays' => ['གཟའ་ཉི་མ་', 'གཟའ་ཟླ་བ་', 'གཟའ་མིག་དམར་', 'གཟའ་ལྷག་པ་', 'གཟའ་ཕུར་བུ་', 'གཟའ་པ་སངས་', 'གཟའ་སྤེན་པ་'], 'weekdays_short' => ['ཉི་མ་', 'ཟླ་བ་', 'མིག་དམར་', 'ལྷག་པ་', 'ཕུར་བུ་', 'པ་སངས་', 'སྤེན་པ་'], 'weekdays_min' => ['ཉི་མ་', 'ཟླ་བ་', 'མིག་དམར་', 'ལྷག་པ་', 'ཕུར་བུ་', 'པ་སངས་', 'སྤེན་པ་'], 'months' => ['ཟླ་བ་དང་པོ', 'ཟླ་བ་གཉིས་པ', 'ཟླ་བ་གསུམ་པ', 'ཟླ་བ་བཞི་པ', 'ཟླ་བ་ལྔ་པ', 'ཟླ་བ་དྲུག་པ', 'ཟླ་བ་བདུན་པ', 'ཟླ་བ་བརྒྱད་པ', 'ཟླ་བ་དགུ་པ', 'ཟླ་བ་བཅུ་པ', 'ཟླ་བ་བཅུ་གཅིག་པ', 'ཟླ་བ་བཅུ་གཉིས་པ'], 'months_short' => ['ཟླ་༡', 'ཟླ་༢', 'ཟླ་༣', 'ཟླ་༤', 'ཟླ་༥', 'ཟླ་༦', 'ཟླ་༧', 'ཟླ་༨', 'ཟླ་༩', 'ཟླ་༡༠', 'ཟླ་༡༡', 'ཟླ་༡༢'], 'months_standalone' => ['ཟླ་བ་དང་པོ་', 'ཟླ་བ་གཉིས་པ་', 'ཟླ་བ་གསུམ་པ་', 'ཟླ་བ་བཞི་པ་', 'ཟླ་བ་ལྔ་པ་', 'ཟླ་བ་དྲུག་པ་', 'ཟླ་བ་བདུན་པ་', 'ཟླ་བ་བརྒྱད་པ་', 'ཟླ་བ་དགུ་པ་', 'ཟླ་བ་བཅུ་པ་', 'ཟླ་བ་བཅུ་གཅིག་པ་', 'ཟླ་བ་བཅུ་གཉིས་པ་'], 'weekend' => [0, 0], 'formats' => ['LT' => 'h:mm a', 'LTS' => 'h:mm:ss a', 'L' => 'YYYY-MM-DD', 'LL' => 'YYYY ལོའི་MMMཚེས་D', 'LLL' => 'སྤྱི་ལོ་YYYY MMMMའི་ཚེས་D h:mm a', 'LLLL' => 'YYYY MMMMའི་ཚེས་D, dddd h:mm a']]);
