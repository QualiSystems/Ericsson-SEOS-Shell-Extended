from threading import Thread
from cloudshell.networking.ericsson.extended.seos.ericsson_seos_extended_resource_driver import \
    EricssonSEOSExtendedResourceDriver
from cloudshell.shell.core.context import ResourceCommandContext, ResourceContextDetails, ReservationContextDetails

tt = EricssonSEOSExtendedResourceDriver()

context = ResourceCommandContext()
context.resource = ResourceContextDetails()
context.resource.name = 'dsada'
context.reservation = ReservationContextDetails()
context.reservation.reservation_id = 'c3b410cb-70bd-4437-ae32-15ea17c33a74'
context.resource.attributes = dict()
context.resource.attributes['User'] = 'root'
context.resource.attributes['SNMP Version'] = '2'
context.resource.attributes['SNMP Read Community'] = 'public'
context.resource.attributes['Password'] = 'P0G8gOpDHL0c52ROLdsaVQ=='  # 'NuCpFxP8cJMCic8ePJokug=='
context.resource.attributes['Enable Password'] = 'NuCpFxP8cJMCic8ePJokug=='
context.resource.attributes['Enable SNMP'] = 'False'
context.resource.attributes['Disable SNMP'] = 'False'
context.resource.attributes['CLI Connection Type'] = 'ssh'
context.resource.attributes['VRF Management Name'] = ''
context.resource.attributes['Sessions Concurrency Limit'] = '1'
context.resource.attributes['CLI TCP Port'] = '0'
context.resource.address = '192.168.73.52'
context.resource.name = '2950'

Thread(target=tt.get_inventory, args=(context, )).start()
