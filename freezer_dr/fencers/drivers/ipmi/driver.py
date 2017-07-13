# (c) Copyright 2014,2015 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from freezer_dr.common.yaml_parser import YamlParser
from freezer_dr.fencers.common.driver import FencerBaseDriver
from freezer_dr.fencers.drivers.ipmi.ipmitool import IpmiInterface
from oslo_log import log
from oslo_config import cfg
import time

CONF = cfg.CONF
LOG = log.getLogger(__name__)


class IpmiDriver(FencerBaseDriver):

    def __init__(self, nodes, fencer_conf):

        super(IpmiDriver, self).__init__(nodes, fencer_conf)
        self.parser = YamlParser(self.fencer_conf['credentials_file'])

    def prepare_node(self, node):
        """Prepares the subprocess to call ``ipmitool`` with the node details!
        :param node: dict contains node fencing information
        """
        self.interface = IpmiInterface(
            node.get('fencer-ip'),
            node.get('fencer-user'),
            node.get('fencer-password'),
            verbose=CONF.debug)

    def force_shutdown(self):
        try:
            self.interface.power_down()
        except Exception as e:
            LOG.error(e)

    def graceful_shutdown(self):
        try:
            self.interface.power_soft()
        except Exception as e:
            LOG.error(e)

    def status(self):
        return self.interface.get_power_status()

    # @todo remove this fn as it's for testing purposes only :)
    def power_on(self):
        self.interface.power_on()

    def get_node_details(self, node):
        """Loads the node's fencing information from ``credentials_file``
        :param node: a dict contains node ip or hostname
        :return: a dict contains node fencing information
        """
        node_details = self.parser.find_server_by_ip(node.get('ip')) or \
                       self.parser.find_server_by_hostname(node.get('host'))

        return node_details

    def fence(self):
        """Implements the fencing procedure for server fencing using ipmi
        :return: a list of nodes and weather they're fenced or not!
        """
        fenced_nodes = []
        for node in self.nodes:
            LOG.debug("fencing node {0}".format(node))
            # load node details
            node_details = self.get_node_details(node)
            # loop on the node number of n times trying to fence it gently,
            # if not force it!
            self.prepare_node(node_details)
            for retry in range(0, self.fencer_conf['retries']):
                if self.status():
                    try:
                        self.graceful_shutdown()
                    except Exception as e:
                        LOG.debug(e)
                else:
                    node['status'] = True
                    break
                time.sleep(self.fencer_conf['hold_period'])
                LOG.info('wait for %d seconds before retrying to gracefully '
                         'shutdown' % self.fencer_conf['hold_period'])

            try:
                self.force_shutdown()
            except Exception as e:
                LOG.error(e)

            if not self.status():
                node['status'] = True
            else:
                node['status'] = False
            fenced_nodes.append(node)

        return fenced_nodes

    def get_info(self):
        return {
            'name': 'IPMI Interface driver',
            'version': 1.1,
            'author': 'Hewlett-Packard Enterprise Company, L.P'
        }
