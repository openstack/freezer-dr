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
class FencorBaseDriver(object):
    """
    Abstract class that all fencor plugins should implement to have a
    unified interface and as many plugins as we want...
    """

    def __init__(self, node_ip, node_username, node_password, **kwargs):
        """
        Initializing the driver. Any fencor driver requires the following
        parameters to do the api calls. All these parameters can be passed from
        the configuration file in /etc/osha/osha.conf (default)
        :param credentials_file: path to the credentials file
        (/etc/osha/servers.yml) ?
        :param kwargs: any additional parameters can be passed using this config
        option.
        """
        self.username = node_username
        self.password = node_password
        self.ip = node_ip
        self.kwargs = kwargs

    @abc.abstractmethod
    def graceful_shutdown(self):
        """
        Gracefully shutdown the compute node to evacuate it.
        """

    @abc.abstractmethod
    def force_shutdown(self):
        """
        Force shutdown the compute node to evacuate it. May be you can try force
        shutdown if the graceful shutdown failed
        """

    @abc.abstractmethod
    def status(self):
        """
        Get compute node status. should return 1 if on and 0 if off or
        -1 if error or unknown power status
        """

    @abc.abstractmethod
    def get_info(self):
        """
        Get Driver information ..
        :return: dict of name, version, author, ...
        """
