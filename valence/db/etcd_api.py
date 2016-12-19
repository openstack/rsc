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

"""etcd storage backend."""

import json
import logging

import etcd
from oslo_utils import uuidutils
import six

from valence import config
from valence.common import singleton
from valence.db import models


LOG = logging.getLogger(__name__)


def get_driver():
    return EtcdAPI(config.etcd_host, config.etcd_port)


def translate_to_models(etcd_resp, model_type):
    """Translate value in etcd response to models."""
    data = json.loads(etcd_resp.value)
    if model_type == models.PodManager.base_path():
        ret = models.PodManager(data)
    else:
        raise exception.InvalidParameterValue(
            _('The model_type value: %s is invalid.'), model_type)
    return ret


@six.add_metaclass(singleton.Singleton)
class EtcdAPI(object):
    """etcd API."""

    def __init__(self, host, port):
        self.client = etcd.Client(host=host, port=port)

    def create_podmanager(self, data):
        if not data.get('uuid'):
            data['uuid'] = uuidutils.generate_uuid()

        container = models.PodManager(data)
        container.save()

        return container

    def get_podmanager_by_uuid(self, podmanager_uuid):
        try:
            resp = self.client.read(models.PodManager.etcd_path(podmanager_uuid))
        except etcd.EtcdKeyNotFound:
            raise exception.ContainerNotFound(container=podmanager_uuid)

        return translate_to_models(resp, models.PodManager.base_path())

    def delete_podmanager(self, podmanager_uuid):
        podmanager = self.get_podmanager_by_uuid(podmanager_uuid)
        podmanager.delete()

    def update_podmanager(self, podmanager_uuid, values):
        podmanager = self.get_podmanager_by_uuid(podmanager_uuid)
        podmanager.update(values)

    def list_podmanager(self):
        # TODO(lin.a.yang): support filter for listing podmanager

        try:
            resp = getattr(self.client.read(models.PodManager.base_path()),
                           'children', None)
        except etcd.EtcdKeyNotFound:
            LOG.error("Path '/pod_managers' does not exist, seems etcd server "
                      "was not been initialized appropriately.")
            raise

        podmanagers = []
        for podm in resp:
            if podm.value is not None:
                podmanagers.append(translate_to_models(
                    podm, models.PodManager.base_path()))

        return podmanagers
