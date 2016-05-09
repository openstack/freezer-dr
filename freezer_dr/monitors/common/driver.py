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
class MonitorBaseDriver(object):
    """
    Abstract class that all monitoring plugins should implement to have a
    unified interface and as many plugins as we want...
    """

    def __init__(self, username, password, endpoint, **kwargs):
        """
        Initializing the driver. Any monitoring system requires the following
        parameters to call it's api. All these parameters can be passed from the
        configuration file in /etc/freezer/dr.conf
        :param username: Username
        :param password: Password
        :param endpoint: API URL
        :param kwargs: any additional parameters can be passed using this config
        option.
        """
        self.username = username
        self.password = password
        self.endpoint = endpoint
        self.kwargs = kwargs

    @abc.abstractmethod
    def get_data(self):
        """
        Gathering metrics data. making the actual api call to
        the monitoring system and get a list of nodes status.
        """
        pass

    @abc.abstractmethod
    def get_metrics(self):
        """
        return list of metrics used to monitor compute nodes. it's Optional
        not all drivers need to implement this method.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def analyze_nodes(self, nodes):
        """
        Process nodes from get_data and return list of down nodes
        :param nodes: dict of metrics of nodes { 'metric1': nodes,
        'metric2': nodes}
        :return: a list of down nodes
        """
        pass

    @abc.abstractmethod
    def process_failed(self, nodes=[], wait=0):
        """
        Double check the failed nodes again to make sure that nodes are down.
        return a list of down nodes to be passed to the evacuation tool to
        process failed hosts.
        :param nodes: a list contains pre-checked nodes to re-check them again
        :param wait: a configurable a mount of time to wait before doing this
        check to give a chance for the host to recover if there was a minor
        issue.
        :return: a list of nodes to be evacuated, the list will be passed
        directly to the evacuation tool to process them
        """
        pass

    @abc.abstractmethod
    def is_alive(self):
        """
        Plugin should provide a way to make sure that the monitoring system is
        a live or not. It's optional not all drivers need to implement it.
        :return: True or False
        """
        raise NotImplementedError()

    def get_info(self):
        """
        Get Driver information ..
        :return: dict of name, version, author, ...
        """
