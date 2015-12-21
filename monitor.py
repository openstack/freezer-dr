#__author__ = 'saad'
from time import sleep


class Monitor(object):
    def __init__(self, client, wait):
        self.client = client
        self.wait = wait

    def get_down_nodes(self):
        # list all down nova compute
        nova_down = self.is_nova_service_down()
        # list all down hypervisors
        hypervisor_down = self.is_hpyervisor_down()
        # list all down openvswitch agents
        agents_down = self.is_neutron_agents_down()

        nodes_down = []
        for node in nova_down:
            if node in hypervisor_down and node in agents_down:
                nodes_down.append(node)
        return nodes_down

    def monitor(self):
        nodes_down = self.get_down_nodes()
        nodes_to_evacuate = []
        if nodes_down:
            nodes_to_evacuate = self.process_failed_nodes(nodes_down)

        evacuated_nodes = []
        if nodes_to_evacuate:
            evacuated_nodes = self.evacuate(nodes_to_evacuate)
        if not evacuated_nodes:
            raise "Error: node didn't evacuated !", nodes_to_evacuate

        self.notify(evacuated_nodes)

    # @todo needs to be implemented !
    def notify(self, nodes):
        print "These nodes %s Evacuated" % nodes[0]['host']
        print nodes
        """
        will be used to notify the admins that there is something went wrong !
        """
        pass

    def evacuate(self, nodes):
        # @todo add shutdown process
        # maintence mode not working with libvirt
        # self.client.set_in_maintance(nodes)
        evacuated = self.client.evacuate(nodes)
        return evacuated

    def process_failed_nodes(self, nodes):
        sleep(self.wait)
        nodes_down = self.get_down_nodes()
        to_be_evacuated = []
        for node in nodes_down:
            if node in nodes:
                to_be_evacuated.append(node)

        return to_be_evacuated

    def is_hpyervisor_down(self):
        hypervisors = self.client.novahypervisors()
        down_hosts = []
        for hypervisor in hypervisors:
            if hypervisor.get('state') == 'down':
                host = {}
                host['host'] = hypervisor.get('service').get('host')
                down_hosts.append(hypervisor.get('service').get('host'))

        return down_hosts

    def is_nova_service_down(self):
        computes = self.client.novacomputes()
        down_hosts = []
        for node in computes:
            if node.get('state') == 'down' and node.get('status') == 'enabled':
                down_hosts.append(node.get('host'))
        return down_hosts

    def is_neutron_agents_down(self):
        agents = self.client.neutronagents()
        down_hosts = []
        for agent in agents:
            if agent.get('admin_state_up') and not agent.get('alive'):
                down_hosts.append(agent.get('host'))

        return down_hosts
