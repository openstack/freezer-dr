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
from oslo_config import cfg
from oslo_log import log
from osha.common.osclient import OSClient
from osha.fencers.common.manager import FencerManager

CONF = cfg.CONF
LOG = log.getLogger(__name__)


class EvacuationManager(object):
    """
    The Evacuation procedure is as follow:
    1- Put node in maintenance mode (disable node )
    2- make sure it's in maintenance mode or disabled
    3- try to fence node and shutdown it
    4- make sure node is down
    5- Get a list of instances running on this node
    6- Evacuate :)
    """
    def __init__(self, nodes=[]):
        """
        @todo we cannot get the credentials from monitoring so, we need to get
        it from keystone section and we need to review that for code in other
         parts
        :return:
        """
        credentials = CONF.get('keystone_authtoken')
        self.client = OSClient(
            authurl=credentials.get('auth_url'),
            username=credentials.get('username'),
            password=credentials.get('password'),
            project_name=credentials.get('project_name'),
            user_domain_id=credentials.get('user_domain_id'),
            project_domain_id=credentials.get('project_domain_id'),
            project_domain_name=credentials.get('project_domain_name'),
            user_domain_name=credentials.get('user_domain_name')
        )
        self.nodes = nodes
        if not nodes:
            raise Exception('No nodes to evacuate ...')


    def evacuate(self):
        """
        This fn will do the evacuation process ...
        :param nodes: List of Failed nodes got from the monitoring system
        :return: List of nodes with success or Fail
        """
        self.check_nodes_maintenance()
        trigger_disable = False
        for node in self.nodes:
            if not node.get('status'):
                trigger_disable = True
                break
        if trigger_disable:
            self._disable_nodes()
        self.fence_nodes()
        self.list_host_instances()

    def _disable_nodes(self):
        disabled_nodes = []
        for node in self.nodes:
            node_status = self.client.get_node_status(hostname=node.get('host'))
            if node_status.get('status') == 'enabled':
                node['status'] = self.client.disable_node(
                    hostname=node.get('host'))
            else:
                node['status'] = True
            disabled_nodes.append(node)

        self.nodes = disabled_nodes

    def check_nodes_maintenance(self):
        nodes_status = []
        for node in self.nodes:
            status = self.client.get_node_status(hostname=node.get('host'))
            if status.get('status') == 'enabled':
                node['status'] = False
                nodes_status.append(node)
            else:
                node['status'] = True
                nodes_status.append(node)

        self.nodes = nodes_status

    def fence_nodes(self):
        fencer = FencerManager(self.nodes)
        nodes = fencer.fence()
        print nodes

    def list_host_instances(self):
        self.client.evacuate(self.nodes)