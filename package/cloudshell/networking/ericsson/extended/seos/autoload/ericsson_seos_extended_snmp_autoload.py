import json
import os
import re
import time

import inject

from cloudshell.configuration.cloudshell_cli_binding_keys import CLI_SERVICE
from cloudshell.networking.ericsson.extended.ericsson_extended_snmp_autoload import EricssonExtendedSNMPAutoload
from cloudshell.shell.core.context_utils import get_attribute_by_name


class EricssonExtendedSEOSSNMPAutoload(EricssonExtendedSNMPAutoload):
    def __init__(self, snmp_handler=None, logger=None, supported_os=None, cli=None, snmp_community=None):
        """Basic init with injected snmp handler and logger

            :param snmp_handler:
            :param logger:
            :return:
            """
        super(EricssonExtendedSEOSSNMPAutoload, self).__init__(snmp_handler, logger, supported_os)
        self._cli = cli
        self.snmp_view = 'qualiview'
        self.snmp_community = snmp_community
        self.vendor_type_exclusion_pattern = ['port.*mgmt']
        self.module_details_regexp = r'^(?P<module_model>.*)\s+[Cc]ard\s+\d+\s+sn:(?P<serial_number>.*)\s+rev:(?P<version>.*) id'
        self.interface_mapping_key = 'rbnIpBindHierarchicalIfIndex'
        self.interface_mapping_mib = 'RBN-IP-BIND-MIB'
        self._load_configuration()
        self.enable_snmp = True
        self.disable_snmp = False
        self.load_mib_list = ['RBN-PRODUCT-MIB']
        if not self.snmp_community:
            self.snmp_community = get_attribute_by_name('SNMP Read Community') or 'qualicommunity'

    def load_ericsson_mib(self):
        path = os.path.abspath(os.path.join(os.path.dirname(__file__), '', 'mib'))
        self.snmp.update_mib_sources(path)

    def _load_configuration(self):
        local_path = os.path.dirname(__file__)
        self.configuration_file_path = os.path.abspath(
            os.path.join(local_path, '', 'ericsson_ext_seos_autoload_config.json'))
        str_config = open(self.configuration_file_path, 'r').read()
        self.configuration = json.loads(str_config)

    @property
    def cli(self):
        if self._cli is None:
            self._cli = inject.instance(CLI_SERVICE)
        return self._cli

    def discover(self):
        try:
            self.enable_snmp = (get_attribute_by_name('Enable SNMP') or 'true').lower() == 'true'
            self.disable_snmp = (get_attribute_by_name('Disable SNMP') or 'false').lower() == 'true'
        except:
            pass

        if self.enable_snmp:
            self._enable_snmp()
        try:
            result = self.get_autoload_details()
        except Exception as e:
            self.logger.error('Autoload failed: {0}'.format(e.message))
            raise Exception('EricssonGenericSNMPAutoload', e.message)
        finally:
            if self.disable_snmp:
                self._disable_snmp()
        return result

    def _enable_snmp(self):
        existing_snmp_server = 'snmp server is not running' not in self.cli.send_command('show snmp server').lower()
        existing_snmp_view = self.snmp_view in self.cli.send_command('show snmp view').lower()
        existing_snmp_community = self.snmp_community in self.cli.send_command('show snmp communities').lower()

        if not existing_snmp_server:
            self.cli.send_config_command('snmp server enhance ifmib')

        if not existing_snmp_view:
            self.cli.send_config_command('snmp view {0} internet included'.format(self.snmp_view))
            if existing_snmp_community:
                self.cli.send_config_command('no snmp community {0}'.format(self.snmp_community))
                existing_snmp_community = False

        if not existing_snmp_community:
            self.cli.send_config_command('snmp community {0} all-contexts view qualiview read-only'.format(
                self.snmp_community))
        self.cli.commit()

    def _disable_snmp(self):
        time.sleep(5)
        self.cli.send_config_command('no snmp community {0}'.format(self.snmp_community))
        self.cli.send_config_command('no snmp view {0}'.format(self.snmp_view))
        self.cli.send_config_command('no snmp server')
        self.cli.send_config_command('end')

    def _get_chassis_model(self, chassis_id):
        model = self.entity_table[chassis_id]['entPhysicalDescr']
        model = re.sub('\s+CLEI.*$', '', model)
        model_match = re.search(r'chassis.*', self.entity_table[chassis_id]['entPhysicalVendorType'], re.IGNORECASE)
        if model_match:
            model = model_match.group()
        return model
