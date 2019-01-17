#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: expandtab sw=4 ts=4:
"""
Retrieve cpu-load and memory usage on old ComWare equipment throught CLI by SSH
2019-01-17 Eric Belhomme <rico-github@ricozome.net> - Initial work
Published under MIT license
"""

import argparse, paramiko, re
from pprint import pprint

__author__ = 'Eric Belhomme'
__contact__ = 'rico-github@ricozome.net'
__license__ = 'MIT'

recode = 3
output = []
perfdata = []
message = ''

rettxt = [
    'OK',
    'WARNING',
    'CRITICAL',
    'UNKNOWN',
]

re_prompt = re.compile(r"^<.*>.*$")


def process_cpu_usage(bufferOut, warning, critical):

    cpu_usage = []
    re_slot = re.compile(r"^Slot (?P<slot>\d+) CPU.*")
    re_cpu = re.compile(r"^\s+(?P<cpu>\d+)% in last 1 min.*")
    slot = 0

    for line in bufferOut:

        match = re_prompt.match(line)
        if match:
            break

        match = re_slot.match(line)
        if match:
            slot = match.group('slot')
        
        match = re_cpu.match(line)
        if match:
            cpu_usage.append((slot, match.group('cpu')))

    if len(cpu_usage) > 0:
        avg = 0.0
        for slot, cpu in cpu_usage:
            avg += float(cpu)
        avg = avg / len(cpu_usage)

        if avg <= warning:
            retcode = 0
        elif avg <= critical:
            retcode = 1
        else:
            retcode = 2

        output.append("{}: Average CPU load : {}%".format(rettxt[retcode], round(avg,2)))
        if args.perfdata:
            perfdata.append("avg_cpu={};{};{}".format(cpu, warning, critical))
        for slot, cpu in cpu_usage:
            output.append("Slot {} CPU load : {}%".format(slot, cpu))
            if args.perfdata:
                perfdata.append("cpu_slot_{}={};{};{}".format(slot, cpu, warning, critical))
    else:
        recode = 3
        output.append('{}: No CPU slot found !'.format(rettxt[retcode]))


def process_memory_usage(bufferOut, warning, critical):

    re_total = re.compile(r'^System Total.*:\s+(?P<total>\d+).*$')
    re_used = re.compile(r'^Total Used.*:\s+(?P<used>\d+).*$')

    total, used = 1, 1

    for line in bufferOut:

        if re_prompt.match(line):
            break

        match = re_total.match(line)
        if match:
            total = match.group('total')

        match = re_used.match(line)
        if match:
            used = match.group('used')

    ratio = (int(used) * 100) / int(total)
    warn = (int(total) * warning) / 100
    crit = (int(total) * critical) / 100
    if int(used) <= warn:
        retcode = 0
    elif int(used) <= crit:
        retcode = 1
    else:
        retcode =2

    output.append("{}: Memory usage : {} MB / {} MB ({}%)".format(rettxt[retcode], int(used)/1024/1024, int(total)/1024/1024, round(ratio,2)))
    if args.perfdata:
        perfdata.append("memory={};{};{};0;{}".format(used, warn, crit, total))


parser = argparse.ArgumentParser(description='Nagios check for ComWare switch')
parser.add_argument('-H', '--hostname', type=str, help='hostname or IP address', required=True)
parser.add_argument('-U', '--username', type=str, help='username', required=True)
parser.add_argument('-P', '--password', type=str, help='user password', required=True)
parser.add_argument('-t', '--type', type=str, help='check type', choices=['cpu-load', 'memory'], required=True)
parser.add_argument('-p', '--perfdata', help='enable pnp4nagios perfdata', action='store_true')
parser.add_argument('-w', '--warning', type=int, nargs='?', help='warning trigger', default=80)
parser.add_argument('-c', '--critical', type=int, nargs='?', help='critical trigger', default=90)
args = parser.parse_args()

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect( args.hostname, username=args.username, password=args.password)
stdin, stdout, stderr = ssh.exec_command("")
    
if args.type.startswith('cpu-load'):
    #stdin, stdout, stderr = ssh.exec_command('dis cpu-usage')
    stdin, stdout, stderr = ssh.exec_command('cat /tmp/cpu')
    stdout=stdout.readlines()
    process_cpu_usage(stdout, args.warning, args.critical)
elif args.type.startswith('memory'):
    stdin, stdout, stderr = ssh.exec_command('cat /tmp/mem')
    #stdin, stdout, stderr = ssh.exec_command('dis memory')
    stdout=stdout.readlines()
    process_memory_usage(stdout, args.warning, args.critical)

ssh.close()

for out in output:
    message += "{}\n".format(out)
if len(perfdata):
    message += '| '
    for out in perfdata:
        message += "{} ".format(out)

print(message)
exit(retcode)