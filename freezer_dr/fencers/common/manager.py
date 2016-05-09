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
from freezer_dr.common.yaml_parser import YamlParser
from time import sleep

CONF = cfg.CONF
LOG = log.getLogger(__name__)


class FencerManager(object):

    def __init__(self, nodes):
        self.fencer = CONF.get('fencer')
        self.nodes = nodes
        self.parser = YamlParser(self.fencer.get('credentials_file'))

    def fence(self):
        """
        Try to shutdown nodes and wait for configurable amount of times
        :return: list of nodes and either they are shutdown or failed
        """
        processed_nodes = []
        for node in self.nodes:
            node_details = self.parser.find_server_by_ip(node.get('ip')) or\
                           self.parser.find_server_by_hostname(node.get('host'))
            driver = importutils.import_object(
                self.fencer.get('driver'),
                node=node_details,
                **self.fencer.get('options')
            )
            node['status'] = self.do_shutdown_procedure(driver)
            processed_nodes.append(node)
        return processed_nodes

    def do_shutdown_procedure(self, driver):
        for retry in range(0, self.fencer.get('retries', 1)):
            if driver.status():
                try:
                    driver.graceful_shutdown()
                except Exception as e:
                    LOG.error(e)
            else:
                return True
            # try to wait a pre-configured amount of time before redoing
            # the fence call again :)
            sleep(self.fencer.get('hold_period', 10))
            LOG.info('wait for %d seconds before retrying to gracefully '
                     'shutdown' % self.fencer.get('hold_period', 10))
            LOG.info('Retrying to gracefully shutdown the node.')

        try:
            driver.force_shutdown()
        except Exception as e:
            LOG.error(e)

        if not driver.status():
            return True

        return False

