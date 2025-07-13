<?php

declare (strict_types=1);
namespace OtomaticAi\Vendors\Doctrine\Inflector\Rules\English;

use OtomaticAi\Vendors\Doctrine\Inflector\GenericLanguageInflectorFactory;
use OtomaticAi\Vendors\Doctrine\Inflector\Rules\Ruleset;
final class InflectorFactory extends GenericLanguageInflectorFactory
{
    protected function getSingularRuleset() : Ruleset
    {
        return Rules::getSingularRuleset();
    }
    protected function getPluralRuleset() : Ruleset
    {
        return Rules::getPluralRuleset();
    }
}
