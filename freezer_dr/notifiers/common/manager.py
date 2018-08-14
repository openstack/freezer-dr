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


class NotificationManager(object):

    def __init__(self):
        notifier_conf = CONF.get('notifiers')
        self.driver = importutils.import_object(
            notifier_conf.get('driver'),
            notifier_conf.get('endpoint'),
            notifier_conf.get('username'),
            notifier_conf.get('password'),
            notifier_conf.get('templates-dir'),
            notifier_conf.get('notify-from'),
            notifier_conf.get('notify-list'),
            **notifier_conf.get('options')
        )

    def notify(self, nodes, status):
        """
        Send Notification to users added on tenants that has VMs running on the
        affected host.
        :param nodes: List of hosts that are affected, contains instances
        running on those hosts, tenants, users added on those tenants.
        :param status: success or error
        :return:
        """
        for node in nodes:
            self.driver.notify_status(node, status)

    def get_driver(self):
        return self.driver



