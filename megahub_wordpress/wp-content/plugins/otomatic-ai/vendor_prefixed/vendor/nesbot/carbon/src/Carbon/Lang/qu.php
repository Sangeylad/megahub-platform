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
return \array_replace_recursive(require __DIR__ . '/es_UY.php', ['formats' => ['LT' => 'HH:mm', 'LTS' => 'HH:mm:ss', 'L' => 'DD/MM/YYYY', 'LL' => 'D MMM YYYY', 'LLL' => 'D MMMM YYYY HH:mm', 'LLLL' => 'dddd, D MMMM, YYYY HH:mm'], 'first_day_of_week' => 0]);
