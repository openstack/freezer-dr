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

    def __init__(self, node, **kwargs):
        """Initialize the driver.

        Any fencer driver requires the following parameters to do the api
        calls. All these parameters can be passed from the configuration
        file in /etc/freezer/dr.conf (default).

        :param node: dict with all node details. (/etc/freezer/servers.yml) ?
        :param kwargs: any additional parameters can be passed using this
                       config option.
        """
        self.node = node
        self.kwargs = kwargs

    @abc.abstractmethod
    def graceful_shutdown(self):
        """Gracefully shutdown the compute node to evacuate it."""

    @abc.abstractmethod
    def force_shutdown(self):
        """Force shutdown the compute node to evacuate it.

        May be you can try force shutdown if the graceful shutdown failed.
        """

    @abc.abstractmethod
    def status(self):
        """Get compute node status.

        Should return 1 if on and 0 if off or -1 if error or unknown power
        status.
        """

    @abc.abstractmethod
    def get_info(self):
        """Get Driver information.

        :return: dict of name, version, author, ...
        """
