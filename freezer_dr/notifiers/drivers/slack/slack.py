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

from datetime import date
from freezer_dr.notifiers.common.driver import NotifierBaseDriver
import json
from oslo_log import log
import requests
from six.moves import urllib
import time


LOG = log.getLogger(__name__)

class SlackNotifier(NotifierBaseDriver):

    MAX_CACHE_SIZE = 100
    RESPONSE_OK = 'ok'

    _raw_data_url_caches = []

    def __init__(self, url, username, password, templates_dir, notify_from,
                 admin_list=None, **kwargs):
        super(SlackNotifier, self).__init__(url, username, password,
                                            templates_dir, notify_from,
                                            admin_list, **kwargs)
        LOG.info('Initializing SlackNotifier driver @ {0}'.format(url))

        self.slack_timeout = kwargs.get('slack_timeout', '')
        self.slack_ca_certs = kwargs.get('slack_ca_certs', '')
        self.slack_insecured = kwargs.get('slack_insecured', 'True')
        self.slack_proxy = kwargs.get('slack_proxy', '')

    def _build_slack_message(self, node, status):
        """Builds slack message body
        """
        body = {
            'title': 'Host Evacuation status',
            'host': node.get('host'),
            'tenants': node.get('tenants'),
            'instances': node.get('instances'),
            'hypervisor': node.get('details'),
            'evacuation_time': date.fromtimestamp(time.time()),
            'status': status
        }
        slack_request = {}
        slack_request['text'] = json.dumps(body, indent=3)

        return slack_request

    def _check_response(self, result):
        if 'application/json' in result.headers.get('Content-Type'):
            response = result.json()
            if response.get(self.RESPONSE_OK):
                return True
            else:
                LOG.error('Received an error message when trying to send to slack. error={}'
                                .format(response.get('error')))
                return False
        elif self.RESPONSE_OK == result.text:
            return True
        else:
            LOG.error('Received an error message when trying to send to slack. error={}'
                            .format(result.text))
            return False

    def _send_message(self, request_options):
        try:
            url = request_options.get('url')
            result = requests.post(**request_options)
            if result.status_code not in range(200, 300):
                LOG.error('Received an HTTP code {} when trying to post on URL {}.'
                                .format(result.status_code, url))
                return False

            # Slack returns 200 ok even if the token is invalid. Response has valid error message
            if self._check_response(result):
                LOG.info('Notification successfully posted.')
                return True

            LOG.error('Failed to send to slack on URL {}.'.format(url))
            return False
        except Exception as err:
            LOG.error('Error trying to send to slack on URL {}. Detail: {}'
                                .format(url, err))
            return False



    def notify_status(self, node, status):
        """Notify the Host Evacuation status via slack
           Posts on the given url
        """

        slack_message = self._build_slack_message(node, status)
        address = self.url
        address = address.replace('#', '%23')

        parsed_url = urllib.parse.urlsplit(address)
        query_params = urllib.parse.parse_qs(parsed_url.query)
        url = urllib.parse.urljoin(address, urllib.parse.urlparse(address).path)

        verify = self.slack_ca_certs or not self.slack_insecured

        proxy = self.slack_proxy
        proxy_dict = None
        if proxy is not None:
            proxy_dict = {'https': proxy}

        data_format_list = ['json', 'data']
        if url in SlackNotifier._raw_data_url_caches:
            data_format_list = ['data']

        for data_format in data_format_list:
            LOG.info('Trying to send message to {} as {}'
                           .format(url, data_format))
            request_options = {
                'url': url,
                'verify': verify,
                'params': query_params,
                'proxies': proxy_dict,
                'timeout': self.slack_timeout,
                data_format: slack_message
            }
            if self._send_message(request_options):
                if (data_format == 'data' and
                        url not in SlackNotifier._raw_data_url_caches and
                        len(SlackNotifier._raw_data_url_caches) < self.MAX_CACHE_SIZE):
                    SlackNotifier._raw_data_url_caches.append(url)
                return True

            LOG.info('Failed to send message to {} as {}'
                           .format(url, data_format))
        return False

    def notify(self, message):
        pass

