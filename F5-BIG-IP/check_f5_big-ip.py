#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: expandtab sw=4 ts=4:
"""
F5 Load-Balancer running BIG-IP OS Nagios plugin
2018-11-10 Eric Belhomme <rico-github@ricozome.net> - Initial work
2018-12-12 Eric Belhomme <rico-github@ricozome.net> - added mem_tmm and sessions modes, fixed perfdata
Published under MIT license
"""
import argparse, netsnmp

__author__ = 'Eric Belhomme'
__contact__ = 'rico-github@ricozome.net'
__license__ = 'MIT'


retText = [
    'OK',
    'WARNING',
    'CRITICAL',
    'UNKNOWN',
]


def print_longHelp():
    print("""
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

    """)
    print('-= health mode =-\n-----------------\n' + get_health_status.__doc__)
    print('-= http mode =-\n---------------\n' + get_http_stats.__doc__)
    print('-= enumvs mode =-\n-----------------\n' + enum_virtualservers.__doc__)
    print('-= vsstats mode =-\n------------------\n' + get_vs_stats.__doc__)
    print('-= nodestats mode =-\n--------------------\n' + get_node_stats.__doc__)
    print('-= mem_tmm mode =-\n--------------------\n' + get_mem_tmm.__doc__)
    print('-= sessions mode =-\n--------------------\n' + get_sessions.__doc__)
   
    print("---\nCopyright {author} <{authmail}> under {license} license".format(
        author = __author__, authmail = __contact__, license = __license__))
    exit(0)


def get_health_status(perfdata):
    '''
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

    '''
    # Sessions concurrentes (coté clients)	Get	.1.3.6.1.4.1.3375.2.1.1.2.1.8.x
    # Sessions concurrentes (coté serveurs)	Get	.1.3.6.1.4.1.3375.2.1.1.2.1.15.x
    # Nombre Max de Sessions Simultanées (coté client)	Get	.1.3.6.1.4.1.3375.2.1.1.2.1.6.x
    # Nombre Max de Sessions Simultanées (coté serveurs)	Get	.1.3.6.1.4.1.3375.2.1.1.2.1.13.x
    # Sessions Totales (coté clients)	Get	.1.3.6.1.4.1.3375.2.1.1.2.1.7.x
    # Sessions Totales (coté serveurs)	Get	.1.3.6.1.4.1.3375.2.1.1.2.1.14.x
    warn = ('1','40','1')
    if isinstance(args.warning,str) and args.warning is not None:
        warn = tuple(args.warning.split(','))
    crit = ('1','50','2')
    if isinstance(args.critical,str) and args.critical is not None:
        crit = tuple(args.critical.split(','))
    flags = ()
    if isinstance(args.arg1,str) and args.arg1 is not None:
        flags = tuple(args.arg1.lower().split(','))
    oid_status_psu = '.1.3.6.1.4.1.3375.2.1.3.2.2.2.1.2'
    psu = { 'bad': 0, 'good': 0, 'missing': 0}
    oid_status_temperature = '.1.3.6.1.4.1.3375.2.1.3.2.3.2.1.2'
    temp = { 'ok': 0, 'warn': 0, 'crit': 0 }
    oid_status_fans = '.1.3.6.1.4.1.3375.2.1.3.2.1.2.1.2'
    fan = { 'bad': 0, 'good': 0, 'missing': 0}
    retcode = 0

    # PSU info
    vals = snmpSession.walk(netsnmp.VarList(netsnmp.Varbind(oid_status_psu)))
    if vals:
        for item in vals:
            if item == '0':
                psu['bad'] += 1
            elif item == '1':
                psu['good'] += 1
            else:
                psu['missing'] += 1

        if psu['missing'] > 0:
            if 'ignoremissingpsu' in args.arg1:
                pass
            elif 'warnmissingpsu' in args.arg1:
                retcode = 1
                message.append("{} PSU missing".format(psu['missing']))
            else:
                retcode = 2
                message.append("{} PSU missing".format(psu['missing']))
        
        if psu['bad'] > int(warn[0]):
            retcode = 1
            message.append("{} PSU failed".format(psu['bad']))
        elif psu['bad'] > int(crit[0]):
            retcode = 2
            message.append("{} PSU failed".format(psu['bad']))
        else:
            message.append("{} PSU OK".format(psu['good']))

    else:
        retcode = 3
        message.append('Unable to retrieve PSU information !')

    # Chassis temperature info
    message.append(' - ')
    vals = snmpSession.walk(netsnmp.VarList(netsnmp.Varbind(oid_status_temperature)))
    if vals:
        ret = 0
        txt = ''
        counter = 1
        for item in vals:
            if int(item) > int(warn[1]):
                ret = 1
            if int(item) > int(crit[1]):
                ret = 2
            if len(txt):
                txt += ', '
            txt += "sensor {}: {}°C".format(str(counter), item)
        if retcode == 0 or retcode == 3:
            retcode = ret
        message.append("temperatures {status} ({text})".format(status=retText[ret], text=txt))
    else:
        if retcode == 0:
            retcode = 3
        message.append('Failed to retrieve chassis temperature sensor !')

    # Chassis fans info
    message.append(' - ')
    vals = snmpSession.walk(netsnmp.VarList(netsnmp.Varbind(oid_status_fans)))
    if vals:
        for item in vals:
            if item == '0':
                fan['bad'] += 1
            elif item == '1':
                fan['good'] += 1
            else:
                fan['missing'] += 1
        ret = 0
        if fan['missing'] > 0:
            if 'ignoremissingfan' in args.arg1:
                pass
            elif 'warnmissingfan' in args.arg1:
                ret = 1
                message.append("{} fan missing".format(fan['missing']))
            else:
                ret = 2
                message.append("{} fan missing".format(fan['missing']))
        
        if fan['bad'] > int(warn[2]):
            if ret < 1:
                ret = 1
            message.append("{} fan failed".format(fan['bad']))
        elif fan['bad'] > int(crit[2]):
            if ret < 2:
                ret = 2
            message.append("{} fan failed".format(fan['bad']))
        else:
            message.append("{} fan OK".format(fan['good']))
        if retcode == 0 or retcode == 3:
            retcode = ret
    else:
        if retcode == 0:
            retcode = 3
        message.append('Unable to retrieve fans status !')

    message.append('\n')
    return retcode


