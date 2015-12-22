# __author__ = 'saad'
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
            raise "No file specified !"
        if not os.path.exists(self.file) or not os.path.isfile(self.file):
            raise "File desn't exists"

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