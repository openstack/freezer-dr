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


class MonitorManager(object):

    def __init__(self, notifier):
        monitor = CONF.get('monitoring')
        backend_name = monitor['backend_name']
        self.driver = importutils.import_object(
            monitor.driver,
            backend_name=backend_name,
            notifier=notifier
        )
        driver_info = self.driver.get_info()
        LOG.info('Initializing driver %s with version %s found in %s' %
                 (driver_info['name'], driver_info['version'],
                  monitor.get('driver')))

    def monitor(self):
        # Check if the monitoring system is a live
        is_alive = self.driver.is_alive()
        # if not a live will record that in logs and will try to communicate !
        if not is_alive:
            LOG.error('Monitoring system is not a live or may be driver is '
                      'missing implementation for is_alive method')

        # getting data from the monitoring system
        # may be in future we add a hock function to external data processors !
        # @todo add external data processors to analyze the monitoring systems
        # data to separate monitoring from analysis
        data = self.driver.get_data()

        # Asking the driver to analyze the data provided and provide list
        # of failed nodes
        nodes_down = self.driver.analyze_nodes(nodes=data)
        if not nodes_down:
            LOG.info('No nodes reported down')
            return 0  # for the time being we will exit with no error !

        LOG.info('Nodes Down are: %s will be double checked again after %s '
                 'seconds' % (str(nodes_down), CONF.wait))
        nodes_to_evacuate = self.driver.process_failed(nodes=nodes_down,
                                                       wait=CONF.wait)
        return nodes_to_evacuate

    def get_driver_info(self):
        return self.driver.get_info()
