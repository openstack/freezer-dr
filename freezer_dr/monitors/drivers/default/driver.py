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
from freezer_dr.common.osclient import OSClient
from freezer_dr.monitors.common.driver import MonitorBaseDriver
from time import sleep
from oslo_config import cfg
from oslo_log import log
from httplib import HTTPConnection
from httplib import HTTPSConnection
from httplib import socket
from urlparse import urlparse

CONF = cfg.CONF
LOG = log.getLogger(__name__)


class StandardDriver(MonitorBaseDriver):
    _OPTS = [
        cfg.StrOpt('username',
                   help='username to be used to initialize the default '
                        'monitoring driver'),
        cfg.StrOpt('password',
                   help='Password to be used for initializing the default '
                        'monitoring driver'),
        cfg.StrOpt('endpoint',
                   help='Monitoring system API endpoint'),
        cfg.DictOpt('kwargs',
                    default={},
                    help='List of kwargs if you want to pass it to initialize'
                         ' the monitoring driver. should be provided in'
                         ' key:value format'),
    ]

    def __init__(self, backend_name, notifier):
        super(StandardDriver, self).__init__(backend_name=backend_name,
                                             notifier=notifier)
        self.endpoint = self.conf.endpoint
        client = OSClient(
            authurl=self.conf.endpoint,
            username=self.conf.username,
            password=self.conf.password,
            **self.conf.kwargs
        )
        LOG.info("OSClient:: username: %s, password: %s, endpoint: %s, kwargs:"
                 " %s" % (self.conf.username, '****', self.conf.endpoint,
                          self.conf.kwargs)
                 )
        self.client = client

    def get_data(self):
        hypervisors = self.client.novahypervisors()
        computes = self.client.novacomputes()
        agents = self.client.neutronagents()
        data = {'hypervisors': hypervisors,
                'computes': computes,
                'agents': agents}
        return data

    def process_failed(self, nodes=None, wait=0):
        if not wait:
            wait = CONF.wait
        if not nodes:
            return None
        sleep(wait)
        # @todo do the api call again to get the nodes status again
        data = self.get_data()
        nodes_down = self.analyze_nodes(nodes=data)
        # Thanks Eldar :) for sets
        nodes_down_hosts = set([dnode['host'] for dnode in nodes_down])
        return [node for node in nodes if node['host'] in nodes_down_hosts]

    def get_metrics(self):
        return ['nova-compute', 'hypervisor', 'neutron-ovs-agent']

    def analyze_nodes(self, nodes):
        # list all down nova compute
        nova_down = self.is_nova_service_down(nodes.get('computes'))
        # list all down hypervisors
        hypervisor_down = self.is_hpyervisor_down(nodes.get('hypervisors'))
        # list all down openvswitch agents
        agents_down = self.is_neutron_agents_down(nodes.get('agents'))

        nodes_down = []
        for server in hypervisor_down:
            ip = server.get('ip')
            host = server.get('host')
            if host in nova_down and host in agents_down:
                node = {'ip': ip, 'host': host}
                nodes_down.append(node)

        return nodes_down

    def is_alive(self):
        url = urlparse(self.endpoint)
        if url.scheme == 'https':
            http_connector = HTTPSConnection
        else:
            http_connector = HTTPConnection
        try:
            connection = http_connector(host=url.netloc)
            connection.request('HEAD', url=url.path)
            response = connection.getresponse()
        except socket.error:
            return False
        try:
            if getattr(response, 'status') == 200:
                return True
        except AttributeError:
            pass
        return False

    def get_info(self):
        return {
            'name': 'Freezer DR Native Driver',
            'version': 1.0,
            'author': 'Hewlett-Packard Development Company, L.P'
                }

    def is_hpyervisor_down(self, hypervisors):
        down_hosts = []
        for hypervisor in hypervisors:
            if hypervisor.get('state') == 'down':
                host = {}
                host['host'] = hypervisor.get('service').get('host')
                host['ip'] = hypervisor.get('host_ip')
                down_hosts.append(host)

        return down_hosts

    def is_nova_service_down(self, computes):
        down_hosts = []
        for node in computes:
            if node.get('state') == 'down' and node.get('status') == 'enabled':
                down_hosts.append(node.get('host'))
        return down_hosts

    def is_neutron_agents_down(self, agents):
        down_hosts = []
        for agent in agents:
            if agent.get('admin_state_up') and not agent.get('alive'):
                down_hosts.append(agent.get('host'))

        return down_hosts

