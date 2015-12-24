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
from osha.common import config
from oslo_config import cfg
from oslo_log import log
from osha.monitors.common.manager import MonitorManager
from osha.fencers.common.manager import FencerManager
from osha.common.osclient import OSClient

CONF = cfg.CONF
LOG = log.getLogger(__name__)


def main():
    config.configure()
    config.setup_logging()
    LOG.info('Starting osha ... ')
    # load and initialize the monitoring driver
    mon = CONF.get('monitoring')
    client = OSClient(
            authurl=mon.get('endpoint'),
            username=mon.get('username'),
            password=mon.get('password'),
            **mon.get('kwargs')
        )
    client.disable_node('padawan-ccp-comp0003-mgmt')
    #client.set_in_maintance(['padawan-ccp-comp0003-mgmt'])
    exit()
    monitor = MonitorManager()
    # Do the monitoring procedure
    # Monitor, analyse, nodes down ?, wait, double check ? evacuate ..
    nodes = monitor.monitor()

    if nodes:
        # @todo put node in maintenance mode :) Not working with virtual
        # deployments
        # Load Fence driver
        # Shutdown the node
        fencer = FencerManager(nodes)
        nodes = fencer.fence()
        print "Fenced nodes are", nodes