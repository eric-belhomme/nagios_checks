#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: expandtab sw=4 ts=4:
"""
Nagios plugin that checks ElasticSearch health status
2018-10-31 Eric Belhomme <rico-github@ricozome.net> - Initial work
Published under MIT license
"""

import sys, argparse, paramiko, requests, json, re

__author__ = 'Eric Belhomme'
__contact__ = 'rico-github@ricozome.net'
__license__ = 'MIT'

requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

parser = argparse.ArgumentParser()
parser.add_argument('-H', '--hostname', type=str, help='Elastic server hostname or IP address', required=True)
parser.add_argument('-U', '--username', type=str, help='username', required=True)
parser.add_argument('-P', '--password', type=str, help='user password', required=True)
parser.add_argument('-p', '--port', type=str, nargs='?', help='listening port', default='9200')
parser.add_argument('-s', '--ssl', help='use SSL/TLS layer', action='store_true')
parser.add_argument('-d', '--perfdata', help='enable Nagios perf data', action='store_true')

args = parser.parse_args()
proto = 'http'
if args.ssl:
    proto='https'

#curl -u admin:nOVvIxqiMYXhT_X -XGET 'https://172.20.9.18:9200/_cluster/health?pretty' -k
url = "{proto}://{hostname}:{port}/_cluster/health".format(
    proto=proto,
    hostname=args.hostname,
    port=args.port,
)

NagiosExit = { 'OK': 0, 'WARNING': 1, 'CRITICAL': 2, 'UNKNOWN': 3 }
req = requests.get( url, auth=(args.username, args.password), verify=False )

if req:
    out = json.loads(req.text)
#    print(out['cluster_name'])
#    print(out)

    if out['status'] == 'red':
        message = 'CRITICAL'
    elif out['status'] == 'yellow':
        message = 'WARNING'
    elif out['status'] == 'green':
        message = 'OK'
    else:
        message = 'UNKNOWN'

    exitcode = NagiosExit[message]
    if exitcode != NagiosExit['UNKNOWN']:
        message += ": ElasticSearch ({cluster_name}) is running with \'{status}\' status.\n" \
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
            unassigned_shards=out['unassigned_shards']
        )
        if args.perfdata:
            message += "\n|'active_primary'={active_primary_shards} 'active'={active_shards} " \
                "'relocating'={relocating_shards} 'init'={initializing_shards} 'delay_unass'=" \
                "{delayed_unassigned_shards} 'unass'={unassigned_shards}".format(
                active_primary_shards=out['active_primary_shards'],
                active_shards=out['active_shards'],
                relocating_shards=out['relocating_shards'],
                initializing_shards=out['initializing_shards'],
                delayed_unassigned_shards=out['delayed_unassigned_shards'],
                unassigned_shards=out['unassigned_shards'])

else:
    exitcode = NagiosExit['UNKNOWN']
    message = "Unable to request URL {}".format(url)

print(message)
exit(exitcode)
