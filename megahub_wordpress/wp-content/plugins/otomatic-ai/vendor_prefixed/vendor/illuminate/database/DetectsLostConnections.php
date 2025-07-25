<?php

namespace OtomaticAi\Vendors\Illuminate\Database;

use OtomaticAi\Vendors\Illuminate\Support\Str;
use Throwable;
trait DetectsLostConnections
{
    /**
     * Determine if the given exception was caused by a lost connection.
     *
     * @param  \Throwable  $e
     * @return bool
     */
    protected function causedByLostConnection(Throwable $e)
    {
        $message = $e->getMessage();
        return Str::contains($message, ['server has gone away', 'no connection to the server', 'Lost connection', 'is dead or not enabled', 'Error while sending', 'decryption failed or bad record mac', 'server closed the connection unexpectedly', 'SSL connection has been closed unexpectedly', 'Error writing data to the connection', 'Resource deadlock avoided', 'Transaction() on null', 'child connection forced to terminate due to client_idle_limit', 'query_wait_timeout', 'reset by peer', 'Physical connection is not usable', 'TCP Provider: Error code 0x68', 'ORA-03114', 'Packets out of order. Expected', 'Adaptive Server connection failed', 'Communication link failure', 'connection is no longer usable', 'Login timeout expired', 'SQLSTATE[HY000] [2002] Connection refused', 'running with the --read-only option so it cannot execute this statement', 'The connection is broken and recovery is not possible. The connection is marked by the client driver as unrecoverable. No attempt was made to restore the connection.', 'SQLSTATE[HY000] [2002] php_network_getaddresses: getaddrinfo failed: Try again', 'SQLSTATE[HY000] [2002] php_network_getaddresses: getaddrinfo failed: Name or service not known', 'SQLSTATE[HY000]: General error: 7 SSL SYSCALL error: EOF detected', 'SQLSTATE[HY000] [2002] Connection timed out', 'SSL: Connection timed out', 'SQLSTATE[HY000]: General error: 1105 The last transaction was aborted due to Seamless Scaling. Please retry.', 'Temporary failure in name resolution', 'SSL: Broken pipe', 'SQLSTATE[08S01]: Communication link failure', 'SQLSTATE[08006] [7] could not connect to server: Connection refused Is the server running on host', 'SQLSTATE[HY000]: General error: 7 SSL SYSCALL error: No route to host', 'The client was disconnected by the server because of inactivity. See wait_timeout and interactive_timeout for configuring this behavior.', 'SQLSTATE[08006] [7] could not translate host name', 'TCP Provider: Error code 0x274C']);
    }
}
