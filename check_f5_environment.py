#!/usr/bin/python

import sys
from pysnmp.entity.rfc3413.oneliner import cmdgen
import logging
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
parse.add_option('-p', '--port', dest='port')
parse.add_option('-c', '--community', dest='community')

(opts, args) = parse.parse_args()
if opts.hostname is None:
    print 'Host not defined'
    exit(UNKNOWN)
else:
    host = opts.hostname

if opts.port:
    port = opts.port
else:
    port = 161

if opts.community is None:
    print 'Community not defined'
    exit(UNKNOWN)
else:
    community = opts.community

# CPU Temperature threshold based on Intel E3-1230 V2 @ 3.30GHz
# Chassis temperature thresholds based on 'tmsh show sys hardware'

F5_BIGOP_SYSTEM_MIB_CRITS = {
    'sysChassisFanStatus_1':            '0 2',
    'sysChassisFanStatus_2':            '0 2',
    'sysChassisFanStatus_3':            '0 2',
    'sysChassisFanStatus_4':            '0 2',
    'sysChassisPowerSupplyStatus_1':    '0 2',
    'sysChassisPowerSupplyStatus_2':    '0 2',
    'sysChassisTemperature_1':          '80',
    'sysChassisTemperature_2':          '60',
    'sysChassisTemperature_3':          '40',
    'sysChassisTemperature_4':          '40',
    'sysChassisTemperature_5':          '50',
    'sysChassisTemperature_6':          '50',
    'sysChassisTemperature_7':          '63',
    'sysChassisTemperature_8':          '63',
    'sysChassisTemperature_9':          '50',
    'sysChassisTemperature_10':         '80',
    'sysCpuTemperature_1':              '60',
    'sysStatMemoryUsed_0':              '3000000000', # TMM Memory use, 3GB out of 12GB
    'sysHostMemoryUsed_0':              '33767682048' # OS Memory is completely used
}


F5_BIGIP_SYSTEM_MIB_MAP = {
    'sysChassisFanStatus_1':            '1.3.6.1.4.1.3375.2.1.3.2.1.2.1.2.1',
    'sysChassisFanStatus_2':            '1.3.6.1.4.1.3375.2.1.3.2.1.2.1.2.2',
    'sysChassisFanStatus_3':            '1.3.6.1.4.1.3375.2.1.3.2.1.2.1.2.3',
    'sysChassisFanStatus_4':            '1.3.6.1.4.1.3375.2.1.3.2.1.2.1.2.4',
    'sysChassisPowerSupplyStatus_1':    '1.3.6.1.4.1.3375.2.1.3.2.2.2.1.2.1',
    'sysChassisPowerSupplyStatus_2':    '1.3.6.1.4.1.3375.2.1.3.2.2.2.1.2.2',
    'sysChassisTemperature_1':          '1.3.6.1.4.1.3375.2.1.3.2.3.2.1.2.1',
    'sysChassisTemperature_2':          '1.3.6.1.4.1.3375.2.1.3.2.3.2.1.2.2',
    'sysChassisTemperature_3':          '1.3.6.1.4.1.3375.2.1.3.2.3.2.1.2.3',
    'sysChassisTemperature_4':          '1.3.6.1.4.1.3375.2.1.3.2.3.2.1.2.4',
    'sysChassisTemperature_5':          '1.3.6.1.4.1.3375.2.1.3.2.3.2.1.2.5',
    'sysChassisTemperature_6':          '1.3.6.1.4.1.3375.2.1.3.2.3.2.1.2.6',
    'sysChassisTemperature_7':          '1.3.6.1.4.1.3375.2.1.3.2.3.2.1.2.7',
    'sysChassisTemperature_8':          '1.3.6.1.4.1.3375.2.1.3.2.3.2.1.2.8',
    'sysChassisTemperature_9':          '1.3.6.1.4.1.3375.2.1.3.2.3.2.1.2.9',
    'sysChassisTemperature_10':         '1.3.6.1.4.1.3375.2.1.3.2.3.2.1.2.10',
    'sysCpuTemperature_1':              '1.3.6.1.4.1.3375.2.1.3.6.2.1.2.0.1',
    'sysStatMemoryUsed_0':              '1.3.6.1.4.1.3375.2.1.1.2.1.45.0',
    'sysHostMemoryUsed_0':              '1.3.6.1.4.1.3375.2.1.7.1.2.0'
}

cmdGen = cmdgen.CommandGenerator()
alerts = []
exit_code = 0

for k, oid in F5_BIGIP_SYSTEM_MIB_MAP.items():
    try:
        error_indication, error_status, error_index, var_binds = cmdGen.getCmd(
            cmdgen.CommunityData(community),
            cmdgen.UdpTransportTarget((host, port)),
            oid
        )
        if error_indication:
            LOGGER.info("Error fetching data from OID %s", oid)
            exit_code = 1
            continue
        else:
            for name, val in var_binds:
                if ('Status' in k):
                    if (str(val) in str(F5_BIGOP_SYSTEM_MIB_CRITS.get(k))):
                        # If the return value has a 0 (unplugged for PSU,
                        # missing for Fans) or a 2 (missing for PSU), add an
                        # alert.
                        status = ('CRITICAL {0} is {1} ; broken or '
                                  'unplugged.'.format(k,val))
                        alerts.append(status)
                else:
                    if (int(F5_BIGOP_SYSTEM_MIB_CRITS.get(k)) < int(val)):
                        status = ('CRITICAL {0} is {1} which is '
                                  'over threshold'.format(k, val))
                        alerts.append(status)
    except:
        LOGGER.info("Error with pysnmp on %s", host)
        exit(UNKNOWN)

if not alerts and exit_code is 0:
    LOGGER.info("OK - F5 environment is pleasant.")
    exit(OK)
elif exit_code is 1:
    exit(WARNING)
else:
    for alert in alerts:
        LOGGER.info(str(alert))
    exit(CRITICAL)
