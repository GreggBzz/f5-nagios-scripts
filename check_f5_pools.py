#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
f5 pool status checker. Uses BigIP
REST API for version 11.5+
"""
from __future__ import division
import json
import urllib3
import logging
import ssl
import os
import sys
import optparse

OK = 0
WARNING = 1
CRITICAL = 2
UNKNOWN = 3
LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.StreamHandler(sys.stdout))
LOGGER.setLevel(logging.INFO)

parse = optparse.OptionParser()
parse.add_option('-H', '--hostname', dest='hostname')
parse.add_option('-u', '--username', dest='username')
parse.add_option('-p', '--password', dest='password')
parse.add_option('-P', '--poolname', dest='poolname')
(opts, args) = parse.parse_args()

if ((opts.hostname is None) or (opts.poolname is None)
     or (opts.username is None) or (opts.password is None)):
    print ('useage: check_f5_pools.py -H <hostname> -u <username>'
           ' -p <password> -P <poolname>')
    exit(UNKNOWN)

urllib3.disable_warnings()
http = urllib3.PoolManager()

hostname = opts.hostname
poolname = opts.poolname
username = opts.username
password = opts.password

pool_url = ('https://' + hostname + '/mgmt/tm/ltm/pool/~Common~'
            + opts.poolname + '/members')

auths = username + ':' + password
headers = urllib3.util.make_headers(basic_auth=auths)

try:
  pool_status_json = http.request('GET', pool_url, headers=headers)
except:
  alert = ('Communication error with the F5 - check your connection and'
         ' credentials.')
  LOGGER.info(str(alert))
  exit(UNKNOWN)

try:
  pool_status = json.loads(pool_status_json.data)
except ValueError:
  alert = ('F5 auth error or bad JSON - check your connection and'
           ' credentials.')
  LOGGER.info(str(alert))
  exit(UNKNOWN)

total_members = 0
available_members = 0

status = OK

for i in pool_status['items']:
  if str(i['state']) == 'up':
    available_members += 1
  total_members += 1

if available_members == 0:
  alert = ('CRITICAL {0} has {1} out of {2} members online!'
           .format(poolname, available_members, total_members))
  LOGGER.info(str(alert))
  exit(CRITICAL)
else:
  available_ratio = available_members / total_members

if available_ratio < 0.68:
  alert = ('CRITICAL {0} has {1} out of {2} members online!'
           .format(poolname, available_members, total_members))
  status = CRITICAL  
elif available_ratio < 1:
  alert = ('WARNING {0} has {1} out of {2} members online!'
           .format(poolname, available_members, total_members))
  status = WARNING
elif available_ratio == 1:
  alert = ('OK {0} has {1} out of {2} members online.'
           .format(poolname, available_members, total_members))
  status = OK

LOGGER.info(str(alert))
exit(status)
