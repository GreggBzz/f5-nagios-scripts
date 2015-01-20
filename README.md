F5 Nagios Scripts
=================
check_f5_environment.py - checks chassis and CPU temeratures. Checks fan and power supply status. Checks memory use (on a 5050 chassis).
You may want to customize the thresholds in F5_BIGOP_SYSTEM_MIB_CRITS based on "tmsh show sys hardware." Known to work on a 5050 chassis
with version BigIP version 11.5.

check_f5_pools.py - checks pool status using the API. You'll need an API user and password. Known to work on a 5050 chassis with BigIP version 
11.5.


Requirements
------------
check_f5_environment.py: requires, optparse and pysnmp.
check_f5_pools.py: requires json, ssl, optparse and urllib3.

