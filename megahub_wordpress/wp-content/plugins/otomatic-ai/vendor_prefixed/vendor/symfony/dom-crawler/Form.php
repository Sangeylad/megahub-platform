<?php

/*
 * This file is part of the Symfony package.
 *
 * (c) Fabien Potencier <fabien@symfony.com>
 *
 * For the full copyright and license information, please view the LICENSE
 * file that was distributed with this source code.
 */
namespace OtomaticAi\Vendors\Symfony\Component\DomCrawler;

use OtomaticAi\Vendors\Symfony\Component\DomCrawler\Field\ChoiceFormField;
use OtomaticAi\Vendors\Symfony\Component\DomCrawler\Field\FormField;
/**
 * Form represents an HTML form.
 *
 * @author Fabien Potencier <fabien@symfony.com>
 */
class Form extends Link implements \ArrayAccess
{
    /**
     * @var \DOMElement
     */
    private $button;
    /**
     * @var FormFieldRegistry
     */
    private $fields;
    /**
     * @var string
     */
    private $baseHref;
    /**
     * @param \DOMElement $node       A \DOMElement instance
     * @param string|null $currentUri The URI of the page where the form is embedded
     * @param string|null $method     The method to use for the link (if null, it defaults to the method defined by the form)
     * @param string|null $baseHref   The URI of the <base> used for relative links, but not for empty action
     *
     * @throws \LogicException if the node is not a button inside a form tag
     */
    public function __construct(\DOMElement $node, ?string $currentUri = null, ?string $method = null, ?string $baseHref = null)
    {
        parent::__construct($node, $currentUri, $method);
        $this->baseHref = $baseHref;
        $this->initialize();
    }
    /**
     * Gets the form node associated with this form.
     *
     * @return \DOMElement
     */
    public function getFormNode()
    {
        return $this->node;
    }
    /**
     * Sets the value of the fields.
     *
     * @param array $values An array of field values
     *
     * @return $this
     */
    public function setValues(array $values)
    {
        foreach ($values as $name => $value) {
            $this->fields->set($name, $value);
        }
        return $this;
    }
    /**
     * Gets the field values.
     *
     * The returned array does not include file fields (@see getFiles).
     *
     * @return array
     */
    public function getValues()
    {
        $values = [];
        foreach ($this->fields->all() as $name => $field) {
            if ($field->isDisabled()) {
                continue;
            }
            if (!$field instanceof Field\FileFormField && $field->hasValue()) {
                $values[$name] = $field->getValue();
            }
        }
        return $values;
    }
    /**
     * Gets the file field values.
     *
     * @return array
     */
    public function getFiles()
    {
        if (!\in_array($this->getMethod(), ['POST', 'PUT', 'DELETE', 'PATCH'])) {
            return [];
        }
        $files = [];
        foreach ($this->fields->all() as $name => $field) {
            if ($field->isDisabled()) {
                continue;
            }
            if ($field instanceof Field\FileFormField) {
                $files[$name] = $field->getValue();
            }
        }
        return $files;
    }
    /**
     * Gets the field values as PHP.
     *
     * This method converts fields with the array notation
     * (like foo[bar] to arrays) like PHP does.
     *
     * @return array
     */
    public function getPhpValues()
    {
        $values = [];
        foreach ($this->getValues() as $name => $value) {
            $qs = \http_build_query([$name => $value], '', '&');
            if (!empty($qs)) {
                \parse_str($qs, $expandedValue);
                $varName = \substr($name, 0, \strlen(\key($expandedValue)));
                $values[] = [$varName => \current($expandedValue)];
            }
        }
        return \array_replace_recursive([], ...$values);
    }
    /**
     * Gets the file field values as PHP.
     *
     * This method converts fields with the array notation
     * (like foo[bar] to arrays) like PHP does.
     * The returned array is consistent with the array for field values
     * (@see getPhpValues), rather than uploaded files found in $_FILES.
     * For a compound file field foo[bar] it will create foo[bar][name],
     * instead of foo[name][bar] which would be found in $_FILES.
     *
     * @return array
     */
    public function getPhpFiles()
    {
        $values = [];
        foreach ($this->getFiles() as $name => $value) {
            $qs = \http_build_query([$name => $value], '', '&');
            if (!empty($qs)) {
                \parse_str($qs, $expandedValue);
                $varName = \substr($name, 0, \strlen(\key($expandedValue)));
                \array_walk_recursive($expandedValue, function (&$value, $key) {
                    if (\ctype_digit($value) && ('size' === $key || 'error' === $key)) {
                        $value = (int) $value;
                    }
                });
                \reset($expandedValue);
                $values[] = [$varName => \current($expandedValue)];
            }
        }
        return \array_replace_recursive([], ...$values);
    }
    /**
     * Gets the URI of the form.
     *
     * The returned URI is not the same as the form "action" attribute.
     * This method merges the value if the method is GET to mimics
     * browser behavior.
     *
     * @return string
     */
    public function getUri()
    {
        $uri = parent::getUri();
        if (!\in_array($this->getMethod(), ['POST', 'PUT', 'DELETE', 'PATCH'])) {
            $query = \parse_url($uri, \PHP_URL_QUERY);
            $currentParameters = [];
            if ($query) {
                \parse_str($query, $currentParameters);
            }
            $queryString = \http_build_query(\array_merge($currentParameters, $this->getValues()), '', '&');
            $pos = \strpos($uri, '?');
            $base = \false === $pos ? $uri : \substr($uri, 0, $pos);
            $uri = \rtrim($base . '?' . $queryString, '?');
        }
        return $uri;
    }
    protected function getRawUri()
    {
        // If the form was created from a button rather than the form node, check for HTML5 action overrides
        if ($this->button !== $this->node && $this->button->getAttribute('formaction')) {
            return $this->button->getAttribute('formaction');
        }
        return $this->node->getAttribute('action');
    }
    /**
     * Gets the form method.
     *
     * If no method is defined in the form, GET is returned.
     *
     * @return string
     */
    public function getMethod()
    {
        if (null !== $this->method) {
            return $this->method;
        }
        // If the form was created from a button rather than the form node, check for HTML5 method override
        if ($this->button !== $this->node && $this->button->getAttribute('formmethod')) {
            return \strtoupper($this->button->getAttribute('formmethod'));
        }
        return $this->node->getAttribute('method') ? \strtoupper($this->node->getAttribute('method')) : 'GET';
    }
    /**
     * Gets the form name.
     *
     * If no name is defined on the form, an empty string is returned.
     */
    public function getName() : string
    {
        return $this->node->getAttribute('name');
    }
    /**
     * Returns true if the named field exists.
     *
     * @return bool
     */
    public function has(string $name)
    {
        return $this->fields->has($name);
    }
    /**
     * Removes a field from the form.
     */
    public function remove(string $name)
    {
        $this->fields->remove($name);
    }
    /**
     * Gets a named field.
     *
     * @return FormField|FormField[]|FormField[][]
     *
     * @throws \InvalidArgumentException When field is not present in this form
     */
    public function get(string $name)
    {
        return $this->fields->get($name);
    }
    /**
     * Sets a named field.
     */
    public function set(FormField $field)
    {
        $this->fields->add($field);
    }
    /**
     * Gets all fields.
     *
     * @return FormField[]
     */
    public function all()
    {
        return $this->fields->all();
    }
    /**
     * Returns true if the named field exists.
     *
     * @param string $name The field name
     *
     * @return bool
     */
    #[\ReturnTypeWillChange]
    public function offsetExists($name)
    {
        return $this->has($name);
    }
    /**
     * Gets the value of a field.
     *
     * @param string $name The field name
     *
     * @return FormField|FormField[]|FormField[][]
     *
     * @throws \InvalidArgumentException if the field does not exist
     */
    #[\ReturnTypeWillChange]
    public function offsetGet($name)
    {
        return $this->fields->get($name);
    }
    /**
     * Sets the value of a field.
     *
     * @param string       $name  The field name
     * @param string|array $value The value of the field
     *
     * @return void
     *
     * @throws \InvalidArgumentException if the field does not exist
     */
    #[\ReturnTypeWillChange]
    public function offsetSet($name, $value)
    {
        $this->fields->set($name, $value);
    }
    /**
     * Removes a field from the form.
     *
     * @param string $name The field name
     *
     * @return void
     */
    #[\ReturnTypeWillChange]
    public function offsetUnset($name)
    {
        $this->fields->remove($name);
    }
    /**
     * Disables validation.
     *
     * @return $this
     */
    public function disableValidation()
    {
        foreach ($this->fields->all() as $field) {
            if ($field instanceof Field\ChoiceFormField) {
                $field->disableValidation();
            }
        }
        return $this;
    }
    /**
     * Sets the node for the form.
     *
     * Expects a 'submit' button \DOMElement and finds the corresponding form element, or the form element itself.
     *
     * @throws \LogicException If given node is not a button or input or does not have a form ancestor
     */
    protected function setNode(\DOMElement $node)
    {
        $this->button = $node;
        if ('button' === $node->nodeName || 'input' === $node->nodeName && \in_array(\strtolower($node->getAttribute('type')), ['submit', 'button', 'image'])) {
            if ($node->hasAttribute('form')) {
                // if the node has the HTML5-compliant 'form' attribute, use it
                $formId = $node->getAttribute('form');
                $form = $node->ownerDocument->getElementById($formId);
                if (null === $form) {
                    throw new \LogicException(\sprintf('The selected node has an invalid form attribute (%s).', $formId));
                }
                $this->node = $form;
                return;
            }
            // we loop until we find a form ancestor
            do {
                if (null === ($node = $node->parentNode)) {
                    throw new \LogicException('The selected node does not have a form ancestor.');
                }
            } while ('form' !== $node->nodeName);
        } elseif ('form' !== $node->nodeName) {
            throw new \LogicException(\sprintf('Unable to submit on a "%s" tag.', $node->nodeName));
        }
        $this->node = $node;
    }
    /**
     * Adds form elements related to this form.
     *
     * Creates an internal copy of the submitted 'button' element and
     * the form node or the entire document depending on whether we need
     * to find non-descendant elements through HTML5 'form' attribute.
     */
    private function initialize()
    {
        $this->fields = new FormFieldRegistry();
        $xpath = new \DOMXPath($this->node->ownerDocument);
        // add submitted button if it has a valid name
        if ('form' !== $this->button->nodeName && $this->button->hasAttribute('name') && $this->button->getAttribute('name')) {
            if ('input' == $this->button->nodeName && 'image' == \strtolower($this->button->getAttribute('type'))) {
                $name = $this->button->getAttribute('name');
                $this->button->setAttribute('value', '0');
                // temporarily change the name of the input node for the x coordinate
                $this->button->setAttribute('name', $name . '.x');
                $this->set(new Field\InputFormField($this->button));
                // temporarily change the name of the input node for the y coordinate
                $this->button->setAttribute('name', $name . '.y');
                $this->set(new Field\InputFormField($this->button));
                // restore the original name of the input node
                $this->button->setAttribute('name', $name);
            } else {
                $this->set(new Field\InputFormField($this->button));
            }
        }
        // find form elements corresponding to the current form
        if ($this->node->hasAttribute('id')) {
            // corresponding elements are either descendants or have a matching HTML5 form attribute
            $formId = Crawler::xpathLiteral($this->node->getAttribute('id'));
            $fieldNodes = $xpath->query(\sprintf('( descendant::input[@form=%s] | descendant::button[@form=%1$s] | descendant::textarea[@form=%1$s] | descendant::select[@form=%1$s] | //form[@id=%1$s]//input[not(@form)] | //form[@id=%1$s]//button[not(@form)] | //form[@id=%1$s]//textarea[not(@form)] | //form[@id=%1$s]//select[not(@form)] )[not(ancestor::template)]', $formId));
            foreach ($fieldNodes as $node) {
                $this->addField($node);
            }
        } else {
            // do the xpath query with $this->node as the context node, to only find descendant elements
            // however, descendant elements with form attribute are not part of this form
            $fieldNodes = $xpath->query('( descendant::input[not(@form)] | descendant::button[not(@form)] | descendant::textarea[not(@form)] | descendant::select[not(@form)] )[not(ancestor::template)]', $this->node);
            foreach ($fieldNodes as $node) {
                $this->addField($node);
            }
        }
        if ($this->baseHref && '' !== $this->node->getAttribute('action')) {
            $this->currentUri = $this->baseHref;
        }
    }
    private function addField(\DOMElement $node)
    {
        if (!$node->hasAttribute('name') || !$node->getAttribute('name')) {
            return;
        }
        $nodeName = $node->nodeName;
        if ('select' == $nodeName || 'input' == $nodeName && 'checkbox' == \strtolower($node->getAttribute('type'))) {
            $this->set(new Field\ChoiceFormField($node));
        } elseif ('input' == $nodeName && 'radio' == \strtolower($node->getAttribute('type'))) {
            // there may be other fields with the same name that are no choice
            // fields already registered (see https://github.com/symfony/symfony/issues/11689)
            if ($this->has($node->getAttribute('name')) && $this->get($node->getAttribute('name')) instanceof ChoiceFormField) {
                $this->get($node->getAttribute('name'))->addChoice($node);
            } else {
                $this->set(new Field\ChoiceFormField($node));
            }
        } elseif ('input' == $nodeName && 'file' == \strtolower($node->getAttribute('type'))) {
            $this->set(new Field\FileFormField($node));
        } elseif ('input' == $nodeName && !\in_array(\strtolower($node->getAttribute('type')), ['submit', 'button', 'image'])) {
            $this->set(new Field\InputFormField($node));
        } elseif ('textarea' == $nodeName) {
            $this->set(new Field\TextareaFormField($node));
        }
    }
}
