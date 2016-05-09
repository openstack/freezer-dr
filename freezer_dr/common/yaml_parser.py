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
import yaml
import os


class YamlParser(object):

    _INDEX = 'servers'

    def __init__(self, yml_file, index='servers'):
        """
        Provide Yaml file to parse it and process data
        :param yml_file: path to yaml file
        :param index: the key in the .yml file to get all servers listed under
        this key. the default 'is servers'
        """
        self.file = yml_file
        self._INDEX = index
        self.data = self.parse()

    def parse(self):
        if not self.file:
            raise Exception('No file specified !')
        if not os.path.exists(self.file) or not os.path.isfile(self.file):
            raise Exception('File desnot exists')

        stream = file(self.file, 'r')
        data = yaml.load(stream)
        return data

    def find_server_by_ip(self, ip):
        """
        get server information ilo username, password and ip
        :param ip: mgmt ip address of the server, this should be the same like
        the ip in the .yml file
        :return: dict contains server information
        """
        return self.find_server('ip-addr', ip)

    def find_server_by_hostname(self, hostname):
        """
        get server information ilo username, password and ip
        :param hostname: hostname matches one of the ones in the .yml file
        :return: dict contains the server information
        """
        return self.find_server(key='hostname', value=hostname)

    def find_server(self, key, value):
        """
        Generic function to query the .yml file to get server information by any
        key.
        :param key:
        :param value:
        :return:
        """
        for server in self.data.get(self._INDEX):
            if server.get(key) == value:
                return server

        return None
