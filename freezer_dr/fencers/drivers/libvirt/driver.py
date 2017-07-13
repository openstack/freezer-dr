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
import libvirt
from oslo_log import log
from oslo_config import cfg
import time

CONF = cfg.CONF
LOG = log.getLogger(__name__)


class LibvirtDriver(FencerBaseDriver):

    def __init__(self, nodes, fencer_conf):
        super(LibvirtDriver, self).__init__(nodes, fencer_conf)
        self.parser = YamlParser(self.fencer_conf['credentials_file'])
        # initiate libvirt connection
        conn_name = self.fencer_conf.get('name', None)
        self.connection = libvirt.open(name=conn_name)

    def force_shutdown(self, node):
        target = self.connection.lookupByName(name=node.get('domain-name'))
        return target.destroy()

    def graceful_shutdown(self, node):
        target = self.connection.lookupByName(name=node.get('domain-name'))
        return target.shutdown()

    def status(self, node):
        target = self.connection.lookupByName(name=node.get('domain-name'))
        return target.isActive()

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
            for retry in range(0, self.fencer_conf['retries']):
                if self.status(node=node_details):
                    try:
                        self.graceful_shutdown(node=node_details)
                    except Exception as e:
                        LOG.debug(e)
                else:
                    node['status'] = True
                    break
                time.sleep(self.fencer_conf['hold_period'])
                LOG.info('wait for %d seconds before retrying to gracefully '
                         'shutdown' % self.fencer_conf['hold_period'])

            try:
                self.force_shutdown(node=node_details)
            except Exception as e:
                LOG.error(e)

            if not self.status(node=node_details):
                node['status'] = True
            else:
                node['status'] = False
            fenced_nodes.append(node)

        return fenced_nodes

    def get_info(self):
        return {
            'name': 'Libvirt Interface driver',
            'version': 1.1,
            'author': 'Hewlett-Packard Enterprise Company, L.P'
        }


