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
from freezer_dr.common import config
from oslo_config import cfg
from oslo_log import log
from freezer_dr.monitors.common.manager import MonitorManager
from freezer_dr.evacuators.common.manager import EvacuationManager
from freezer_dr.notifiers.common.manager import NotificationManager

CONF = cfg.CONF
LOG = log.getLogger(__name__)


def main():
    config.configure()
    config.setup_logging()
    LOG.info('Starting Freezer DR ... ')
    # initialize the notification driver as it will be used in many parts
    notifier = NotificationManager()
    # load and initialize the monitoring driver
    monitor = MonitorManager(notifier=notifier.get_driver())
    # Do the monitoring procedure
    # Monitor, analyse, nodes down ?, wait, double check ? evacuate ..
    nodes = monitor.monitor()

    if nodes:
        # @todo put node in maintenance mode :) Not working with virtual
        # deployments
        # Load Fence driver
        # Shutdown the node
        evac = EvacuationManager()
        notify_nodes = evac.get_nodes_details(nodes)
        evacuated_nodes, failed_nodes = evac.evacuate(nodes)
        LOG.debug("Successfully evacuated nodes {0}".format(evacuated_nodes))
        LOG.debug("Failed to evacuate nodes {0}".format(failed_nodes))
        notifier.notify(notify_nodes, 'success')
        failed_nodes = evac.get_nodes_details(failed_nodes)
        notifier.notify(failed_nodes, 'error')
    else:
        print "No nodes reported to be down"
