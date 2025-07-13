<?php

namespace OtomaticAi\Vendors\Egulias\EmailValidator\Validation\Error;

use OtomaticAi\Vendors\Egulias\EmailValidator\Exception\InvalidEmail;
class RFCWarnings extends InvalidEmail
{
    const CODE = 997;
    const REASON = 'Warnings were found.';
}
