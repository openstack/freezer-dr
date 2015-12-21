#__author__ = 'saad'
from monitor import Monitor
import osclient

password = 'BOMrLNGHsoBb'
user_id = 'ec2548d6acb54e7ba24f479e2f3cb1a5'
username = 'admin'
auth_url = 'http://192.168.245.9:35357/v3'
project_name = 'demo'
project_id = 'f749b2874b0040aca92ea131210eb774'
user_domain_name = 'Default'
project_domain_name = 'Default'

client = osclient.OSClient(authurl=auth_url,
                           username=username,
                           password=password,
                           user_domain_name=user_domain_name,
                           project_name=project_name,
                           project_domain_name=project_domain_name,
                           endpoint_type='internal')
monitor = Monitor(client, 1)
monitor.monitor()