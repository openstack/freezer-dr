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

from keystoneclient.auth.identity import v3
from keystoneclient import session
from novaclient.v2 import client as novaclient
from neutronclient.v2_0 import client as neutronclient
from oslo_log import log

LOG = log.getLogger(__name__)


class OSClient:
    def __init__(self, authurl, authmethod='password', ** kwargs):
        """
        Provide Openstack credentials to initalize the connection to Openstack
        :param authmethod: string authmethod should be password or token but
         currently we support only password !
        :param kwargs: username, user_id, project_name, project_id,
        default_domain_id,
        """
        self.authmethod = authmethod
        self.authurl = authurl
        self.auth_session = None
        if authmethod == 'password':
            self.username = kwargs.get('username', None)
            self.password = kwargs.get('password')
            self.project_name = kwargs.get('project_name', None)
            self.project_id = kwargs.get('project_id', None)
            self.user_id = kwargs.get('user_id', None)
            self.user_domain_id = kwargs.get('user_domain_id', None)
            self.user_domain_name = kwargs.get('user_domain_name', None)
            self.project_domain_name = kwargs.get('project_domain_name', None)
            self.endpoint_type = kwargs.get('endpoint_type', 'internal')
        else:
            print "The available authmethod is password for the time being" \
                  "Please, provide a password credentials :) "

        self.auth()

    def auth(self):
        auth = v3.Password(auth_url=self.authurl,
                           username=self.username,
                           password=self.password,
                           project_name=self.project_name,
                           user_domain_id=self.user_domain_id,
                           user_domain_name=self.user_domain_name,
                           project_domain_name=self.project_domain_name)
        self.auth_session = session.Session(auth=auth)

    def novacomputes(self):
        nova = novaclient.Client(session=self.auth_session,
                                 endpoint_type=self.endpoint_type)
        services = nova.services.list()
        compute_nodes = []
        compute_hosts = []
        for service in services:
            service = service.to_dict()
            if service.get('binary') == 'nova-compute':
                compute_nodes.append(service)
                compute_hosts.append(service.get('host'))
        self.compute_hosts = compute_hosts
        return compute_nodes

    def novahypervisors(self):
        nova = novaclient.Client(session=self.auth_session,
                                 endpoint_type=self.endpoint_type)
        hypervisors = nova.hypervisors.list()
        nova_hypervisors = []

        for hypervisor in hypervisors:
            nova_hypervisors.append(hypervisor.to_dict())
        return nova_hypervisors

    def neutronagents(self, hosts=[]):
        if not hosts:
            hosts = self.compute_hosts
        new_sess = session.Session(auth=self.auth_session.auth)
        neutron = neutronclient.Client(session=new_sess,
                                       endpoint_type=self.endpoint_type)
        self.auth_session = new_sess
        agents = neutron.list_agents()
        neutron_agents = []
        for agent in agents.get('agents'):
                if agent.get('host') in hosts and agent.get('binary') == \
                        'neutron-openvswitch-agent':
                    neutron_agents.append(agent)

        return neutron_agents

    def evacuate(self, nodes):
        """
        Will get the hypervisors and list all running VMs on it and then start
        Evacuating one by one ...
        :param nodes: List of nodes to be evacuated !
        :return: List of nodes with VMs that were running on that node
        """
        new_sess = session.Session(auth=self.auth_session.auth)
        nova = novaclient.Client(session=new_sess,
                                 endpoint_type=self.endpoint_type)
        self.auth_session = new_sess
        evacuated_nodes = []
        for node in nodes:
            hypervisors = nova.hypervisors.search(node.get('host'), True)
            for hypervisor in hypervisors:
                if not hasattr(hypervisor, 'servers'):
                    break
                for server in hypervisor.servers:
                    try:
                        nova.servers.evacuate(server.get('uuid'),
                                              on_shared_storage=True)
                    except Exception as e:
                        LOG.error(e)
                host = {'host': node.get('host'), 'servers': hypervisor.servers}
                evacuated_nodes.append(host)
        return evacuated_nodes

    def set_in_maintance(self, nodes):
        new_sess = session.Session(auth=self.auth_session.auth)
        nova = novaclient.Client(session=new_sess,
                                 endpoint_type=self.endpoint_type)
        self.auth_session = new_sess
        for node in nodes:
            output = []
            host = nova.hosts.get(node)[0]
            values = {"maintenance_mode": "enable"}
            try:
                output.append(host.update(values))
            except Exception as e:
                LOG.error(e)
            return output

    def get_session(self):
        auth_session = session.Session(auth=self.auth_session.auth)
        return auth_session

    def get_node_status(self, node):
        """
        Check the node nova-service status and if it's disabled or not
        :param node: dict contains node info
        :return: True or False. True => node disabled, False => node is enabled
        or unknow status !
        """
        nova = novaclient.Client(session=self.auth_session,
                                 endpoint_type=self.endpoint_type)
        try:
            node_service = nova.services.find(host=node.get('host'))
            del nova
        except Exception as e:
            LOG.error(e)
            return False

        if not node_service:
            return False
        node = node_service.to_dict()
        if node.get('status') == 'disabled':
            return True
        return False

    def disable_node(self, node):
        auth_session = session.Session(auth=self.auth_session.auth)
        nova = novaclient.Client(session=auth_session,
                                 endpoint_type=self.endpoint_type)
        try:
            node_service = nova.services.find(host=node.get('host'))
        except Exception as e:
            LOG.error(e)
            return False

        if not node_service:
            return False
        node = node_service.to_dict()
        del node_service
        try:
            nova.services.disable_log_reason(
                host=node.get('host'),
                binary=node.get('binary'),
                reason='Host Failed and needs to be evacuated.'
            )
            del nova
            LOG.info('Compute host: %s has been disabled to be evacuated. '
                     'Host details: %s' % (node.get('host'), str(node)))
        except Exception as e:
            LOG.error(e)
            return False
        return True

    def get_hypervisor_instances(self, node):
        auth_session = session.Session(auth=self.auth_session.auth)
        nova = novaclient.Client(session=auth_session,
                                 endpoint_type=self.endpoint_type)
        hypervisors = nova.hypervisors.search(node.get('host'), True)
        if not hypervisors:
            return []
        return hypervisors[0].servers


