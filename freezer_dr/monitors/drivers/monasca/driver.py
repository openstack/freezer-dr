# (c) Copyright 2016 Hewlett-Packard Development Enterprise, L.P.
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

import httplib
import time
import urlparse

from monascaclient import client
from oslo_config import cfg
from oslo_log import log

from freezer_dr.common import utils
from freezer_dr.monitors.common import driver

CONF = cfg.CONF
LOG = log.getLogger(__name__)


class MonascaDriver(driver.MonitorBaseDriver):
    """Monasca monitoring driver to monitor compute nodes. It makes use of
    Monasca to monitor the compute nodes. Metric information needed. 'hostname'
     must be used in dimensions to filter the values in alarms. You need to
     define alarms for all hosts with the required metrics."""

    _OPTS = [
        cfg.StrOpt('keystone_url',
                   help="Keystone Url for authentication",
                   required=True),
        cfg.StrOpt('username',
                   help="cloud user used to record monasca alerts and alarms",
                   required=True),
        cfg.StrOpt('password',
                   help="Cloud user's password",
                   required=True),
        cfg.StrOpt('project_name',
                   help='Project/Tenant name. Default is admin',
                   default='admin',
                   required=True),
        cfg.BoolOpt('insecure',
                    help='Use insecure connection.',
                    default=False),
        cfg.StrOpt('project_domain_id',
                   help="Project Domain Id. Default is default",
                   default='default'),
        cfg.StrOpt('user_domain_id',
                   help="User Domain Id. Default is default",
                   default='default'),
        cfg.StrOpt('cacert',
                   help='CA certificate. Default is None',
                   default=None),
        cfg.StrOpt('monasca_url',
                   help='Monasca endpoint URL. This is required to create a '
                        'monasca client instance '
                   ),
        cfg.ListOpt('metrics',
                    help='Monasca Metrics that needs to be checked. Each metric'
                         ' should be defined in a seperate section in the'
                         ' configuration file.',
                    default=['host_alive_status'],
                    required=True
                    ),
        cfg.StrOpt('aggregate',
                   choices=['any', 'all'],
                   default='all',
                   help="If more than one metric used and they reported "
                        "different states i.e.(a:failed, b:success) should we "
                        "evacuate the compute host if only one metric failed "
                        "(any) or only if all failed we evacuate (all). "
                        "Default is all")
    ]

    def __init__(self, backend_name, notifier):
        super(MonascaDriver, self).__init__(backend_name=backend_name,
                                            notifier=notifier)
        self.monasca_client = client.Client(
            "2_0",
            self.conf['monasca_url'],
            auth_url=self.conf['keystone_url'],
            username=self.conf['username'],
            password=self.conf['password'],
            project_name=self.conf['project_name'],
            user_doamin_id=self.conf['user_domain_id'],
            project_doamin_id=self.conf['project_domain_id'],
            insecure=self.conf.get('insecure'),
            cacert=self.conf.get('cacert', None)
            )
        # Compute nodes might be disabled or set to maintenance mode so
        # freezer-dr needs to process only enabled nodes ...
        self.nodes = [node for node in self.get_compute_nodes()
                      if node['status'] == "enabled"]
        # register metric options in their groups and load their values
        self.__load_metrics()

    def _get_raw_data(self):
        """ This function returns the raw data we got from Monasca before
        processing and normalizing. You shouldn't call this function directly.
        :return: dict contains:
        {
            hostname1: {
                metric_name1: [{metric value 1}, {metric value 2}]
                metric_name2: [{metric value 1}, {metric value 2}]
            },
            hostname2: {
                metric_name1: [{metric value 1}, {metric value 2}]
                metric_name2: [{metric value 1}, {metric value 2}]
            }
        }
        """
        data = {}
        for node in self.nodes:
            data[node['host']] = {}
            for metric in self.conf.metrics:
                data[node['host']][metric] = self.monasca_client.alarms.list(
                    **self._build_metrics(
                        metric=metric,
                        hostname=node['host']
                    )
                )
        return data

    def get_data(self):
        """This function returns monitoring data from Monasca. It calls
         _get_raw_data to get raw data and then process these data returns
        a normalized dict
        :return: doct contains:
        {
            hostname1: {
                metric_name1: ['Ok', 'ALARM', 'UNDETERMINED']
                metric_name2: ['OK', 'OK', 'OK']
            },
            hostname2: {
                metric_name1: ['Ok', 'ALARM', 'OK']
                metric_name2: ['ALARM', 'UNDETERMINED', 'OK']
            }
        }
        """
        data = self._get_raw_data()
        data2 = {}
        for host, metric_results in data.iteritems():
            data2[host] = {}
            for metric_name, metric_values in metric_results.iteritems():
                data2[host][metric_name] = []
                for metric_value in metric_values:
                    data2[host][metric_name].append(metric_value.get('state'))
        return data2

    def process_failed(self, nodes=None, wait=1):
        time.sleep(wait)
        data = self.get_data()
        nodes_down = self.analyze_nodes(nodes=data)
        # Thanks Eldar :) for sets
        nodes_down_hosts = set([dnode['host'] for dnode in nodes_down])
        return [node for node in nodes if node['host'] in nodes_down_hosts]

    def get_metrics(self):
        """Lists all metrics
        :return: List of Metrics
        """
        return self.conf['metrics']

    def _build_metrics(self, metric, hostname=None):
        """Build the query to send to Monasca"""
        metric = CONF[metric]
        dimensions = {'hostname': hostname}
        dimensions.update(metric.get('dimensions', {}))

        fields = {
            'metric_dimensions': dimensions,
            'metric_name': metric['metric_name']
        }
        return fields

    def analyze_nodes(self, nodes):
        """It will check if the nodes are in 'OK' state or not. If not they
        will considered down. We have three states as follow:
            1. OK
            2. ALARM
            3. UNDEFINED
        """
        # @todo(szaher) use list comprehension instead of loops
        # list below is correct and should return the extact same value like
        # the two nested for loops
        # nodes_down = [
        #     {"host": hostname} for hostname, metrics in nodes.iteritems() if
        #   [True for name, values in metrics.iteritems() if 'ALARM' in values]
        #     ]
        nodes_data = []
        for node, metrics in nodes.iteritems():
            node_data = {node: []}
            for metric_name, metric_data in metrics.iteritems():
                node_data[node].append(
                    self.__process_metric(node, metric_name, metric_data)
                )
            nodes_data.append(node_data)

        aggregate = self.conf.get('aggregate', 'all')
        aggregate += '({0})'
        nodes_down = []
        for node_data in nodes_data:
            node_info = {}
            for node, data in node_data.iteritems():
                if not data:
                    LOG.warning('No data available for node: {0}'.format(node))
                    continue
                node_info[node] = eval(aggregate.format(data))
            if node_info:
                nodes_down.append(node_info)

        if not nodes_down:
            return []
        return [
            {'host': host.keys()[0]} for host in nodes_down
            if True in host.values()
            ]

    def __process_metric(self, node, metric_name, metric_data):
        """Process metric values got from Monasca.
        Handles UNDETERMINED states and changes it to required state(read
        from config file).
        If no metric data found,"""
        metric_conf = CONF[metric_name]
        # process UNDETERMINED State and change it to the required state
        metric_data = [
            i if i in ['OK', 'ALARM'] else
            metric_conf.get('undetermined', 'ALARM').upper()
            for i in metric_data
        ]
        if not metric_data:
            message = """
            No data found for this metric: {0} <br />
            Data returned: {1} <br />
            hostname: {2} <br />
            Cause might be: <br />
            <ul>
            <li>Metric is not defined in Monasca </li>
            <li>Alarm with this metric name is not set for this host </li>
            <li>Check your Monasca configuration and Metric configuration
                 defined in freezer-dr.conf </li>
            </ul>
            You can try this command to check: <br /><code>
            $ monasca alarm-list --metric-name {3} --metric-dimensions
                  hostname={2}
            </code>
            <br /> <br />
            Freezer-DR
            """.format(metric_name, str(metric_data), node,
                       metric_conf['metric_name'])
            self.notifier.notify(message)
            LOG.warning("No data found for metric: {0} on host: {1}".format(
                metric_name, node
            ))
            exit(1)
        # build the decision
        aggregate = metric_conf.get('aggregate')
        aggregate += "(x=='ALARM' for x in metric_data)"
        return eval(aggregate)

    def is_alive(self):
        url = urlparse.urlparse(self.conf.monasca_url)
        if url.scheme == 'https':
            http_connector = httplib.HTTPSConnection
        else:
            http_connector = httplib.HTTPConnection
        try:
            connection = http_connector(host=url.netloc)
            connection.request('HEAD', url=url.path)
            response = connection.getresponse()
        except httplib.socket.error:
            return False
        try:
            if getattr(response, 'status') in [200, 401]:
                return True
        except AttributeError:
            pass
        return False

    def get_info(self):
        return {
            'name': 'Monasca Driver',
            'version': 1.0,
            'author': 'Hewlett-Packard Development Enterprise, L.P'
                }

    def get_compute_nodes(self):
        """Get a list of available compute hosts."""
        client = utils.get_os_client()
        return client.novacomputes()

    def __load_metrics(self):
        """load custom sections created by user"""
        for metric in self.conf.metrics:
            CONF.register_opts(self.__metric_opts, group=metric)

    @property
    def __metric_opts(self):
        """List of options to be used in metric defined sections"""
        return [
            cfg.StrOpt("metric_name",
                       help="Metric Name used to log monitoring information"
                            " in Monasca",
                       required=True),
            cfg.DictOpt("dimensions",
                        default={},
                        help="Dict that contains dimensions information. "
                             "component:nova-compute,service:compute",
                        ),
            cfg.StrOpt("aggregate",
                       choices=["any", "all"],
                       help="How to consider the compute node is down. If you "
                            "metric reports many states, like checking "
                            "different services on the compute host, should we"
                            " consider if one component down all are down or"
                            " only if all components are down. Default is all."
                            " This means if all components fail, freezer-dr"
                            " will consider the host failed",
                       default='all'
                       ),
            cfg.StrOpt("undetermined",
                       choices=['OK', 'ALARM'],
                       default='ALARM',
                       help="How to handle UNDETERMINED states. It can be "
                            "ignored, will be considered OK state or can be "
                            "considered ALARM. Default is ALARM")

        ]
