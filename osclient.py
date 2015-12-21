__author__ = 'saad'

from keystoneclient.auth.identity import v3
from keystoneclient import session
from novaclient.v2 import client as novaclient
from neutronclient.v2_0 import client as neutronclient


class OSClient:
    def __init__(self, authurl, authmethod = 'password', ** kwargs):
        """
        Provide Openstack credentials to initalize the connection to Openstack
        :param authmethod: string authmethod should be password or token but
         currently we support only password !
        :param kwargs: username, user_id, project_name, project_id,
        default_domain_id,
        """
        self.authmethod = authmethod
        self.authurl = authurl
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
        self.authSession = session.Session(auth=auth)

    def novacomputes(self):
        nova = novaclient.Client(session=self.authSession,
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
        nova = novaclient.Client(session=self.authSession,
                                 endpoint_type=self.endpoint_type)
        hypervisors = nova.hypervisors.list()
        nova_hypervisors = []

        for hypervisor in hypervisors:
            nova_hypervisors.append(hypervisor.to_dict())
        return nova_hypervisors

    def neutronagents(self, hosts=[]):
        if not hosts:
            hosts = self.compute_hosts
        new_sess = session.Session(auth=self.authSession.auth)
        neutron = neutronclient.Client(session=new_sess,
                                       endpoint_type=self.endpoint_type)
        self.authSession = new_sess
        agents = neutron.list_agents()
        neutron_agents = []
        for agent in agents.get('agents'):
                if agent.get('host') in hosts and agent.get('binary') == \
                        'neutron-openvswitch-agent':
                    neutron_agents.append(agent)

        return neutron_agents

    def evacuate(self, nodes):
        new_sess = session.Session(auth=self.authSession.auth)
        nova = novaclient.Client(session=new_sess,
                                       endpoint_type=self.endpoint_type)
        self.authSession = new_sess
        evacuated_nodes = []
        for node in nodes:
            hypervisors = nova.hypervisors.search(node, True)
            for hypervisor in hypervisors:
                host = {'host': node, 'servers': hypervisor.servers}
                evacuated_nodes.append(host)
                for server in hypervisor.servers:
                    pass
#                    output = nova.servers.evacuate(server.get('uuid'),
#                                                   on_shared_storage=True)
        return evacuated_nodes

    def set_in_maintance(self, nodes):
        new_sess = session.Session(auth=self.authSession.auth)
        nova = novaclient.Client(session=new_sess,
                                       endpoint_type=self.endpoint_type)
        self.authSession = new_sess
        for node in nodes:
            output = []
            host = nova.hosts.get(node)[0]
            values = {"maintenance_mode": "enable"}
            try:
                output.append(host.update(values))
            except Exception as e:
                print "ERROR ::: ", e
            return output
