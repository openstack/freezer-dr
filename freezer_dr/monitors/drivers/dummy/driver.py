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
from freezer_dr.monitors.common.driver import MonitorBaseDriver


class DummyDriver(MonitorBaseDriver):
    """ A monitoring driver that returns a configured list of nodes as failed.

    This can be useful for testing without actually shutting down the nodes.
    The nodes that should be reported as failing, can be configured in the
    monitoring section of the freezer_dr configuration file as follows:
       kwargs = nodes_down:hostname1;hostname2
    """

    def __init__(self, username, password, endpoint, **kwargs):
        super(DummyDriver, self).__init__(username, password, endpoint, **kwargs)

        hostnames = kwargs['nodes_down'].split(';')
        self.nodes_down = [{'host': n} for n in hostnames]

    def get_data(self):
        return self.nodes_down

    def get_metrics(self):
        raise NotImplementedError()

    def process_failed(self, nodes=None, wait=0):
        return nodes

    def analyze_nodes(self, nodes):
        return nodes

    def is_alive(self):
        return True

    def get_info(self):
        return {
            'name': 'Freezer DR Dummy Driver',
            'version': 1.0,
            'author': 'Hewlett-Packard Development Company, L.P'
                }
