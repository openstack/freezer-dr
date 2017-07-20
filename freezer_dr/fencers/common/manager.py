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
from oslo_utils import importutils


CONF = cfg.CONF
LOG = log.getLogger(__name__)


class FencerManager(object):

    def __init__(self, nodes):
        self.fencer_conf = CONF.get('fencer')
        self.nodes = nodes

    def fence(self, nodes=None):
        """
        Try to shutdown nodes and wait for configurable amount of times
        :return: list of nodes and either they are shutdown or failed
        """
        # update the list of nodes if required!
        if nodes:
            self.nodes = nodes
        driver_name = self.fencer_conf['driver']
        driver = importutils.import_object(
            driver_name,
            self.nodes,
            self.fencer_conf
        )
        LOG.debug('Loaded fencing driver {0} with config: '
                  '{1}'.format(driver.get_info(), self.fencer_conf))

        return driver.fence()
