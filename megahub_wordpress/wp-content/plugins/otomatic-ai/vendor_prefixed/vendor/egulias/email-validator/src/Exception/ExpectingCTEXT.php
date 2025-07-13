<?php

namespace OtomaticAi\Vendors\Egulias\EmailValidator\Exception;

class ExpectingCTEXT extends InvalidEmail
{
    const CODE = 139;
    const REASON = "Expecting CTEXT";
}
