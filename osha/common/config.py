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
from osha.common.utils import env
import sys
from osha import __version__ as OSHA_VERSION
from oslo_log import log

CONF = cfg.CONF

_MONITORS = [
    cfg.StrOpt('driver',
               default='osha.monitors.drivers.osha.driver.OshaDriver',
               help='Driver used to get a status updates of compute nodes'),
    cfg.StrOpt('username',
               help='username to be used to initialize the monitoring driver'),
    cfg.StrOpt('password',
               help='Password to be used for initializing monitoring driver'),
    cfg.StrOpt('endpoint',
               help='Monitoring system API endpoint'),
    cfg.DictOpt('kwargs',
                default={},
                help='List of kwargs if you want to pass it to initialize'
                     ' the monitoring driver. should be provided in key:value '
                     'format')
]


_COMMON = [
    cfg.IntOpt('wait',
               default=30,
               help='Time to wait between different operations')
]

_FENCOR = [
    cfg.StrOpt('credentials-file',
               help='YAML File contains the required credentials for compute '
                    'nodes'),
    cfg.IntOpt('retries',
               default=1,
               help='Number of retries to fence the each compute node. Must be'
                    ' at least 1 to try first the soft shutdown'),
    cfg.IntOpt('hold-period',
               default=10,
               help='Time in seconds to wait between retries. Should be '
                    'reasonable amount of time as different servers take '
                    'different times to shut off'),
    cfg.StrOpt('driver',
               default='osha.fencors.drivers.ipmi.driver.IpmiDriver',
               help='Choose the best fencor driver i.e.(ipmi, libvirt, ..'),
    cfg.DictOpt('options',
                default={},
                help='List of kwargs to customize the fencor operation. You '
                     'fencor driver should support these options. Options '
                     'should be in key:value format')
]


def build_os_options():
    osclient_opts = [
        cfg.StrOpt('os-username',
                   default=env('OS_USERNAME'),
                   help='Name used for authentication with the OpenStack '
                        'Identity service. Defaults to env[OS_USERNAME].',
                   dest='os_username'),
        cfg.StrOpt('os-password',
                   default=env('OS_PASSWORD'),
                   help='Password used for authentication with the OpenStack '
                        'Identity service. Defaults to env[OS_PASSWORD].',
                   dest='os_password'),
        cfg.StrOpt('os-project-name',
                   default=env('OS_PROJECT_NAME'),
                   help='Project name to scope to. Defaults to '
                        'env[OS_PROJECT_NAME].',
                   dest='os_project_name'),
        cfg.StrOpt('os-project-domain-name',
                   default=env('OS_PROJECT_DOMAIN_NAME'),
                   help='Domain name containing project. Defaults to '
                        'env[OS_PROJECT_DOMAIN_NAME].',
                   dest='os_project_domain_name'),
        cfg.StrOpt('os-user-domain-name',
                   default=env('OS_USER_DOMAIN_NAME'),
                   help='User\'s domain name. Defaults to '
                        'env[OS_USER_DOMAIN_NAME].',
                   dest='os_user_domain_name'),
        cfg.StrOpt('os-tenant-name',
                   default=env('OS_TENANT_NAME'),
                   help='Tenant to request authorization on. Defaults to '
                        'env[OS_TENANT_NAME].',
                   dest='os_tenant_name'),
        cfg.StrOpt('os-tenant-id',
                   default=env('OS_TENANT_ID'),
                   help='Tenant to request authorization on. Defaults to '
                        'env[OS_TENANT_ID].',
                   dest='os_tenant_id'),
        cfg.StrOpt('os-auth-url',
                   default=env('OS_AUTH_URL'),
                   help='Specify the Identity endpoint to use for '
                        'authentication. Defaults to env[OS_AUTH_URL].',
                   dest='os_auth_url'),
        cfg.StrOpt('os-backup-url',
                   default=env('OS_BACKUP_URL'),
                   help='Specify the Freezer backup service endpoint to use. '
                        'Defaults to env[OS_BACKUP_URL].',
                   dest='os_backup_url'),
        cfg.StrOpt('os-region-name',
                   default=env('OS_REGION_NAME'),
                   help='Specify the region to use. Defaults to '
                        'env[OS_REGION_NAME].',
                   dest='os_region_name'),
        cfg.StrOpt('os-token',
                   default=env('OS_TOKEN'),
                   help='Specify an existing token to use instead of retrieving'
                        ' one via authentication (e.g. with username & '
                        'password). Defaults to env[OS_TOKEN].',
                   dest='os_token'),
        cfg.StrOpt('os-identity-api-version',
                   default=env('OS_IDENTITY_API_VERSION'),
                   help='Identity API version: 2.0 or 3. '
                        'Defaults to env[OS_IDENTITY_API_VERSION]',
                   dest='os_identity_api_version'),
        cfg.StrOpt('os-endpoint-type',
                   choices=['public', 'publicURL', 'internal', 'internalURL',
                            'admin', 'adminURL'],
                   default=env('OS_ENDPOINT_TYPE') or 'public',
                   help='Endpoint type to select. Valid endpoint types: '
                        '"public" or "publicURL", "internal" or "internalURL",'
                        ' "admin" or "adminURL". Defaults to '
                        'env[OS_ENDPOINT_TYPE] or "public"',
                   dest='os_endpoint_type'),
    ]

    return osclient_opts


def configure():
    CONF.register_cli_opts(build_os_options())
    CONF.register_opts(_COMMON)
    monitors_grp = cfg.OptGroup('monitoring',
                                title='Monitoring',
                                help='Monitoring Driver/plugin to be used to '
                                     'monitor compute nodes')
    CONF.register_group(monitors_grp)
    CONF.register_opts(_MONITORS, group='monitoring')

    fencors_grp = cfg.OptGroup('fencor',
                                title='Fencor Options',
                                help='Fencor Driver/plugin to be used to '
                                     'fence compute nodes')
    CONF.register_group(fencors_grp)
    CONF.register_opts(_FENCOR, group='fencor')

    default_conf = cfg.find_config_files('osha', 'osha',
                                         '.conf')
    log.register_options(CONF)

    CONF(args=sys.argv[1:],
         project='osha',
         default_config_files=default_conf,
         version=OSHA_VERSION
         )


def setup_logging():
    _DEFAULT_LOG_LEVELS = ['amqp=WARN', 'amqplib=WARN', 'boto=WARN','qpid=WARN',
                           'stevedore=WARN', 'oslo_log=INFO', 'iso8601=WARN',
                           'requests.packages.urllib3.connectionpool=WARN',
                           'urllib3.connectionpool=WARN', 'websocket=WARN',
                           'keystonemiddleware=WARN', 'osha=INFO']

    _DEFAULT_LOGGING_CONTEXT_FORMAT = ('%(asctime)s.%(msecs)03d %(process)d '
                                       '%(levelname)s %(name)s [%(request_id)s '
                                       '%(user_identity)s] %(instance)s'
                                       '%(message)s')
    log.set_defaults(_DEFAULT_LOGGING_CONTEXT_FORMAT, _DEFAULT_LOG_LEVELS)
    log.setup(CONF, 'osha', version=OSHA_VERSION)


def list_opts():
    _OPTS = {
        None: _COMMON,
        'monitoring': _MONITORS,
        'keystone': build_os_options(),
        'fencor': _FENCOR
    }

    return _OPTS.items()

