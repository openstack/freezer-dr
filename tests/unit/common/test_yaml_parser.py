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

import unittest
from mock import patch

from freezer_dr.common import utils
from freezer_dr.common.osclient import OSClient


class TestUtils(unittest.TestCase):

    @patch('freezer_dr.common.utils.CONF')
    def test_os_credentials(self, mock_CONF):
        keystone_conf = dict({
            'auth_url': '',
            'password': '',
            'project_name': '',
            'user_domain_id': '',
            'project_domain_id': '',
            'project_domain_id': '',
            'user_domain_name': '',
            'kwargs': ''
        })
        mock_CONF = {'keystone_authtoken': keystone_conf}
        cred = utils.get_os_client()
        osclient_object = isinstance(cred, OSClient)
        self.assertEqual(osclient_object, True, '')
