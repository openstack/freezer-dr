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
from osha.common.osclient import OSClient

CONF = cfg.CONF
LOG = log.getLogger(__name__)


class EvacuationManager(object):
    """
    The Evacuation procedure is as follow:
    1- Put node in maintenance mode (disable node )
    2- make sure it's in maintenance mode or disabled
    3- try to fence node and shutdown it
    4- make sure node is down
    5- Get a list of instances running on this node
    6- Evacuate :)
    """
    def __init__(self):
        """
        @todo we cannot get the credentials from monitoring so, we need to get
        it from keystone section and we need to review that for code in other
         parts
        :return:
        """
        credentials = CONF.get('monitoring')
        self.client = OSClient(
            authurl=credentials.get('endpoint'),
            username=credentials.get()
        )
