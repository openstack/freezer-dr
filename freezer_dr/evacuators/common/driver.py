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
import abc
import six


@six.add_metaclass(abc.ABCMeta)
class EvacuatorBaseDriver(object):
    """
    Abstract class for all evacuation drivers should implement to have
    a unified interface
    """

    def __init__(self, wait, retries, **kwargs):
        """
        Initialize Evacuation driver with the config args
        :param wait: time in seconds that the evcauator should wait before
        retrying to disable the node
        :param retries: Number of times the evacuator will try to disable the
        compute node
        :param kwargs: Dict of arguments that any future driver may need to
        load it from the config file
        :return: None
        """
        self.wait = wait
        self.retries = retries
        self.options = kwargs

    @abc.abstractmethod
    def disable_node(self, node):
        """
        Disable the compute node from accepting any new VMs or requests
        :param node: dict contains node's hostname
        :return: True pr False
        """
        pass

    @abc.abstractmethod
    def is_node_disabled(self, node):
        """
        Check if node is already disabled or not
        :param node: dict contains node's hostname
        :return: True or False
        """
        pass

    @abc.abstractmethod
    def evacuate_nodes(self, nodes):
        """
        Will evacuate all running VMs on the required nodes
        :param nodes: list of nodes
        :return: list of nodes with updated status
        """
        pass

    @abc.abstractmethod
    def get_node_instances(self, node):
        """
        List instances on a compute host
        :param node: dict contains node's hostname
        :return: List contains running VMs on a given node
        """
        pass

    def get_info(self):
        """
        Get Driver Information
        :return: Dict contains driver information
        """
        pass

    @abc.abstractmethod
    def get_node_status(self, node):
        """
        Check the node status and report it
        :param node: dict contains node's hostname
        :return: dict with key 'status': 'True or False'
        """
        pass
