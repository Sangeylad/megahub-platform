<?php

declare (strict_types=1);
namespace OtomaticAi\Vendors\Doctrine\Inflector\Rules\Turkish;

use OtomaticAi\Vendors\Doctrine\Inflector\Rules\Patterns;
use OtomaticAi\Vendors\Doctrine\Inflector\Rules\Ruleset;
use OtomaticAi\Vendors\Doctrine\Inflector\Rules\Substitutions;
use OtomaticAi\Vendors\Doctrine\Inflector\Rules\Transformations;
final class Rules
{
    public static function getSingularRuleset() : Ruleset
    {
        return new Ruleset(new Transformations(...Inflectible::getSingular()), new Patterns(...Uninflected::getSingular()), (new Substitutions(...Inflectible::getIrregular()))->getFlippedSubstitutions());
    }
    public static function getPluralRuleset() : Ruleset
    {
        return new Ruleset(new Transformations(...Inflectible::getPlural()), new Patterns(...Uninflected::getPlural()), new Substitutions(...Inflectible::getIrregular()));
    }
}
