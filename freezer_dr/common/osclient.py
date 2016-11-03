"""OpenStack client class."""
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
from __future__ import print_function

from keystoneclient import session

from keystoneclient.auth.identity import v3

from keystoneclient import client as keystoneclient

from neutronclient.v2_0 import client as neutronclient

from novaclient import client as novaclient

from oslo_log import log


LOG = log.getLogger(__name__)


class OSClient:
    """Provide OpenStack credentials to initalize the connection."""

    def __init__(self, authurl, authmethod='password', ** kwargs):
        """Initialize the all class vars.

        :param authmethod: string authmethod should be password or token but
         currently we support only password !
        :param kwargs: username, user_id, project_name, project_id,
        default_domain_id,
        """
        self.authmethod = authmethod
        self.authurl = authurl
        self.auth_session = None
        self.endpoint_type = 'internalURL'
        self.interface = 'internal'
        self.verify = True
        self.insecure = kwargs.pop('insecure', False)
        if self.insecure:
            self.verify = not bool(self.insecure)

        if authmethod == 'password':
            if 'endpoint_type' in kwargs:
                self.endpoint_type = kwargs.pop('endpoint_type', 'internalURL')
            if 'interface' in kwargs:
                self.interface = kwargs.pop('interface', 'internal')
            self.kwargs = kwargs
            # self.username = kwargs.get('username', None)
            # self.password = kwargs.get('password')
            # self.project_name = kwargs.get('project_name', None)
            # self.project_id = kwargs.get('project_id', None)
            # self.user_id = kwargs.get('user_id', None)
            # self.user_domain_id = kwargs.get('user_domain_id', None)
            # self.user_domain_name = kwargs.get('user_domain_name', None)
            # self.project_domain_name =
            #           kwargs.get('project_domain_name', None)
            # self.endpoint_type = kwargs.get('endpoint_type', 'internalURL')
        else:
            print("The available authmethod is password for the time being")
            print("Please, provide a password credential.")

        self.auth()

    def auth(self):
        """Create a session."""
        auth = v3.Password(auth_url=self.authurl, reauthenticate=True,
                           **self.kwargs)
        self.auth_session = session.Session(auth=auth, verify=self.verify)

    def get_novaclient(self):
        if not hasattr(self, 'nova'):
            self.auth()
            self.nova = novaclient.Client('2', session=self.auth_session,
                                          endpoint_type=self.endpoint_type,
                                          insecure=self.insecure)
        return self.nova

    def get_neutronclient(self):
        if not hasattr(self, 'neutron'):
            self.auth()
            self.neutron = neutronclient.Client(
                session=self.auth_session,
                endpoint_type=self.endpoint_type,
                insecure=self.insecure
            )
        return self.neutron

    def novacomputes(self):
        nova = self.get_novaclient()
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
        nova = self.get_novaclient()
        hypervisors = nova.hypervisors.list()
        nova_hypervisors = []

        for hypervisor in hypervisors:
            nova_hypervisors.append(hypervisor.to_dict())
        return nova_hypervisors

    def neutronagents(self, hosts=[]):
        if not hosts:
            hosts = self.compute_hosts
        neutron = self.get_neutronclient()
        agents = neutron.list_agents()
        neutron_agents = []
        for agent in agents.get('agents'):
            if agent.get('host') in hosts and agent.get('binary') == \
                    'neutron-openvswitch-agent':
                neutron_agents.append(agent)

        return neutron_agents

    def evacuate(self, nodes, shared_storage=False):
        """
        Will get the hypervisors and list all running VMs on it and then start
        Evacuating one by one ...
        :param nodes: List of nodes to be evacuated !
        :param shared_storage: Boolean, True if your compute nodes are running
        under shared storage and False otherwise
        :return: List of nodes with VMs that were running on that node
        """
        nova = self.get_novaclient()
        evacuated_nodes = []
        for node in nodes:
            hypervisors = nova.hypervisors.search(node.get('host'), True)
            for hypervisor in hypervisors:
                if not hasattr(hypervisor, 'servers'):
                    break
                for server in hypervisor.servers:
                    try:
                        nova.servers.evacuate(server.get('uuid'),
                                              on_shared_storage=shared_storage)
                    except Exception as e:
                        LOG.error(e)
                host = {'host': node.get(
                    'host'), 'servers': hypervisor.servers}
                evacuated_nodes.append(host)
        return evacuated_nodes

    def set_in_maintenance(self, nodes):
        """Set compute nodes in maintenance mode."""
        nova = self.get_novaclient()
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
        """Get the authentication section."""
        auth_session = session.Session(auth=self.auth_session.auth,
                                       verify=self.verify)
        return auth_session

    def get_node_status(self, node):
        """
        Check the node nova-service status and if it's disabled or not.
        :param node: dict contains node info
        :return: True or False. True => node disabled, False => node is enabled
        or unknow status !
        """
        nova = self.get_novaclient()
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
        """Disable nova on the failing node."""
        nova = self.get_novaclient()
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
                reason='Host failed and needs to be evacuated.'
            )
            del nova
            LOG.info('Compute host: %s has been disabled to be evacuated. '
                     'Host details: %s' % (node.get('host'), str(node)))
        except Exception as e:
            LOG.error(e)
            return False
        return True

    def get_hypervisor_instances(self, node):
        """Get instances from an hypervisor."""
        nova = self.get_novaclient()
        hypervisors = nova.hypervisors.search(node.get('host'), True)
        if not hypervisors:
            return []
        return hypervisors[0].servers

    def get_hypervisor(self, node):
        """Get an instance of the hypervisor.

        :param node: dict contains host index
        :return: Hypervisor
        """
        nova = self.get_novaclient()
        hypervisors = nova.hypervisors.search(node.get('host'), True)
        if not hypervisors:
            return None
        return hypervisors[0]

    def get_instances_list(self, node):
        """Get instances running on a node for all tenants."""
        nova = self.get_novaclient()
        servers = nova.servers.list(detailed=True,
                                    search_opts={'host': node.get('host'),
                                                 'all_tenants': True})
        servers_data = []
        for server in servers:
            servers_data.append(server.to_dict())

        return servers_data

    def get_affected_tenants(self, node):
        return self.get_instances_list(node)

    def list_tenants(self):
        """List tenants."""
        auth_session = session.Session(auth=self.auth_session.auth)
        keystone = keystoneclient.Client(session=auth_session,
                                         endpoint_type=self.endpoint_type)
        projects = keystone.projects.list()

        projects_data = []
        for project in projects:
            projects_data.append(project.to_dict())

        return projects_data

    def users_on_tenant(self, tenant):
        """List user per project."""
        auth_session = session.Session(auth=self.auth_session.auth,
                                       verify=self.verify)
        keystone = keystoneclient.Client(session=auth_session,
                                         endpoint_type=self.endpoint_type,
                                         interface='internal',
                                         insecure=self.insecure)
        users = []
        try:
            users = keystone.users.list(default_project=tenant)
        except Exception as e:
            print(e)
        users_list = []
        for user in users:
            users_list.append(user.to_dict())

        return users_list

    def get_hypervisors_stats(self):
        """Get stats for all hypervisors."""
        nova = self.get_novaclient()
        stats = nova.hypervisor_stats.statistics()
        return stats.to_dict()

    def get_hypervisor_details(self, node):
        """Get details about hypervisor running on the provided node."""
        nova = self.get_novaclient()
        hypervisors = nova.hypervisors.list(detailed=True)
        for hypervisor in hypervisors:
            hypervisor = hypervisor.to_dict()
            if hypervisor.get('hypervisor_hostname') == node.get('host'):
                return hypervisor

        return None
