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

import os
from osha.common.osclient import OSClient
from oslo_config import cfg
from oslo_log import log

CONF = cfg.CONF
LOG = log.getLogger(__name__)


def env(*env_vars, **kwargs):
    for variable in env_vars:
        value = os.environ.get(variable, None)
        if value:
            return value
    return kwargs.get('default', '')


def get_os_client():
    """
    Loads credentials from [keystone_authtoken] section in the configuration
    file and initialize the client and return an instance of the client
    :return: Initialized instance of OS Client
    """
    credentials = CONF.get('keystone_authtoken')
    client = OSClient(
        authurl=credentials.get('auth_url'),
        username=credentials.get('username'),
        password=credentials.get('password'),
        project_name=credentials.get('project_name'),
        user_domain_id=credentials.get('user_domain_id'),
        project_domain_id=credentials.get('project_domain_id'),
        project_domain_name=credentials.get('project_domain_name'),
        user_domain_name=credentials.get('user_domain_name')
    )

    return client
