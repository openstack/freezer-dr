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

    def __init__(self, nodes, evacuator_conf, fencer):
        """
        Initialize Evacuation driver with the config args
        :param nodes: A list of nodes to be evacuated!
        :param evacuator_conf: A dict of arguments that got loaded from the 
        configuration file! 
        :return: None
        """
        self.nodes = nodes
        self.evacuator_conf = evacuator_conf
        self.fencer = fencer

    @abc.abstractmethod
    def evacuate(self, enable_fencing=True):
        """Evacuate the infected node.
        :return: Two lists; the first one will be the succeeded nodes and the 
        other is the failed nodes
        """
        pass

    @abc.abstractmethod
    def get_info(self):
        """
        Get Driver Information
        :return: Dict contains driver information
        """
        pass
