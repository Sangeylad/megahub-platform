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
return \array_replace_recursive(require __DIR__ . '/fr.php', ['first_day_of_week' => 6, 'weekend' => [5, 6]]);