def _enum_virtualservers():
    return snmpSession.walk(netsnmp.VarList(
        netsnmp.Varbind('.1.3.6.1.4.1.3375.2.2.10.13.2.1.1'),
        netsnmp.Varbind('.1.3.6.1.4.1.3375.2.2.10.2.3.1.1')))

def enum_virtualservers():
    '''
Enumerates **VirtualServers** configured on the appliance

This mode is mainly used to ease Nagios configuration to define how to use
**vsstats** mode

This mode does not require any additional parameters.

    '''
    vals = _enum_virtualservers()
    if vals:
        message.append('F5 VirtualServers list: \n')
        for item in set(vals):
            message.append("  {}\n".format(item))
    else:
        message.append('Unable to retrieve VirtualServer informations')
        return 3
    return 0


def _check_avail(status, strType, strObject):
    ltmVsStatusAvailState = [
        ('none',   'error'),                        # 0
        ('green',  'available in some capacity'),   # 1
        ('yellow', 'not currently available'),      # 2
        ('red',    'not available'),                # 3
        ('blue',   'availability is unknown'),      # 4
        ('gray',   'unlicensed'),                   # 5
    ]
    retcode = 0
    if status < 0 or status > 5:
        retcode = 3
        message.append("Failed to retrieve {} status information".format(strObject))
    else:
        message.append("{} {} status {} ({})\n".format(strType, strObject, ltmVsStatusAvailState[status][0], ltmVsStatusAvailState[status][1]))
        if status == 4:
            retcode = 3
        elif status == 1 or status == 5:
            retcode = 1
        elif status == 0 or status == 3:
            retcode = 2
    return retcode


