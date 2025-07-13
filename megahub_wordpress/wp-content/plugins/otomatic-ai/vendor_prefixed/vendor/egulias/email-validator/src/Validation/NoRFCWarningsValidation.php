<?php

namespace OtomaticAi\Vendors\Egulias\EmailValidator\Validation;

use OtomaticAi\Vendors\Egulias\EmailValidator\EmailLexer;
use OtomaticAi\Vendors\Egulias\EmailValidator\Exception\InvalidEmail;
use OtomaticAi\Vendors\Egulias\EmailValidator\Validation\Error\RFCWarnings;
class NoRFCWarningsValidation extends RFCValidation
{
    /**
     * @var InvalidEmail|null
     */
    private $error;
    /**
     * {@inheritdoc}
     */
    public function isValid($email, EmailLexer $emailLexer)
    {
        if (!parent::isValid($email, $emailLexer)) {
            return \false;
        }
        if (empty($this->getWarnings())) {
            return \true;
        }
        $this->error = new RFCWarnings();
        return \false;
    }
    /**
     * {@inheritdoc}
     */
    public function getError()
    {
        return $this->error ?: parent::getError();
    }
}
