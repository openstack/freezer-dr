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
from freezer_dr.common.utils import get_os_client, get_admin_os_client


def get_nodes_details(nodes):
    """
    Get the hypervisor details, instances running on it, tenants
    :param nodes: list of hypervisors
    :return: List of hypervisors with detailed information
    """
    nodes_details = []
    client = get_os_client()
    for node in nodes:
        instances = client.get_instances_list(node)
        tenants = set([instance.get('tenant_id') for instance in instances])
        node['instances'] = instances
        node['tenants'] = tenants
        node['details'] = client.get_hypervisor_details(node)
        nodes_details.append(node)
    nodes_details = get_users_on_tenants(nodes_details)
    return nodes_details


def get_users_on_tenants(nodes):
    """
    Lists all users that have access to a certain tenant.
    REQUIRE ADMIN PRIVILEGES !
    :param nodes: list of hypervisors
    :return: List of hypervisors with detailed tenant info
    """
    details = []
    client = get_admin_os_client()
    for node in nodes:
        if 'tenants' in node:
            tenants = []
            for tenant in node.get('tenants'):
                users = client.users_on_tenant(tenant)
                tenants.append(
                    {'id': tenant,
                     'users': users,
                     'instances': [instance for instance in
                                   node.get('instances') if
                                   instance.get('tenant_id') == tenant]})
            node['tenants'] = tenants
        details.append(node)
    return details