def _get_stats(cnx_actives, cnx_max, cnx_total, bytes_in, bytes_out, warn, crit):
    retcode, ret = 0, 0
    # check actives connections
    cnx_actives = int(cnx_actives)
    if cnx_actives > warn[0]:
        ret = 1
    if cnx_actives > crit[0]:
        ret = 2
    message.append(" - {} actives connections".format(str(cnx_actives)))
    if ret > retcode:
        retcode = ret
    if args.perfdata:
        perfmsg.append("'cnx_actv'={};{};{}".format(str(cnx_actives), str(warn[0]), str(crit[0])))
    # check total connections
    ret = 0
    cnx_total = int(cnx_total)
    if cnx_total > warn[2]:
        ret = 1
    if cnx_total > crit[2]:
        ret = 2
    message.append(" - {} max connections".format(str(cnx_total)))
    if ret > retcode:
        retcode = ret
    if args.perfdata:
        perfmsg.append("'cnx_total'={};{};{}".format(str(cnx_total), str(warn[2]), str(crit[2])))
    message.append( " - bytes in: {}, bytes out: {}\n".format(bytes_in, bytes_out))
    if args.perfdata:
        perfmsg.append("'bytes_in'=".format(bytes_in))
        perfmsg.append("'bytes_out'=".format(bytes_out))
    return retcode
    

def get_vs_stats(vsfilter, perfdata=False):
    '''
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

    '''
    regex = None
    if vsfilter is not None:
        regex = re.compile(vsfilter)

    warn = ('200000','200000','200000')
    if isinstance(args.warning,str) and args.warning is not None:
        warn = tuple(args.warning.split(','))
    crit = ('250000','250000','250000')
    if isinstance(args.critical,str) and args.critical is not None:
        crit = tuple(args.critical.split(','))
    retcode = 0
    
    vals = snmpSession.walk( netsnmp.VarList(
        netsnmp.Varbind('.1.3.6.1.4.1.3375.2.2.10.13.2.1.1'),   # Virtual Server name
        netsnmp.Varbind('.1.3.6.1.4.1.3375.2.2.10.13.2.1.2'),   # status
        netsnmp.Varbind('.1.3.6.1.4.1.3375.2.2.10.2.3.1.1'),    # Virtual Server name (from another OID)
        netsnmp.Varbind('.1.3.6.1.4.1.3375.2.2.10.2.3.1.12'),   # actives cnx (gauge)
        netsnmp.Varbind('.1.3.6.1.4.1.3375.2.2.10.2.3.1.10'),   # max cnx (gauge)
        netsnmp.Varbind('.1.3.6.1.4.1.3375.2.2.10.2.3.1.11'),   # total cnx (gauge)
        netsnmp.Varbind('.1.3.6.1.4.1.3375.2.2.10.2.3.1.7'),    # bytes in (counter64)
        netsnmp.Varbind('.1.3.6.1.4.1.3375.2.2.10.2.3.1.9')))   # bytes out (counter64)
    if vals:
        for name1, status, name2, cnx_actives, cnx_max, cnx_total, bytes_in, bytes_out in tuple( vals[i:i+8] for i in range(0, len(vals), 8)):
            if regex is not None:
                if re.match(regex, name1) != None:
                    continue
            # VS name match
            if name1 != name2:
                message.append("VirtualServer OID names mismatch: {} != {}".format(name1, name2))
                retcode = 3
            # check status
            retcode = _check_avail(int(status), 'VirtualServer', name1)
            ret = _get_stats(cnx_actives, cnx_max, cnx_total, bytes_in, bytes_out, warn, crit)
            if ret < 3 and ret > retcode:
                retcode = ret
    else:
        retcode = 3
        message.append('Failed to retrieve VirtualServer data')
    
    return retcode


