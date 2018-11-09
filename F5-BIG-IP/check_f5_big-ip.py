#!/usr/bin/env python
# vim: expandtab sw=4 ts=4:
#
# F5 Load-Balancer running BIG-IP OS Nagios plugin
#
# 2018-11-10 Eric Belhomme <eric.belhomme@axians.com> - Initial write

import argparse, netsnmp



def _get_health_status():
    '''
warning and critical values are tuples for respectively psu, temp, fans triggers
arg1 contains flags that alters the check behaviour :
- ignoremissingpsu : don't trigger any warning or error is a PSU is reported as missing
- warnmissingpsu : trigger warning (instead of critical) error is a PSU is reported as missing

    '''
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
    oid_status_fans = '.1.3.6.1.4.1.3375.2.1.3.2.1.2.1.2'
    retcode = 0
    message = ''

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
    else:
        retcode = 3
        message.append('Unable to retrieve PSU information !\n')

    if psu['missing'] > 0:
        if 'ignoremissingpsu' in args.arg1:
            pass
        elif 'warnmissingpsu' in args.arg1:
            retcode = 1
            message.append("{} PSU missing\n".format(psu['missing']))
        else:
            retcode = 2
            message.append("{} PSU missing\n".format(psu['missing']))
    
    if psu['bad'] > int(warn[0]):
        retcode = 1
        message.append("{} PSU failed\n".format(psu['bad']))
    elif psu['bad'] > int(crit[0]):
        retcode = 2
        message.append("{} PSU failed\n".format(psu['bad']))
    else:
        message.append("{} PSU OK\n".format(psu['good']))

    print(message)

    # PSU info
    vals = snmpSession.walk(netsnmp.VarList(netsnmp.Varbind(oid_status_temperature)))
    if vals:
        for item in vals:
            pass

    # temperature info
    vals = snmpSession.walk(netsnmp.VarList(netsnmp.Varbind(oid_status_fans)))
    if vals:
        for item in vals:
            pass


    	






parser = argparse.ArgumentParser(description='Nagios check for F5 BIG-IP OS-based Load-Balancer')
parser.add_argument('-H', '--hostname', type=str, help='hostname or IP address', required=True)
parser.add_argument('-C', '--community', type=str, help='SNMP community (currently only v2c)', required=True)
parser.add_argument('-P', '--port', type=int, help='SNMP port', default=161)
parser.add_argument('-m', '--mode', type=str, help='Operational mode',
    choices = [
        'health',
        'http',
        'enumvs',
        'vsstats',
        'enumnodes',
        'nodestats',
    ],
    required=True)
parser.add_argument('-x', '--arg1', type=str, help='optional argument 1 (eg. vs or node name, health flags)')    
parser.add_argument('-p', '--perfdata', help='enable pnp4nagios perfdata', action='store_true')
parser.add_argument('-w', '--warning', type=int, nargs='?', help='warning trigger', default=10)
parser.add_argument('-c', '--critical', type=int, nargs='?', help='critical trigger', default=6)

args = parser.parse_args()

print(args.hostname, args.community, args.port)
snmpSession = netsnmp.Session(Version=2, DestHost=args.hostname, Community=args.community, RemotePort=args.port)

_get_health_status()