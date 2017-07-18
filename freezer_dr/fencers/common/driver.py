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

"""Abstract fencer"""

import abc
import six


@six.add_metaclass(abc.ABCMeta)
class FencerBaseDriver(object):

    """Abstract class that all fencer plugins.

    Should be implemented to have a unified interface and as many plugins as
    needed.
    """

    def __init__(self, nodes, fencer_conf):
        """Initialize the driver.

        Any fencer driver requires the following parameters to do the api
        calls. All these parameters can be passed from the configuration
        file in /etc/freezer/dr.conf (default).

        :param nodes: A list of failed nodes to be fenced!
        :param fencer_conf: dict contains configuration options loaded
        from the config file.
        """
        self.nodes = nodes
        self.fencer_conf = fencer_conf

    @abc.abstractmethod
    def fence(self):
        """This function to be implemented by each driver. Each driver will
        implement its own fencing logic and the manager will just load it and
        call the fence function"""

    @abc.abstractmethod
    def get_info(self):
        """Get Driver information.

        :return: dict of name, version, author, ...
        """
