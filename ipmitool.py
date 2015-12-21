# __author__ = 'saad'
import sys
import subprocess
from distutils import spawn


class IpmiInterface:

    _IPMI = 'ipmitool'
    _RAW_CMD = '{0} -I {1} -H {2} -U {3} -P {4} '
    _SUPPORTED_INTERFACES = ['lan', 'lanplus']

    def __init__(self, host, username, password, verbose=False,
                 interface='lanplus'):
        self._IPMI = spawn.find_executable('ipmitool')
        if not self._IPMI:
            self._IPMI = spawn.find_executable('ipmitool',
                                               path=':'.join(sys.path))
        if interface not in self._SUPPORTED_INTERFACES:
            raise Exception("Provided Interface is not supported")

        self._host = host
        self._username = username
        self._password = password
        self._verbose = verbose
        self._interface = interface

        self._update_cmd_credentials(
            host=host,
            username=username,
            password=password,
            interface=interface
        )

    def _update_cmd_credentials(self, host, username, password, interface):
        """
        Update credentials to work with different server
        :param host: IPMI IP address of the server
        :param username: IPMI username
        :param password: IPMI password
        :param interface: IPMI Interface lan, lanplus
        """
        cmd = self._RAW_CMD.format(
            self._IPMI,
            interface,
            host,
            username,
            password
        )
        self._cmd = cmd

    def get_power_status(self):
        """
        get the machine power status
        :return: 1 if the power is on and 0 if the power is off. otherwise it
        will return -1 for unknown state
        """
        cmd = self._cmd + ' chassis power status'
        output = self._process_request(cmd)
        if self._verbose:
            print "[Debug]: ", output
        if 'is on'.lower() in output.lower():
            return 1
        elif 'is off'.lower() in output.lower():
            return 0
        return -1  # power status unknown

    def power_down(self):
        """
        shutdown the machine
        """
        cmd = self._cmd + ' chassis power down'
        output = self._process_request(cmd)
        return output

    def power_reset(self):
        """
        restart the machine
        """
        cmd = self._cmd + ' chassis power reset'
        return self._process_request(cmd)

    def power_on(self):
        """
        power on the machine
        """
        cmd = self._cmd + ' chassis power on'
        return self._process_request(cmd)

    def _process_request(self, cmd):
        if self._verbose:
            print "Executing IPMI command: ", cmd

        process = subprocess.Popen(cmd, shell=True,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        output, error = process.communicate()

        if self._verbose:
            print "[Debug] Process Output: ", output
            print "[Debug] Process Error: ", error

        if process.returncode:
            raise Exception(error)
        return output

    def _custom_cmd(self, cmd):
        """
        execute custom ipmitool commands
        :param cmd: string contains the command, for credentials and interface
         you should _update_cmd_credentials to update them first
        :return: output of the command you sent or raise error
        """
        cmd = self._cmd + cmd
        return self._process_request(cmd)
