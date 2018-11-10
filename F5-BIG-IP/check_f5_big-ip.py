#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: expandtab sw=4 ts=4:
# 
# F5 Load-Balancer running BIG-IP OS Nagios plugin
#
# 2018-11-10 Eric Belhomme <eric.belhomme@axians.com> - Initial write

import argparse, netsnmp

retText = [
    'OK',
    'WARNING',
    'CRITICAL',
    'UNKNOWN',
]



def get_health_status():
    '''
warning and critical values are tuples for respectively psu, temp, fans triggers
arg1 contains flags that alters the check behaviour :
- ignoremissingpsu : don't trigger any warning or error is a PSU is reported as missing
- warnmissingpsu   : trigger warning (instead of critical) error is a PSU is reported as missing
- ignoremissingfan : don't trigger any warning or error is a fan is reported as missing
- warnmissingfan   : trigger warning (instead of critical) error is a fan is reported as missing

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





def enum_virtualservers():

    vals = snmpSession.walk(netsnmp.VarList(
        netsnmp.Varbind('.1.3.6.1.4.1.3375.2.2.10.13.2.1.1'),
        netsnmp.Varbind('.1.3.6.1.4.1.3375.2.2.10.2.3.1.1')))
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
    if perfdata:
        perfmsg.append("'cnx_actv': {}:{}:{}".format(str(cnx_actives), str(warn[0]), str(crit[0])))
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
    if perfdata:
        perfmsg.append("'cnx_total': {}:{}:{}".format(str(cnx_total), str(warn[2]), str(crit[2])))
    message.append( " - bytes in: {}, bytes out: {}\n".format(bytes_in, bytes_out))
    if perfdata:
        perfmsg.append("'bytes_in':".format(bytes_in))
        perfmsg.append("'bytes_out':".format(bytes_out))
    return retcode
    

def get_vs_stats(virtualServer, perfdata=False):
    '''
Retrieve F5 VirtualServer statics
warning and critical values are tuples for respectively : actives_cnx,max_cnx,total_cnx
    '''


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
            if virtualServer in name1:
                # VS name match
                if name1 != name2:
                    message.append("VirtualServer OID names mismatch: {} != {}".format(name1, name2))
                    return 3
                # check status
                retcode = _check_avail(status, 'VirtualServer', name1)
                ret = _get_stats(cnx_actives, cnx_max, cnx_total, bytes_in, bytes_out, warn, crit)
                if ret < 3 and ret > retcode:
                    retcode = ret
    else:
        retcode = 3
        message.append('Failed to retrieve VirtualServer data')
    
    return retcode


def get_node_stats(virtualServer, perfdata=False):

    warn = ('200000','200000','200000')
    if isinstance(args.warning,str) and args.warning is not None:
        warn = tuple(args.warning.split(','))
    crit = ('250000','250000','250000')
    if isinstance(args.critical,str) and args.critical is not None:
        crit = tuple(args.critical.split(','))

    vals = snmpSession.walk( netsnmp.VarList(
        netsnmp.Varbind('.1.3.6.1.4.1.3375.2.2.4.3.2.1.7'),     # Nom des Nodes (Serveurs Réels)
#        netsnmp.Varbind('.1.3.6.1.4.1.3375.2.2.4.3.2.1.3'),     # Statut des Nodes (Serveurs Réels) /!\ deprecated
        netsnmp.Varbind('.1.3.6.1.4.1.3375.2.2.4.3.2.1.3'),     # node availability
        netsnmp.Varbind('.1.3.6.1.4.1.3375.2.2.4.2.3.1.9'),     # Connexions actives par Node (Serveur Réel)
        netsnmp.Varbind('.1.3.6.1.4.1.3375.2.2.4.2.3.1.7'),     # Connexions maximales par Node (Serveur Réel)
        netsnmp.Varbind('.1.3.6.1.4.1.3375.2.2.4.2.3.1.8'),     # Connexions totale par Node (Serveur Réel)
        netsnmp.Varbind('.1.3.6.1.4.1.3375.2.2.4.2.3.1.4'),     # Traffic entrant en octets par Node (Serveurs Réels)
        netsnmp.Varbind('.1.3.6.1.4.1.3375.2.2.4.2.3.1.6'),     # Traffic sortant en octets par Node  (Serveurs Réels)
    ))
    if vals:
        for name, status, cnx_actives, cnx_max, cnx_total, bytes_in, bytes_out in tuple( vals[i:i+7] for i in range(0, len(vals), 7)):
            # check status
            retcode = _check_avail(status, 'Node', name)
            ret = _get_stats(cnx_actives, cnx_max, cnx_total, bytes_in, bytes_out, warn, crit)
            if ret < 3 and ret > retcode:
                retcode = ret
    else:
        retcode = 3
        message.append('Failed to retrieve VirtualServer data')
    
    return retcode





parser = argparse.ArgumentParser(description='Nagios check for F5 BIG-IP OS-based Load-Balancer')
parser.add_argument('-H', '--hostname', type=str, help='hostname or IP address', required=True)
parser.add_argument('-C', '--community', type=str, help='SNMP community (currently only v2c)', required=True)
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
retcode = 3

snmpSession = netsnmp.Session(Version=2, DestHost=args.hostname, Community=args.community)

message = []
perfdata = []


#retcode = get_health_status()
#retcode = enum_virtualservers()
#retcode = get_vs_stats()
retcode = get_node_stats('',True)



print("{}: ".format(retText[retcode]) + "".join(message))
exit(retcode)