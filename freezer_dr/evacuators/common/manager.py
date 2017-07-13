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
from freezer_dr.fencers.common.manager import FencerManager
from time import sleep
from freezer_dr.evacuators.common.utils import get_nodes_details

CONF = cfg.CONF
LOG = log.getLogger(__name__)


class EvacuationManager(object):

    def __init__(self, enable_fencing=True):
        self.enable_fencing = enable_fencing

    def evacuate(self, nodes):
        fencer = FencerManager(nodes)
        evacuation_conf = CONF.get('evacuation')
        driver = importutils.import_object(
            evacuation_conf['driver'],
            nodes,
            evacuation_conf,
            fencer
        )

        return driver.evacuate(self.enable_fencing)

    def get_nodes_details(self, nodes):
        """
        To be re-structured after fixing the nova bug !
        :param nodes: list of nodes
        :return: list of node with more details
        """
        return get_nodes_details(nodes)
