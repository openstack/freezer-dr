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
from freezer_dr.evacuators.common.driver import EvacuatorBaseDriver
from freezer_dr.common.utils import get_os_client
import time
CONF = cfg.CONF
LOG = log.getLogger(__name__)


class StandardEvacuator(EvacuatorBaseDriver):

    def __init__(self, nodes, evacuator_conf, fencer):
        super(StandardEvacuator, self).__init__(nodes, evacuator_conf, fencer)
        # initialize the OS client!
        self.client = get_os_client()
        self.wait = evacuator_conf.get('wait')
        self.retires = evacuator_conf.get('retries', 1)
        if self.retires <= 0:
            self.retires = 1

    def _disable_node(self, node):
        if not self.is_node_disabled(node):
                return self.disable_node(node)
        else:
            True

    def evacuate(self, enable_fencing=True):
        # try to disable node
        # @todo needs more error handling like if the status didn't update or
        # we are unable to disable the node ???
        failed_nodes = []  # maintain nodes that are going to fail at any state
        succeeded_nodes = []
        for node in self.nodes:
            status = False
            for i in range(0, self.retires):
                status = self._disable_node(node)
                # if True ( node disabled ) break the loop
                if status:
                    break
                else:
                    status = False
            node['status'] = status
            # make sure the disable request was successful
            if not self.get_node_status(node):
                # if the node failed at any step no reason to move it to
                # the next step
                failed_nodes.append(node)
                self.nodes.remove(node)  #
            else:
                succeeded_nodes.append(node)

        nodes = succeeded_nodes
        if enable_fencing:
            nodes = self.fencer.fence(nodes=nodes)
        """
        @todo this code needs to be commented for the time being till we fix
         nova bug found in state, which always go up afer enable or disable. We
         will use get_node_details for the time being from the main script to
         get nodes details before evacuating ...
        succeeded_nodes = []
        for node in nodes:
            node['instances'] = self.driver.get_node_instances(node)
            succeeded_nodes.append(node)

        nodes = succeeded_nodes
        """
        # Start evacuation calls ...
        evacuated_nodes = []
        for i in range(0, self.retires):
            try:
                time.sleep(self.wait)
                nodes = self.evacuate_nodes(nodes)
                if not nodes:
                    break
                evacuated_nodes = nodes
            except Exception as e:
                LOG.error(e)

        return evacuated_nodes, failed_nodes

    def get_node_instances(self, node):
        return self.client.get_hypervisor_instances(node)

    def disable_node(self, node):
        return self.client.disable_node(node)

    def get_node_status(self, node):
        return self.client.get_node_status(node)

    def is_node_disabled(self, node):
        return self.client.get_node_status(node)

    def evacuate_nodes(self, nodes):
        return self.client.evacuate(
            nodes, shared_storage=self.evacuator_conf['shared_storage'])