def get_node_stats(perfdata=False):
    """
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

    """
    warn = ('200000','200000','200000')
    if isinstance(args.warning,str) and args.warning is not None:
        warn = tuple(args.warning.split(','))
    crit = ('250000','250000','250000')
    if isinstance(args.critical,str) and args.critical is not None:
        crit = tuple(args.critical.split(','))

    vals = snmpSession.walk( netsnmp.VarList(
        netsnmp.Varbind('.1.3.6.1.4.1.3375.2.2.5.6.2.1.9'),     # Nom des Nodes (Serveurs Réels)
        netsnmp.Varbind('.1.3.6.1.4.1.3375.2.2.5.6.2.1.5'),     # node availability
        netsnmp.Varbind('.1.3.6.1.4.1.3375.2.2.4.2.3.1.9'),     # Connexions actives par Node (Serveur Réel)
        netsnmp.Varbind('.1.3.6.1.4.1.3375.2.2.4.2.3.1.7'),     # Connexions maximales par Node (Serveur Réel)
        netsnmp.Varbind('.1.3.6.1.4.1.3375.2.2.4.2.3.1.8'),     # Connexions totale par Node (Serveur Réel)
        netsnmp.Varbind('.1.3.6.1.4.1.3375.2.2.4.2.3.1.4'),     # Traffic entrant en octets par Node (Serveurs Réels)
        netsnmp.Varbind('.1.3.6.1.4.1.3375.2.2.4.2.3.1.6'),     # Traffic sortant en octets par Node  (Serveurs Réels)
    ))
    if vals:
        for name, status, cnx_actives, cnx_max, cnx_total, bytes_in, bytes_out in tuple( vals[i:i+7] for i in range(0, len(vals), 7)):
            # check status
            retcode = _check_avail(int(status), 'Node', name)
            ret = _get_stats(cnx_actives, cnx_max, cnx_total, bytes_in, bytes_out, warn, crit)
            if ret < 3 and ret > retcode:
                retcode = ret
    else:
        retcode = 3
        message.append('Failed to retrieve VirtualServer data')
    
    return retcode


def get_http_stats(perfdata):
    '''
Reports global HTTP requests

Warning and critical triggers (respectively `-w` and `-c` command-line
parameters) 

If ommited, defaults to :
    -w 200000
    -c 250000
    
Additionally, if `--perfdata` command-line argument is triggered, Nagios
perfdata are computed and appended to the output.

No additional arguments are required

    '''
    retcode = 0
    warn = '200000'
    if isinstance(args.warning,str) and args.warning is not None:
        warn = int(args.warning)
    crit = '250000'
    if isinstance(args.critical,str) and args.critical is not None:
        crit = int(args.critical)

    vals = map( int, snmpSession.get(netsnmp.VarList(netsnmp.Varbind('.1.3.6.1.4.1.3375.2.1.1.2.1.56.0'))))
    if len(vals):
        val = vals[0]
        if val > warn:
            retcode = 1
        if val > crit:
            retcode = 2
        message.append("global HTTP requests: {}".format(val))
        if perfdata:
            perfmsg.append("'http_req'={};{};{}".format(str(val), str(warn), str(crit)))
    else:
        retcode = 3
        message.append('Failed to retrieve HTTP session data')

    return retcode


def get_mem_tmm(perfdata):
    '''
Reports consumed memory by TMM processes

Warning and critical triggers (respectively `-w` and `-c` command-line
parameters) are exprimed as percentage values

If ommited, defaults to :
    -w 85
    -c 95
    
Additionally, if `--perfdata` command-line argument is triggered, Nagios
perfdata are computed and appended to the output.

No additional arguments are required

    '''
    retcode = 3
    memtot, memused = (0,0)

    warn = '85'
    if isinstance(args.warning,str) and args.warning is not None:
        warn = int(args.warning)
    crit = '95'
    if isinstance(args.critical,str) and args.critical is not None:
        crit = int(args.critical)

    vals = map( int, snmpSession.get(netsnmp.VarList(netsnmp.Varbind('.1.3.6.1.4.1.3375.2.1.1.2.1.44.0'))))
    if len(vals):
        memtot = vals[0]
    vals = map( int, snmpSession.get(netsnmp.VarList(netsnmp.Varbind('.1.3.6.1.4.1.3375.2.1.1.2.1.45.0'))))
    if len(vals):
        memused = vals[0]

    if memtot and memused:
        retcode = 0
        warn = (int(warn) * memtot) / 100
        crit = (int(crit) * memtot) / 100

        if memused > warn:
            retcode = 1
        if memused > crit:
            retcode = 2
        message.append("TMM memory: {} MB / {} MB ({}%)".format(str(memused/(1024**2)), str(memtot/(1024**2)), str((memused * 100)/memtot)))
        if perfdata:
            perfmsg.append("'mem_tmm'={};{};{};0;{}".format(str(memused), str(warn), str(crit), str(memtot)))
    else:
        retcode = 3
        message.append('Failed to retrieve TMM memory data')

    return retcode


