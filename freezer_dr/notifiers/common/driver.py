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
import six
import abc


@six.add_metaclass(abc.ABCMeta)
class NotifierBaseDriver(object):
    """ Used to notify admins/users at any stage that an error happened or
    process completed or something went wrong !
    """

    def __init__(self, url, username, password, templates_dir, notify_from,
                 admin_list=None, **kwargs):
        """ Initialize the notification backend.
        :param url: Notification system backend
        :param username: Username
        :param password: Password
        :param templates_dir: Path to templates directory to load message
        templates
        :param kwargs: Key:Value arguments
        """
        self.url = url
        self.username = username
        self.password = password
        self.templates_dir = templates_dir
        self.admin_list = admin_list
        self.notify_from = notify_from
        self.options = kwargs

    @abc.abstractmethod
    def notify_status(self, node, status):
        """ Custom notification method. Can be used if you want to send custom
        notification about Tenant, Instance, or go deeper if you want
        :param node: Compute Host, Tenant, Instance, ...
        :param status: Error, Success, Info
        :return: True, False
        """
        pass

    @abc.abstractmethod
    def notify(self, message):
        """ This method will be used in different places to notify admins
        about certain problem
        :param message: String message name
        :return:
        """
        pass
