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
CONF = cfg.CONF
LOG = log.getLogger(__name__)


class StandardEvacuator(EvacuatorBaseDriver):

    def __init__(self, wait, retires, **kwargs):
        super(StandardEvacuator, self).__init__(wait, retires, **kwargs)
        self.client = get_os_client()

    def get_node_instances(self, node):
        return self.client.get_hypervisor_instances(node)

    def disable_node(self, node):
        return self.client.disable_node(node)

    def get_node_status(self, node):
        return self.client.get_node_status(node)

    def is_node_disabled(self, node):
        return self.client.get_node_status(node)

    def evacuate_nodes(self, nodes):
        return self.client.evacuate(nodes)



