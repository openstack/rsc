# Copyright (c) 2017 NEC, Corp.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
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

import unittest

import mock

from valence.common import exception
from valence.podmanagers import expether_manager
from valence.tests.unit.fakes import device_fakes
from valence.tests.unit.fakes import expether_fakes
from valence.tests.unit.fakes import node_fakes


class TestExpEtherManager(unittest.TestCase):

    def setUp(self):
        self.url = 'http://fake_url'
        self.expether_manager = expether_manager.ExpEtherManager('username',
                                                                 'password',
                                                                 self.url)

    @staticmethod
    def _get_compose_node_request_body():
        return {'Name': 'node4',
                'PCIDevice': [{}],
                'Processors': [{}],
                'Memory': [{}]}

    @mock.patch('valence.podmanagers.expether_manager.ExpEtherManager'
                '.sync_device_info')
    @mock.patch('valence.db.api.Connection.list_composed_nodes')
    @mock.patch('valence.podmanagers.expether_manager.ExpEtherManager.'
                '_send_request_to_eem')
    def test_compose_node(self, mock_eesv_list,
                          mock_list_composed_node,
                          mock_sync_device_info):
        mock_eesv_list.return_value = {"devices": [{"id": "1"},
                                                   {"id": "2"},
                                                   {"id": "3"},
                                                   {"id": "4"}],
                                       "timestamp": "1520845301785"}
        mock_list_composed_node.return_value = node_fakes.get_test_node_list()
        result = self.expether_manager.compose_node(
            self._get_compose_node_request_body())
        expected = {'name': 'node4', 'index': '4', 'resource_uri': 'devices/4'}
        self.assertEqual(result, expected)

    @mock.patch('valence.db.api.Connection.list_composed_nodes')
    @mock.patch('valence.podmanagers.expether_manager.ExpEtherManager.'
                '_send_request_to_eem')
    def test_compose_node_no_free_eesv(self, mock_eesv_list,
                                       mock_list_composed_node,):
        mock_eesv_list.return_value = {"devices": [{"id": "1"},
                                                   {"id": "2"},
                                                   {"id": "3"}],
                                       "timestamp": "1520845301785"}
        mock_list_composed_node.return_value = node_fakes.get_test_node_list()
        self.assertRaises(exception.ExpEtherException,
                          self.expether_manager.compose_node,
                          self._get_compose_node_request_body())

    @mock.patch('valence.podmanagers.expether_manager.ExpEtherManager.attach')
    @mock.patch('valence.db.api.Connection.list_devices')
    @mock.patch('valence.podmanagers.expether_manager.ExpEtherManager'
                '.sync_device_info')
    @mock.patch('valence.db.api.Connection.list_composed_nodes')
    @mock.patch('valence.podmanagers.expether_manager.ExpEtherManager.'
                '_send_request_to_eem')
    def test_compose_node_with_attach_pci_device(self, mock_eesv_list,
                                                 mock_list_composed_node,
                                                 mock_sync_device_info,
                                                 mock_list_devices,
                                                 mock_attach):
        mock_eesv_list.return_value = {'devices': [{'id': '1'},
                                                   {'id': '2'},
                                                   {'id': '3'},
                                                   {'id': '4'}],
                                       'timestamp': '1520845301785'}
        mock_list_composed_node.return_value = node_fakes.get_test_node_list()
        db_device = device_fakes.fake_device_list()[0]
        mock_list_devices.return_value = [db_device]
        request_body = self._get_compose_node_request_body()
        request_body['PCIDevice'] = [{'Type': 'SSD'}]
        result = self.expether_manager.compose_node(request_body)
        expected = {'name': 'node4', 'index': '4',
                    'resource_uri': 'devices/4'}
        self.assertEqual(result, expected)
        mock_sync_device_info.assert_called_once_with('4')
        mock_attach.assert_called_once_with(device_db=db_device,
                                            node_index='4')

    @mock.patch('valence.podmanagers.expether_manager.ExpEtherManager'
                '.sync_device_info')
    @mock.patch('valence.podmanagers.expether_manager.ExpEtherManager'
                '.get_node_info')
    def test_manage_node(self, mock_get_node_info, mock_sync_device_info):
        node_info = {'name': '0x1111111111',
                     'resource_uri': 'devices/0x1111111111',
                     'serial_number': 'abcd 01234',
                     'power_state': 'on',
                     'host_model': '',
                     'host_serial_number': '',
                     'index': '0x1111111111',
                     'description': 'ExpEther Board (40G)',
                     'type': '40g',
                     'mac_address': '11:11:11:11:11:11',
                     'pooled_group_id': '1234'
                     }
        mock_get_node_info.return_value = node_info
        result = self.expether_manager.manage_node('0x1111111111')
        self.assertEqual(result, node_info)
        mock_sync_device_info.assert_called_once_with('0x1111111111', '1234')

    @mock.patch('valence.podmanagers.expether_manager.ExpEtherManager'
                '._send_request_to_eem')
    def test_get_node_info(self, mock_get_eesv):
        eesv_info = expether_fakes.fake_eesv()
        mock_get_eesv.return_value = eesv_info
        result = self.expether_manager.get_node_info('0x1111111111')
        expected = {'name': '0x1111111111',
                    'resource_uri': 'devices/0x1111111111',
                    'serial_number': 'abcd 01234',
                    'power_state': 'on',
                    'host_model': '',
                    'host_serial_number': '',
                    'index': '0x1111111111',
                    'description': 'ExpEther Board (40G)',
                    'type': '40g',
                    'mac_address': '11:11:11:11:11:11',
                    'pooled_group_id': '1234'
                    }
        self.assertEqual(result, expected)

    @mock.patch('valence.podmanagers.expether_manager.ExpEtherManager'
                '._send_request_to_eem')
    def test_get_node_info_with_invalid_node(self, mock_get_eesv):
        eesv_info = expether_fakes.fake_eesv()
        eesv_info['device']['status'] = 'eeio'
        mock_get_eesv.return_value = eesv_info
        self.assertRaises(exception.ExpEtherException,
                          self.expether_manager.get_node_info,
                          '0x1111111111')

    @mock.patch('valence.podmanagers.expether_manager.ExpEtherManager'
                '._detach_all_devices_from_node')
    def test_delete_composed_node(self, mock_detach_devices):
        self.expether_manager.delete_composed_node('node_id')
        mock_detach_devices.assert_called_once_with('node_id')

    @mock.patch('valence.podmanagers.expether_manager.ExpEtherManager'
                '._detach_all_devices_from_node')
    def test_delete_composed_node_with_exception(self, mock_detach_devices):
        mock_detach_devices.side_effect = exception.ExpEtherException()
        self.assertRaises(exception.ExpEtherException,
                          self.expether_manager.delete_composed_node,
                          'node_id')

    @mock.patch('valence.podmanagers.expether_manager.ExpEtherManager.attach')
    @mock.patch('valence.db.api.Connection.get_device_by_uuid')
    def test_node_action_attach_with_resource_id(self, mock_db_device,
                                                 mock_attach):
        device_obj = device_fakes.fake_device_obj()
        mock_db_device.return_value = device_obj
        request_body = {"attach": {
            "resource_id": "00000000-0000-0000-0000-000000000000"}}
        self.expether_manager.node_action('0x12345', request_body)
        mock_attach.assert_called_once_with(device_obj.as_dict(), '0x12345')

    @mock.patch('valence.podmanagers.expether_manager.ExpEtherManager.detach')
    @mock.patch('valence.podmanagers.expether_manager.ExpEtherManager'
                '._get_device_by_mac_id')
    def test_node_action_detach_with_mac_id(self, mock_db_device,
                                            mock_detach):
        device = device_fakes.fake_device()
        mock_db_device.return_value = device
        request_body = {"detach": {"mac_id": "77:77:77:77:77:77"}}
        self.expether_manager.node_action('0x12345', request_body)
        mock_detach.assert_called_once_with(device, '0x12345')

    @mock.patch('valence.podmanagers.expether_manager.ExpEtherManager.attach')
    @mock.patch('valence.podmanagers.expether_manager.ExpEtherManager'
                '._get_device_by_device_id')
    def test_node_action_attach_with_device_id(self, mock_db_device,
                                               mock_attach):
        device = device_fakes.fake_device()
        mock_db_device.return_value = device
        request_body = {"attach": {"device_id": "0x7777777777"}}
        self.expether_manager.node_action('0x12345', request_body)
        mock_attach.assert_called_once_with(device, '0x12345')

    @mock.patch('valence.podmanagers.expether_manager.ExpEtherManager'
                '._get_device_by_device_id')
    def test_node_action_with_unsupported_action(self, mock_db_device):
        device = device_fakes.fake_device()
        mock_db_device.return_value = device
        request_body = {"run": {"device_id": "0x7777777777"}}
        self.assertRaises(exception.BadRequest,
                          self.expether_manager.node_action,
                          '0x12345', request_body)

    @mock.patch('valence.podmanagers.expether_manager.ExpEtherManager'
                '._get_device_by_mac_id')
    def test_node_action_with_non_existing_resource(self, mock_db_device):
        mock_db_device.return_value = {}
        request_body = {"attach": {"mac_id": "77:77:77:77:77:77"}}
        self.assertRaises(exception.ExpEtherException,
                          self.expether_manager.node_action,
                          '0x12345', request_body)

    @mock.patch('valence.podmanagers.expether_manager.ExpEtherManager.'
                '_send_request_to_eem')
    def test_system_list(self, mock_eesv_list):
        mock_eesv_list.return_value = expether_fakes.fake_eesv_list()
        result = self.expether_manager.systems_list()
        expected = [{'id': '0x1111111111',
                     'resource_uri': 'devices/0x1111111111',
                     'pooled_group_id': '1234',
                     'type': '40g',
                     'mac_address': '11:11:11:11:11:11',
                     },
                    {'id': '0x2222222222',
                     'resource_uri': 'devices/0x2222222222',
                     'pooled_group_id': '5678',
                     'type': '10g',
                     'mac_address': '22:22:22:22:22:22',
                     }]
        self.assertEqual(result, expected)

    @mock.patch('valence.podmanagers.expether_manager.ExpEtherManager.'
                '_send_request_to_eem')
    def test_system_list_with_exception(self, mock_eesv_list):
        mock_eesv_list.side_effect = exception.ExpEtherException()
        self.assertRaises(exception.ExpEtherException,
                          self.expether_manager.systems_list)

    @mock.patch('valence.podmanagers.expether_manager.ExpEtherManager.'
                '_send_request_to_eem')
    def test_get_system_by_id(self, mock_eesv):
        mock_eesv.return_value = expether_fakes.fake_eesv()
        result = self.expether_manager.get_system_by_id('0x1111111111')
        expected = {'id': '0x1111111111',
                    'type': '40g',
                    'pooled_group_id': '1234',
                    'mac_address': '11:11:11:11:11:11',
                    'serial_number': 'abcd 01234',
                    'name': 'eesv',
                    'power_state': 'on',
                    'host_model': '',
                    'host_serial_number': '',
                    'description': 'ExpEther Board (40G)',
                    'ee_version': 'v1.0',
                    'update_time': '2018-02-19 05:55:10'
                    }
        self.assertEqual(result, expected)

    @mock.patch('valence.podmanagers.expether_manager.ExpEtherManager.'
                '_send_request_to_eem')
    def test_get_system_by_id_with_passing_eeio_device_id(self, mock_eesv):
        system = expether_fakes.fake_eesv()
        system['device']['status'] = 'eeio'
        mock_eesv.return_value = system
        self.assertRaises(exception.ExpEtherException,
                          self.expether_manager.get_system_by_id,
                          '0x1111111111')

    @mock.patch('valence.db.api.Connection.update_device')
    @mock.patch('valence.podmanagers.expether_manager.ExpEtherManager'
                '._set_gid')
    @mock.patch('valence.podmanagers.expether_manager.ExpEtherManager.'
                '_send_request_to_eem')
    def test_attach(self, mock_req_to_eem, mock_set_gid, mock_update_device):
        input = [expether_fakes.fake_eesv(),
                 {"devices": [{"id": "0x8cdf9d911cb0"},
                              {"id": "0x8cdf9d53e9d8"}],
                  "timestamp": "1521117379726"}]
        mock_req_to_eem.side_effect = input
        device = device_fakes.fake_device()
        device['pooled_group_id'] = '4093'
        self.expether_manager.attach(device, '0x1111111111')
        mock_set_gid.assert_called_once_with(
            device_id=device['properties']['device_id'], group_id='1234')
        mock_update_device.assert_called_once_with(
            device['uuid'], {'pooled_group_id': '1234',
                             'node_id': '0x1111111111',
                             'state': 'allocated'})

    @mock.patch('valence.db.api.Connection.update_device')
    @mock.patch('valence.podmanagers.expether_manager.ExpEtherManager'
                '._del_gid')
    def test_detach(self, mock_del_gid, mock_update_device):
        device = device_fakes.fake_device()
        self.expether_manager.detach(device)
        mock_del_gid.assert_called_once_with(device['properties']['device_id'])
        mock_update_device.assert_called_once_with(
            device['uuid'], {'pooled_group_id': '4093',
                             'node_id': None,
                             'state': 'free'})

    @mock.patch('valence.podmanagers.expether_manager.ExpEtherManager.'
                '_send_request_to_eem')
    def test_set_gid(self, mock_request_to_eem):
        self.expether_manager._set_gid('dev_id', 'gid')
        mock_request_to_eem.assert_called_once_with(
            'devices/dev_id/group_id', 'put', json={'group_id': 'gid'})

    @mock.patch('valence.podmanagers.expether_manager.ExpEtherManager.'
                '_send_request_to_eem')
    def test_del_gid(self, mock_request_to_eem):
        self.expether_manager._del_gid('dev_id')
        mock_request_to_eem.assert_called_once_with(
            'devices/dev_id/group_id', 'delete')

    def test_get_device_type(self):
        result = self.expether_manager._get_device_type('0x20000')
        self.assertEqual(result, 'NIC')

    @mock.patch('valence.podmanagers.expether_manager.ExpEtherManager.detach')
    @mock.patch('valence.db.api.Connection.list_devices')
    def test_detach_all_devices_from_node(self, mock_list_devices,
                                          mock_detach):
        dev_list = device_fakes.fake_device_list()
        mock_list_devices.return_value = dev_list
        self.expether_manager._detach_all_devices_from_node('node_id')
        mock_detach.assert_has_calls([mock.call(dev_list[0]),
                                      mock.call(dev_list[1])])

    @mock.patch('valence.podmanagers.expether_manager.ExpEtherManager.'
                '_send_request_to_eem')
    def test_get_status(self, mock_request_to_eem):
        result = self.expether_manager.get_status()
        self.assertEqual(result, 'Online')
        mock_request_to_eem.assert_called_once_with('api_version')

    @mock.patch('valence.podmanagers.expether_manager.ExpEtherManager.'
                '_send_request_to_eem')
    def test_get_status_with_auth_exception(self, mock_request_to_eem):
        mock_request_to_eem.side_effect = exception.AuthorizationFailure
        self.assertRaises(exception.AuthorizationFailure,
                          self.expether_manager.get_status)

    @mock.patch('valence.podmanagers.expether_manager.ExpEtherManager.'
                '_send_request_to_eem')
    def test_get_status_with_expether_exception(self, mock_request_to_eem):
        mock_request_to_eem.side_effect = exception.ExpEtherException
        self.assertRaises(exception.ExpEtherException,
                          self.expether_manager.get_status)

    def test_system_dict(self):
        result = self.expether_manager._system_dict(
            expether_fakes.fake_eesv()['device'])
        expected = {'id': '0x1111111111',
                    'resource_uri': 'devices/0x1111111111',
                    'pooled_group_id': '1234',
                    'type': '40g',
                    'mac_address': '11:11:11:11:11:11',
                    # 'host_serial_num': device['host_serial_number'],
                    # 'host_model': device['host_model']
                    }
        self.assertEqual(result, expected)

    @mock.patch('valence.podmanagers.expether_manager.ExpEtherManager.'
                '_send_request_to_eem')
    def test_check_eeio_state(self, mock_request_to_eem):
        mock_request_to_eem.return_value = {"devices": [{"id": "012345678"}],
                                            "timestamp": "1521178770450"}
        state, eesv_id = self.expether_manager._check_eeio_state('1234')
        self.assertEqual(state, 'allocated')
        self.assertEqual(eesv_id, '012345678')

    def test_get_ironic_node_params(self):
        request_body = {"driver_info": {"ipmi_address": "xxx.xxx.xx.xx",
                                        "ipmi_username": "xxxxx",
                                        "ipmi_password": "xxxxx"},
                        "mac": "11:11:11:11:11:11",
                        "driver": "agent_ipmitool"}
        node, port = self.expether_manager.get_ironic_node_params(
            {'name': 'node1'},
            **request_body)
        expected_node = {'name': 'node1',
                         'driver': 'agent_ipmitool',
                         'driver_info': request_body['driver_info']}
        self.assertEqual(node, expected_node)
        expected_port = {'address': '11:11:11:11:11:11'}
        self.assertEqual(port, expected_port)

    def test_convert_time_format(self):
        result = self.expether_manager._convert_time_format('1518999910510')
        self.assertEqual(result, '2018-02-19 05:55:10')
