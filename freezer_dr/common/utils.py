"""Utility functions shared from all modules into the project."""
# (c) Copyright 2016 Hewlett-Packard Development Company, L.P.
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

import jinja2

from oslo_config import cfg
from oslo_log import log

from freezer_dr.common.osclient import OSClient


CONF = cfg.CONF
LOG = log.getLogger(__name__)


def env(*env_vars, **kwargs):
    """Get all environment variables."""
    for variable in env_vars:
        value = os.environ.get(variable, None)
        if value:
            return value
    return kwargs.get('default', '')


def get_os_client():
    """Return the OpenStack client.

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
        user_domain_name=credentials.get('user_domain_name'),
        **credentials.get('kwargs')
    )

    return client


def load_jinja_templates(template_dir, template_name, template_vars):
    """Load and render existing Jinja2 templates.

    The main purpose of the function is to prepare the message to be sent and
    render it for the driver to send it directly.

    :param template_dir: Location where jinja2 templates are stored
    :param template_name: name of the template to load it
    :param template_vars: Dict to replace existing vars in the template with
                          values.
    :return: String message
    """
    template_loader = jinja2.FileSystemLoader(searchpath=template_dir)
    template_env = jinja2.Environment(loader=template_loader)
    template = template_env.get_template(template_name)
    return template.render(template_vars)


def get_admin_os_client():
    """Return admin client data.

    Loads credentials from [keystone_authtoken] section in the configuration
    file and initialize the client with admin privileges and return
    an instance of the client
    :return: Initialized instance of OS Client
    """
    credentials = CONF.get('keystone_authtoken')
    client = OSClient(
        authurl=credentials.get('auth_url'),
        username=credentials.get('username'),
        password=credentials.get('password'),
        domain_name=credentials.get('domain_name'),
        user_domain_id=credentials.get('user_domain_id'),
        user_domain_name=credentials.get('user_domain_name'),
        **credentials.get('kwargs')
    )
    return client
