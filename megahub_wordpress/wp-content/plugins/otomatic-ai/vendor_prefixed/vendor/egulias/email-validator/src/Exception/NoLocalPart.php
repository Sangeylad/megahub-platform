<?php

namespace OtomaticAi\Vendors\Egulias\EmailValidator\Exception;

class NoLocalPart extends InvalidEmail
{
    const CODE = 130;
    const REASON = "No local part";
}
