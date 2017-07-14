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
from freezer_dr.evacuators.common.driver import EvacuatorBaseDriver


class DummyEvacuator(EvacuatorBaseDriver):
    """Evacuation driver that does nothing. Useful for testing other parts
    of Freezer-DR.
    """

    def __init__(self, nodes, evacuator_conf, fencer):
        super(DummyEvacuator, self).__init__(nodes, evacuator_conf, fencer)

    def disable_node(self, node):
        return True

    def get_node_status(self, node):
        return False

    def is_node_disabled(self, node):
        return True

    def evacuate_nodes(self, nodes):
        return nodes

    def get_node_instances(self, node):
        raise NotImplementedError

