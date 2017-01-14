# copyright (c) 2016 Intel, Inc.
#
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import etcd


def get_etcd_read_result(key, value):
    """Return EtcdResult object for read regular key"""
    data = {
        u'action': u'get',
        u'node': {
            u'modifiedIndex': 190,
            u'key': key,
            u'value': value
        }
    }
    return etcd.EtcdResult(**data)


def get_etcd_write_result(key, value):
    """Return EtcdResult object for write regular key"""
    data = {
        u'action': u'set',
        u'node': {
            u'expiration': u'2013-09-14T00:56:59.316195568+02:00',
            u'modifiedIndex': 183,
            u'key': key,
            u'ttl': 19,
            u'value': value
        }
    }
    return etcd.EtcdResult(**data)


def get_test_podmanager(**kwargs):
    return {
        'uuid': kwargs.get('uuid', 'ea8e2a25-2901-438d-8157-de7ffd68d051'),
        'name': kwargs.get('name', 'fake_name'),
        'url': kwargs.get('url', 'fake_url'),
        'auth': kwargs.get('auth', 'fake_auth'),
        'status': kwargs.get('size', 'fake_status'),
        'description': kwargs.get('description', 'fake_description'),
        'location': kwargs.get('location', 'fake_location'),
        'redfish_link': kwargs.get('redfish_link', 'fake_redfish_link'),
        'bookmark_link': kwargs.get('bookmark_link', 'fake_bookmark_link'),
        'created_at': kwargs.get('created_at', '2016-01-01 00:00:00 UTC'),
        'updated_at': kwargs.get('updated_at', '2016-01-01 00:00:00 UTC'),
    }


def get_test_composed_node(**kwargs):
    return {
        'uuid': kwargs.get('uuid', 'ea8e2a25-2901-438d-8157-de7ffd68d051'),
        'name': kwargs.get('name', 'fake_name'),
        'description': kwargs.get('description', 'fake_description'),
        'boot_source': kwargs.get('boot_source', 'Hdd'),
        'health_status': kwargs.get('health_status', 'OK'),
        'index': kwargs.get('index', '1'),
        'node_power_state': kwargs.get('node_power_state', 'On'),
        'node_state': kwargs.get('node_state', 'Assembling'),
        'pooled_group_id': kwargs.get('bookmark_link', 'None'),
        'target_boot_source': kwargs.get('target_boot_source', 'Hdd'),
        'links': kwargs.get(
            'links',
            [{'href': 'http://127.0.0.1:8181/v1/nodes/'
                      '7be5bc10-dcdf-11e6-bd86-934bc6947c55/',
              'rel': 'self'},
             {'href': 'http://127.0.0.1:8181/nodes/'
                      '7be5bc10-dcdf-11e6-bd86-934bc6947c55/',
              'rel': 'bookmark'}]),
        'metadata': kwargs.get(
            'metadata',
            {'memory': [{'data_width_bit': 0,
                         'speed_mhz': 2400,
                         'total_memory_mb': 8192}],
             'network': [{'ipv4': [{'address': '192.168.0.10',
                                    'gateway': '192.168.0.1',
                                    'subnet_mask': '255.255.252.0'}],
                          'mac': 'e9:47:d3:60:64:66',
                          'speed_mbps': 0,
                          'status': 'Enabled',
                          'vlans': [{'status': 'Enabled',
                                     'vlanid': 99}]}],
             'processor': [{'instruction_set': None,
                            'model': None,
                            'speed_mhz': 3700,
                            'total_core': 0}]}),
        'created_at': kwargs.get('created_at', '2016-01-01 00:00:00 UTC'),
        'updated_at': kwargs.get('updated_at', '2016-01-01 00:00:00 UTC'),
    }
