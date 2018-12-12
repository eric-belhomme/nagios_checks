
F5 Load-Balancer running BIG-IP OS Nagios plugin
================================================

-= modes =-
-----------
* help - This help     
* health - Reports global system health
* http - Reports global HTTP requests
* enumvs - enumerates 'VirtualServers' configured on the appliance
* vsstats - get statistics for a given VirtualServer
* nodestats - get statistics for remote Nodes (real servers)
* mem_tmm - get TMM meory usage stats (global)
* sessions - get client and server sessions stats (global)

    
-= health mode =-
-----------------

Report global system health: PSU health, chassis temperature, and fans health

Warning and critical triggers (respectively `-w` and `-c` command-line
parameters) are passed as 3 comma-separated values for respectively
PSU, temp, and fans:

    -w 1,35,3 will set warning values as below:
        -> 1 failed PSU
        -> 35°C for temperature
        -> 3 failed fans

Additionnaly, it is possible to alter default behaviour with the following
flags, passed with `--arg1` command-lien parameter:

    ignoremissingpsu : don't trigger any warning or error is a PSU is
                       reported as missing
    warnmissingpsu   : trigger warning (instead of critical) error is a PSU
                       is reported as missing
    ignoremissingfan : don't trigger any warning or error is a fan is
                       reported as missing
    warnmissingfan   : trigger warning (instead of critical) error is a fan
                       is reported as missing

    --arg1=ignoremissingpsu,warnmissingfan

    
-= http mode =-
---------------

Reports global HTTP requests

Warning and critical triggers (respectively `-w` and `-c` command-line
parameters) 

If ommited, defaults to :
    -w 200000
    -c 250000
    
Additionally, if `--perfdata` command-line argument is triggered, Nagios
perfdata are computed and appended to the output.

No additional arguments are required

    
-= enumvs mode =-
-----------------

Enumerates **VirtualServers** configured on the appliance

This mode is mainly used to ease Nagios configuration to define how to use
**vsstats** mode

This mode does not require any additional parameters.

    
-= vsstats mode =-
------------------

Get statistics for a given VirtualServer, the target VS is passed as `--arg1`
parameter.

The check returns the following informations:
* VirtualServer name and status,
* connections details (current, max, total)
* bandwidth usage (incoming bytes, outgoing bytes)

Warning and critical triggers (respectively `-w` and `-c` command-line
parameters) are passed as 3 comma-separated values for respectively
active connections, max connections, total connections

If ommited, defaults to :

    -w 200000,200000,200000
    -c 250000,250000,250000

Additionally, if `--perfdata` command-line argument is triggered, Nagios
perfdata are computed and appended to the output.

    
-= nodestats mode =-
--------------------

Get statistics for Nodes, the 'real' servers behind the Load Balancer.

The check returns for each node found the following informations:
* Node name and status,
* connections details (current, max, total)
* bandwidth usage (incoming bytes, outgoing bytes)

Warning and critical triggers (respectively `-w` and `-c` command-line
parameters) are passed as 3 comma-separated values for respectively
active connections, max connections, total connections

If ommited, defaults to :

    -w 200000,200000,200000
    -c 250000,250000,250000

Additionally, if `--perfdata` command-line argument is triggered, Nagios
perfdata are computed and appended to the output.

    
-= mem_tmm mode =-
--------------------

Reports consumed memory by TMM processes

Warning and critical triggers (respectively `-w` and `-c` command-line
parameters) are exprimed as percentage values

If ommited, defaults to :
    -w 85
    -c 95
    
Additionally, if `--perfdata` command-line argument is triggered, Nagios
perfdata are computed and appended to the output.

No additional arguments are required

    
-= sessions mode =-
--------------------

Reports clients & servers sessions

Warning and critical triggers (respectively `-w` and `-c` command-line
parameters) are comma separated and respectvely refers to client and
server values, and are exprimed as percentage values

If ommited, defaults to :
    -w 90,90
    -c 95,95
    
Additionally, if `--perfdata` command-line argument is triggered, Nagios
perfdata are computed and appended to the output.

No additional arguments are required

    
---
Copyright Eric Belhomme <rico-github@ricozome.net> under MIT license
