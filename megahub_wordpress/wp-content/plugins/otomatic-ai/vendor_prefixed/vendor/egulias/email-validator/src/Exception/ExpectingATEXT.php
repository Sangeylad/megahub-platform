<?php

namespace OtomaticAi\Vendors\Egulias\EmailValidator\Exception;

class ExpectingATEXT extends InvalidEmail
{
    const CODE = 137;
    const REASON = "Expecting ATEXT";
}
