from unittest import TestCase
from cloudshell.networking.ericsson.extended.seos.autoload.ericsson_seos_extended_snmp_autoload import \
    EricssonExtendedSEOSSNMPAutoload

from cloudshell.snmp.quali_snmp import QualiSnmp
from mock import MagicMock
from cloudshell.core.logger.qs_logger import get_qs_logger


class TestEricssonSEOSAutoload(TestCase):
    def _check_relative_path(self, resources):
        relative_path = []
        for resource in resources:
            if resource.relative_address in relative_path:
                return False
            else:
                relative_path.append(resource.relative_address)
        return True

    def test_is_loads_SE600_correctly(self):
        print '-----------SSR80020------------'
        ip = '192.168.73.52'
        community = 'public'
        logger = get_qs_logger(log_file_prefix=ip)
        cli = MagicMock()
        snmp = QualiSnmp(ip=ip, snmp_community=community, logger=logger)
        handler = EricssonExtendedSEOSSNMPAutoload(snmp_handler=snmp, cli=cli, logger=logger,
                                                   supported_os=["SE[ -]?OS"],
                                                   snmp_community=community)
        result = handler.discover()
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.resources)
        self.assertIsNotNone(result.attributes)
        chassis = [resource for resource in result.resources if 'Chassis' in resource.name]
        modules = [resource for resource in result.resources if resource.model == 'Generic Module']
        ports = [resource for resource in result.resources if resource.model == 'Generic Port']
        port_channels = [resource for resource in result.resources if resource.model == 'Generic Port Channel']
        power_ports = [resource for resource in result.resources if resource.model == 'Generic Power Port']
        sub_modules = [resource for resource in result.resources if 'Sub Module' in resource.name]
        trash_chrs = [attribute for attribute in result.attributes if type(attribute.attribute_value) is str and
                      '\\s' in attribute.attribute_value]
        if len(trash_chrs) > 0:
            for char in trash_chrs:
                print char.relative_address + ': ' + char.attribute_name + ' = ' + char.attribute_value
        self.assertTrue(len(chassis) == 1)
        self.assertTrue(len(ports) == 22)
        self.assertTrue(len(modules) == 4)
        self.assertTrue(len(sub_modules) == 0)
        self.assertTrue(len(port_channels) == 0)
        self.assertTrue(len(power_ports) == 0)
        self.assertFalse(len(trash_chrs) > 0)
        self.assertTrue(self._check_relative_path(result.resources))
        print len(chassis)
        print len(ports)
        print len(modules)
        print len(sub_modules)
        print len(port_channels)
        print str(len(power_ports)) + '\n'
