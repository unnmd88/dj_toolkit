import asyncio


from pysnmp.hlapi.asyncio import *
from toolkit.sdp_lib.management_controllers import controller_management2, controller_management
from toolkit.sdp_lib.management_controllers.snmp_oids import Oids



def oupt_snmp_data(data):
    vals = {}
    for oid, val in data:
        print(f'oid: {str(oid)}, val: {str(val)}')
        vals[f'{Oids(str(oid)).name}[{str(oid)}]'] = val.prettyPrint()

    print(vals)

ip = '10.122.38.3'
host_id = 'test_laba'

h = controller_management.GetDifferentStatesFromWeb(ip, host_id)
err, res, obj  = asyncio.run(h.get_request())

print(res[1].result().split())
for line in res[1].result().split():
    print(line)