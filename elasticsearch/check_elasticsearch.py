#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: expandtab sw=4 ts=4:
'''
Nagios plugin that checks ElasticSearch health status
2018-10-31 Eric Belhomme <rico-github@ricozome.net> - Initial work
Published under MIT license
'''

import sys, argparse, paramiko, requests, json, re, collections

__author__ = 'Eric Belhomme'
__contact__ = 'rico-github@ricozome.net'
__license__ = 'MIT'

requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
NagiosExit = { 'OK': 0, 'WARNING': 1, 'CRITICAL': 2, 'UNKNOWN': 3 }


def processHealth(out):
    '''
Retrieve Elasticearch cluster health by requesting _cluster/health API:
curl -ku admin:password -XGET 'https://elastic.local:9200/_cluster/health?pretty'

warning and critical trggers are useless for this check
    '''

    message = ['UNKNOWN',]
    if out['status'] == 'red':
        message[0] = 'CRITICAL'
    elif out['status'] == 'yellow':
        message[0] = 'WARNING'
    elif out['status'] == 'green':
        message[0] = 'OK'

    if message[0] != 'UNKNOWN':
        message.append(": ElasticSearch ({cluster_name}) is running with \'{status}\' status.\n" \
            "{nodes} nodes on cluster, with {data_nodes} data nodes:\n" \
            "  active primary shards : {active_primary_shards}\n" \
            "  active shards         : {active_shards}\n" \
            "  relocating shards     : {relocating_shards}\n" \
            "  initializing shards   : {initializing_shards}\n" \
            "  delayed unassigned shards : {delayed_unassigned_shards}\n" \
            "  unassigned shards     : {unassigned_shards}".format(
            cluster_name=out['cluster_name'],
            status=out['status'],
            nodes=out['number_of_nodes'],
            data_nodes=out['number_of_data_nodes'],
            active_primary_shards=out['active_primary_shards'],
            active_shards=out['active_shards'],
            relocating_shards=out['relocating_shards'],
            initializing_shards=out['initializing_shards'],
            delayed_unassigned_shards=out['delayed_unassigned_shards'],
            unassigned_shards=out['unassigned_shards'])
        )
        if args.perfdata:
            message.append("\n|'active_primary'={active_primary_shards} 'active'={active_shards} " \
                "'relocating'={relocating_shards} 'init'={initializing_shards} 'delay_unass'=" \
                "{delayed_unassigned_shards} 'unass'={unassigned_shards}".format(
                active_primary_shards=out['active_primary_shards'],
                active_shards=out['active_shards'],
                relocating_shards=out['relocating_shards'],
                initializing_shards=out['initializing_shards'],
                delayed_unassigned_shards=out['delayed_unassigned_shards'],
                unassigned_shards=out['unassigned_shards'])
            )
    return message


def processIndices(text, warn, crit):
    '''
Retrieve indinces catalog:
curl -ku 'admin:password' -XGET 'https://elastic.local:9200/_cat/indices'
then triggers warning or critical depending of:
  * the status of open index (if some are not green status)
  * the number of open triggers (if it exceed trigger values defined by warning
    or critical command-line parameters)
    '''
    message = ['UNKNOWN','']
    items = []
    regex = re.compile(r"^(?P<status>\w+)\s+open\s+(?P<index>[-\.\w\d]+)\s+.*$")
    for line in text.splitlines():
        m = re.match(regex, line)
        if m:
            items.append((m.group(1), m.group(2),))
    
    counts = collections.Counter([x[0] for x in items])
    message[1] = "{} opened indexes ({} green, {} yellow, {} red)".format(
        len(items), counts['green'], counts['yellow'], counts['red'])

    if counts['red'] > 0:
        message[0] = 'CRITICAL'
    elif counts['yellow'] > 0:
        message[0] = 'WARNING'
    elif counts['green']:
        message[0] = 'OK'

    if NagiosExit[message[0]] < NagiosExit['WARNING'] and len(items) > warn:
        message[0] = 'WARNING'
        message.insert(1,'Too many opened indexes: ')
    if NagiosExit[message[0]] < NagiosExit['CRITICAL'] and len(items) > crit:
        message[0] = 'CRITICAL'
        message.insert(1,'Too many opened indexes: ')

    message.insert(1, ': ')
    if args.perfdata:
        message.append("\n|'indexes'={};{};{}".format(len(items), warn, crit))
    return message



parser = argparse.ArgumentParser()
parser.add_argument('-H', '--hostname', type=str, help='Elastic server hostname or IP address', required=True)
parser.add_argument('-U', '--username', type=str, help='username', required=True)
parser.add_argument('-P', '--password', type=str, help='user password', required=True)
parser.add_argument('-p', '--port', type=str, nargs='?', help='listening port', default='9200')
parser.add_argument('-s', '--ssl', help='use SSL/TLS layer', action='store_true')
parser.add_argument('-d', '--perfdata', help='enable Nagios perf data', action='store_true')
parser.add_argument('-m', '--mode', help='check mode', choices=['health', 'indices'], default='health')
parser.add_argument('-w', '--warning', help='warning trigger for indices', type=int, default=32)
parser.add_argument('-c', '--critical', help='critical trigger for indices', type=int, default=64)

args = parser.parse_args()

proto = 'http'
if args.ssl:
    proto='https'

url = "{proto}://{hostname}:{port}/".format(
    proto=proto,
    hostname=args.hostname,
    port=args.port,
)

if args.mode == 'health':
    url += '_cluster/health'
elif args.mode == 'indices':
    url += '_cat/indices?v'   
else:
    print('unknown mode !')

req = requests.get( url, auth=(args.username, args.password), verify=False )
message = []
if req:
    if args.mode == 'health':
        out = json.loads(req.text)
        message = processHealth(out)
    elif args.mode == 'indices':
        message = processIndices(req.text, args.warning, args.critical)        
else:
    message[0] = 'UNKNOWN'
    message = "Unable to request URL {}".format(url)

print("".join(message))
exit(NagiosExit[message[0]])
