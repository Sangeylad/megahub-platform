<?php

/*
 * This file is part of the Symfony package.
 *
 * (c) Fabien Potencier <fabien@symfony.com>
 *
 * For the full copyright and license information, please view the LICENSE
 * file that was distributed with this source code.
 */
namespace OtomaticAi\Vendors\Symfony\Component\DomCrawler\Field;

/**
 * FormField is the abstract class for all form fields.
 *
 * @author Fabien Potencier <fabien@symfony.com>
 */
abstract class FormField
{
    /**
     * @var \DOMElement
     */
    protected $node;
    /**
     * @var string
     */
    protected $name;
    /**
     * @var string
     */
    protected $value;
    /**
     * @var \DOMDocument
     */
    protected $document;
    /**
     * @var \DOMXPath
     */
    protected $xpath;
    /**
     * @var bool
     */
    protected $disabled;
    /**
     * @param \DOMElement $node The node associated with this field
     */
    public function __construct(\DOMElement $node)
    {
        $this->node = $node;
        $this->name = $node->getAttribute('name');
        $this->xpath = new \DOMXPath($node->ownerDocument);
        $this->initialize();
    }
    /**
     * Returns the label tag associated to the field or null if none.
     *
     * @return \DOMElement|null
     */
    public function getLabel()
    {
        $xpath = new \DOMXPath($this->node->ownerDocument);
        if ($this->node->hasAttribute('id')) {
            $labels = $xpath->query(\sprintf('descendant::label[@for="%s"]', $this->node->getAttribute('id')));
            if ($labels->length > 0) {
                return $labels->item(0);
            }
        }
        $labels = $xpath->query('ancestor::label[1]', $this->node);
        return $labels->length > 0 ? $labels->item(0) : null;
    }
    /**
     * Returns the name of the field.
     *
     * @return string
     */
    public function getName()
    {
        return $this->name;
    }
    /**
     * Gets the value of the field.
     *
     * @return string|array|null
     */
    public function getValue()
    {
        return $this->value;
    }
    /**
     * Sets the value of the field.
     */
    public function setValue(?string $value)
    {
        $this->value = $value ?? '';
    }
    /**
     * Returns true if the field should be included in the submitted values.
     *
     * @return bool
     */
    public function hasValue()
    {
        return \true;
    }
    /**
     * Check if the current field is disabled.
     *
     * @return bool
     */
    public function isDisabled()
    {
        return $this->node->hasAttribute('disabled');
    }
    /**
     * Initializes the form field.
     */
    protected abstract function initialize();
}
