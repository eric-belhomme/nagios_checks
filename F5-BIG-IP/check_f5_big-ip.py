#!/usr/bin/env python
# vim: expandtab sw=4 ts=4:
#
# F5 Load-Balancer running BIG-IP OS Nagios plugin
#
# 2018-11-10 Eric Belhomme <eric.belhomme@axians.com> - Initial write

import argparse, re


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
parser.add_argument('-x', '--arg1', type=str, help='optional argument 1 (eg. vs or node name)')    
parser.add_argument('-p', '--perfdata', help='enable pnp4nagios perfdata', action='store_true')
parser.add_argument('-w', '--warning', type=int, nargs='?', help='warning trigger', default=10)
parser.add_argument('-c', '--critical', type=int, nargs='?', help='critical trigger', default=6)

args = parser.parse_args()

snmpSession = netsnmp.Session(Version = 2, DestHost=args.hostname, Community=args.community)

_get_health_status():

def _get_health_status():
    oid_status_psu = '.1.3.6.1.4.1.3375.2.1.3.2.2.2.1.2'
    oid_status_temperature = '.1.3.6.1.4.1.3375.2.1.3.2.3.2.1.2'
    oid_status_fans = '.1.3.6.1.4.1.3375.2.1.3.2.1.2.1.2'

    for item in [oid_status_psu, oid_status_temperature, oid_status_fans]:
    	vals = snmpSession.walk(netsnmp.VarList(netsnmp.Varbind(item)))
        if vals:
            print(vals)
