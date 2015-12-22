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
from osha.monitor import Monitor
import osclient

password = 'a22dQNcT'
user_id = None
username = 'admin'
auth_url = 'http://192.168.245.9:35357/v3'
project_name = 'demo'
project_id = None
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