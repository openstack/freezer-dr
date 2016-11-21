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
from oslo_config import cfg
from oslo_log import log
from freezer_dr.notifiers.common.driver import NotifierBaseDriver
from freezer_dr.common.utils import load_jinja_templates
from datetime import date
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


CONF = cfg.CONF
LOG = log.getLogger(__name__)


class StandardEmail(NotifierBaseDriver):

    def __init__(self, url, username, password, templates_dir, notify_from,
                 admin_list=None, **kwargs):
        super(StandardEmail, self).__init__(url, username, password,
                                            templates_dir, notify_from,
                                            admin_list, **kwargs)
        LOG.info('Initializing StandardEmail driver @ {0}'.format(url))
        server = smtplib.SMTP(url, kwargs.get('port'))
        server.ehlo()
        if kwargs.get('tls'):
            LOG.info('TLS enabled !')
            server.starttls()
        if username and password:
            server.login(username, password)
            LOG.info('Logged in !')
        self.server = server

    def notify_status(self, node, status):
        _template = 'info.jinja'
        if status == 'success':
            _template = 'user_success.jinja'
        elif status == 'error':
            _template = 'error.jinja'

        for tenant in node.get('tenants'):
            for user in tenant.get('users'):
                if 'email' in user:
                    subject = '[' + status + '] Evacuation Status'
                    template_vars = {
                        'name': user.get('name'),
                        'tenant': tenant.get('id'),
                        'instances': tenant.get('instances'),
                        'evacuation_time': date.fromtimestamp(time.time())
                    }
                    message = load_jinja_templates(self.templates_dir,
                                                   _template, template_vars)
                    self.send_email(self.notify_from, user.get('email'),
                                    subject, html_msg=message)
        # notify administrators
        subject = 'Host Evacuation status'
        _template = 'success.jinja'
        template_vars = {
            'host': node.get('host'),
            'tenants': node.get('tenants'),
            'instances': node.get('instances'),
            'hypervisor': node.get('details'),
            'evacuation_time': date.fromtimestamp(time.time())
        }
        message = load_jinja_templates(self.templates_dir, _template,
                                       template_vars)
        self.send_email(self.notify_from, self.notify_from, subject,
                        message, self.admin_list or None)

    def send_email(self, mail_from, mail_to, subject, html_msg, cc_list=None,
                   plain_msg=None):
        LOG.info('Sending email ....')
        message = MIMEMultipart()
        message['Subject'] = subject
        message['to'] = mail_to
        if cc_list:
            message['cc'] = ', '.join(cc_list)
        message['from'] = mail_from or self.notify_from
        msg = MIMEText(html_msg, 'html')
        message.attach(msg)
        if plain_msg:
            plain_msg = MIMEText(plain_msg, 'plain')
            message.attach(plain_msg)

        try:
            self.server.sendmail(mail_from, mail_to,
                                 message.as_string())
            LOG.info('Email sent successfully !')
        except Exception as e:
            LOG.error(e)

    def notify(self, message):
        try:
            self.send_email(
                mail_from=self.notify_from,
                mail_to=self.notify_from,
                subject="[Freezer-DR] Problem Occurred",
                html_msg=message,
                cc_list=self.admin_list or []
            )
            return True
        except:
            return False

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.server.quit()