def get_sessions(perfdata):
    '''
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

    '''
    retcode = 3

    warn = ('90', '90')
    if isinstance(args.warning,str) and args.warning is not None:
        warn = tuple(args.warning.split(','))
    crit = ('95', '95')
    if isinstance(args.critical,str) and args.critical is not None:
        crit = tuple(args.critical.split(','))

    (cliCurSess, serCurSess, cliMaxSess, serMaxSess, cliTotSess, serTotSess) = map(int,
        snmpSession.get(netsnmp.VarList(
        netsnmp.Varbind('.1.3.6.1.4.1.3375.2.1.1.2.1.8.0'),
        netsnmp.Varbind('.1.3.6.1.4.1.3375.2.1.1.2.1.15.0'),
        netsnmp.Varbind('.1.3.6.1.4.1.3375.2.1.1.2.1.6.0'),
        netsnmp.Varbind('.1.3.6.1.4.1.3375.2.1.1.2.1.13.0'),
        netsnmp.Varbind('.1.3.6.1.4.1.3375.2.1.1.2.1.7.0'),
        netsnmp.Varbind('.1.3.6.1.4.1.3375.2.1.1.2.1.14.0')
        )))

    if cliTotSess and serTotSess:
        retcode = 0

        warn = ( (int(warn[0]) * cliTotSess) / 100, (int(warn[1]) * serTotSess) / 100 )
        crit = ( (int(crit[0]) * cliTotSess) / 100, (int(crit[1]) * serTotSess) / 100 )
        if cliCurSess + serCurSess > max(warn):
            retcode = 1
        if cliCurSess + serCurSess > max(crit):
            retcode = 2

        message.append( "client sessions: {} (max: {}) / {}".format(str(cliCurSess), str(cliMaxSess), str(cliTotSess)))
        message.append( " - ")
        message.append( "server sessions: {} (max: {}) / {}".format(str(serCurSess), str(serMaxSess), str(serTotSess)))

    if perfdata:
        perfmsg.append("'cli_sess'={};{};{};0;{}".format(str(cliCurSess), str(warn[0]), str(crit[0]), str(cliTotSess)))
        perfmsg.append("'srv_sess'={};{};{};0;{}".format(str(serCurSess), str(warn[1]), str(crit[1]), str(serTotSess)))
    return retcode


##### Main starts here

parser = argparse.ArgumentParser(description='Nagios check for F5 BIG-IP OS-based Load-Balancer')
parser.add_argument('-H', '--hostname', type=str, help='hostname or IP address', required=True)
parser.add_argument('-C', '--community', type=str, help='SNMP community (currently only v2c)', required=True)
parser.add_argument('-m', '--mode', type=str, help='Operational mode',
    choices = [
        'help',
        'health',
        'http',
        'enumvs',
        'vsstats',
        'nodestats',
        'mem_tmm',
        'sessions',
    ],
    required=True)
parser.add_argument('-x', '--arg1', type=str, help='optional argument 1 (eg. vs or node name, health flags)', default=None) 
parser.add_argument('-p', '--perfdata', help='enable pnp4nagios perfdata', action='store_true')
parser.add_argument('-w', '--warning', type=str, nargs='?', help='warning trigger', default=10)
parser.add_argument('-c', '--critical', type=str, nargs='?', help='critical trigger', default=6)

args = parser.parse_args()
retcode = 3
message = []
perfmsg = []

snmpSession = netsnmp.Session(Version=2, DestHost=args.hostname, Community=args.community)

if args.mode == 'help':
    print_longHelp()
elif args.mode =='health':
    retcode = get_health_status(args.perfdata)
elif args.mode == 'enumvs':
    retcode = enum_virtualservers()
elif args.mode == 'vsstats':
    retcode = get_vs_stats(args.arg1, args.perfdata)
elif args.mode == 'nodestats':
    retcode = get_node_stats(args.perfdata)
elif args.mode == 'http':
    retcode = get_http_stats(args.perfdata)
elif args.mode == 'mem_tmm':
    retcode = get_mem_tmm(args.perfdata)
elif args.mode == 'sessions':
    retcode = get_sessions(args.perfdata)

print("{}: ".format(retText[retcode]) + "".join(message))
if args.perfdata and len(perfmsg):
    print('|' + " ".join(perfmsg))

exit(retcode)
