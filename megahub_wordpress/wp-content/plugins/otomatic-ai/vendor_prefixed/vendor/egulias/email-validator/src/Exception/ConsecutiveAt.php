<?php

namespace OtomaticAi\Vendors\Egulias\EmailValidator\Exception;

class ConsecutiveAt extends InvalidEmail
{
    const CODE = 128;
    const REASON = "Consecutive AT";
}
