<?php

/*
 * This file is part of the Symfony package.
 *
 * (c) Fabien Potencier <fabien@symfony.com>
 *
 * For the full copyright and license information, please view the LICENSE
 * file that was distributed with this source code.
 */
namespace OtomaticAi\Vendors\Symfony\Component\HttpFoundation\RateLimiter;

use OtomaticAi\Vendors\Symfony\Component\HttpFoundation\Request;
use OtomaticAi\Vendors\Symfony\Component\RateLimiter\LimiterInterface;
use OtomaticAi\Vendors\Symfony\Component\RateLimiter\Policy\NoLimiter;
use OtomaticAi\Vendors\Symfony\Component\RateLimiter\RateLimit;
/**
 * An implementation of RequestRateLimiterInterface that
 * fits most use-cases.
 *
 * @author Wouter de Jong <wouter@wouterj.nl>
 */
abstract class AbstractRequestRateLimiter implements RequestRateLimiterInterface
{
    public function consume(Request $request) : RateLimit
    {
        $limiters = $this->getLimiters($request);
        if (0 === \count($limiters)) {
            $limiters = [new NoLimiter()];
        }
        $minimalRateLimit = null;
        foreach ($limiters as $limiter) {
            $rateLimit = $limiter->consume(1);
            $minimalRateLimit = $minimalRateLimit ? self::getMinimalRateLimit($minimalRateLimit, $rateLimit) : $rateLimit;
        }
        return $minimalRateLimit;
    }
    public function reset(Request $request) : void
    {
        foreach ($this->getLimiters($request) as $limiter) {
            $limiter->reset();
        }
    }
    /**
     * @return LimiterInterface[] a set of limiters using keys extracted from the request
     */
    protected abstract function getLimiters(Request $request) : array;
    private static function getMinimalRateLimit(RateLimit $first, RateLimit $second) : RateLimit
    {
        if ($first->isAccepted() !== $second->isAccepted()) {
            return $first->isAccepted() ? $second : $first;
        }
        $firstRemainingTokens = $first->getRemainingTokens();
        $secondRemainingTokens = $second->getRemainingTokens();
        if ($firstRemainingTokens === $secondRemainingTokens) {
            return $first->getRetryAfter() < $second->getRetryAfter() ? $second : $first;
        }
        return $firstRemainingTokens > $secondRemainingTokens ? $second : $first;
    }
}
