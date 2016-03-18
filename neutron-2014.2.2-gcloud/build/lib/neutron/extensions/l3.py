# -*- coding:utf-8 -*-
# Copyright 2012 VMware, Inc.
# All rights reserved.
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

import abc

from oslo.config import cfg

from neutron.api import extensions
from neutron.api.v2 import attributes as attr
from neutron.api.v2 import resource_helper
from neutron.common import exceptions as qexception
from neutron.plugins.common import constants
from neutron.common import constants as com_const

# L3 Exceptions
class RouterNotFound(qexception.NotFound):
    message = _("Router %(router_id)s could not be found")
    code = "neutron_server_router_000001"


class RouterInUse(qexception.InUse):
    message = _("Router %(router_id)s still has ports")
    code = "neutron_server_router_000002"


class RouterInterfaceNotFound(qexception.NotFound):
    message = _("Router %(router_id)s does not have "
                "an interface with id %(port_id)s")
    code = "neutron_server_router_000003"


class RouterInterfaceNotFoundForSubnet(qexception.NotFound):
    message = _("Router %(router_id)s has no interface "
                "on subnet %(subnet_id)s")
    code = "neutron_server_router_000004"


class RouterInterfaceInUseByFloatingIP(qexception.InUse):
    message = _("Router interface for subnet %(subnet_id)s on router "
                "%(router_id)s cannot be deleted, as it is required "
                "by one or more floating IPs.")
    code = "neutron_server_router_000005"


class FloatingIPNotFound(qexception.NotFound):
    message = _("Floating IP %(floatingip_id)s could not be found")
    code = "neutron_server_floatingip_000001"


class ExternalGatewayForFloatingIPNotFound(qexception.NotFound):
    message = _("External network %(external_network_id)s is not reachable "
                "from subnet %(subnet_id)s.  Therefore, cannot associate "
                "Port %(port_id)s with a Floating IP.")
    code = "neutron_server_floatingip_000002"


class FloatingIPPortAlreadyAssociated(qexception.InUse):
    message = _("Cannot associate floating IP %(floating_ip_address)s "
                "(%(fip_id)s) with port %(port_id)s "
                "using fixed IP %(fixed_ip)s, as that fixed IP already "
                "has a floating IP on external network %(net_id)s.")
    code = "neutron_server_floatingip_000003"


class L3PortInUse(qexception.InUse):
    message = _("Port %(port_id)s has owner %(device_owner)s and therefore"
                " cannot be deleted directly via the port API.")
    code = "neutron_server_router_000006"


class RouterExternalGatewayInUseByFloatingIp(qexception.InUse):
    message = _("Gateway cannot be updated for router %(router_id)s, since a "
                "gateway to external network %(net_id)s is required by one or "
                "more floating IPs.")
    code = "neutron_server_router_000007"

ROUTERS = 'routers'
EXTERNAL_GW_INFO = 'external_gateway_info'
positive_int = (1, attr.UNLIMITED)

RESOURCE_ATTRIBUTE_MAP = {
    ROUTERS: {
        'id': {'allow_post': False, 'allow_put': False,
               'validate': {'type:uuid': None},
               'is_visible': True,
               'primary_key': True},
        'name': {'allow_post': True, 'allow_put': True,
                 'validate': {'type:string': None},
                 'is_visible': True, 'default': ''},
        'admin_state_up': {'allow_post': True, 'allow_put': True,
                           'default': True,
                           'convert_to': attr.convert_to_boolean,
                           'is_visible': True},
        'status': {'allow_post': False, 'allow_put': False,
                   'is_visible': True},
        'tenant_id': {'allow_post': True, 'allow_put': False,
                      'required_by_policy': True,
                      'validate': {'type:string': None},
                      'is_visible': True},
        #add by xm-2015.5.19-create_time,user_id
        'create_time': {'allow_post': False, 'allow_put': False,
                      'is_visible': True},
        'user_id': {'allow_post': False, 'allow_put': False,
                      'is_visible': True},
        'subnet_num': {'allow_post': False, 'allow_put': False,
                      'is_visible': True},
        EXTERNAL_GW_INFO: {'allow_post': True, 'allow_put': True,
                           'is_visible': True, 'default': None,
                           'enforce_policy': True,
                           'validate': {
                               'type:dict_or_nodata': {
                                   'network_id': {'type:uuid': None,
                                                  'required': True},
                                   'external_fixed_ips': {
                                       'convert_list_to':
                                       attr.convert_kvp_list_to_dict,
                                       'type:fixed_ips': None,
                                       'default': None,
                                       'required': False,
                                   }
                               }
                           }}
    },
    'floatingips': {
        'id': {'allow_post': False, 'allow_put': False,
               'validate': {'type:uuid': None},
               'is_visible': True,
               'primary_key': True},
        'floating_port_id': {'allow_post': False, 'allow_put': False,
                                'default': None,
                                 'validate': {'type:uuid': None},
                                'is_visible': True},
        'floating_ip_address': {'allow_post': True, 'allow_put': False,
                                'default': None,
                                'validate': {'type:ip_address_or_none': None},
                                'is_visible': True},
        #alter by xm-2015.6.16- 创建浮动IP时（create_floating_ip）运行指定floating_ip_address参数
        'floating_network_id': {'allow_post': True, 'allow_put': False,
                                'validate': {'type:uuid': None},
                                'is_visible': True},
        'router_id': {'allow_post': False, 'allow_put': False,
                      'validate': {'type:uuid_or_none': None},
                      'is_visible': True, 'default': None},
        'port_id': {'allow_post': True, 'allow_put': True,
                    'validate': {'type:uuid_or_none': None},
                    'is_visible': True, 'default': None,
                    'required_by_policy': True},
        'fixed_ip_address': {'allow_post': True, 'allow_put': True,
                             'validate': {'type:ip_address_or_none': None},
                             'is_visible': True, 'default': None},
        'tenant_id': {'allow_post': True, 'allow_put': False,
                      'required_by_policy': True,
                      'validate': {'type:string': None},
                      'is_visible': True},
        'status': {'allow_post': False, 'allow_put': False,
                   'is_visible': True},
        'user_id': {'allow_post': False, 'allow_put': False,
                                 'is_visible': True}, #add by luoyibing 20150901
        'type':{'allow_post':True,'allow_put':False,'is_visible':False,
                 'default': None,
                 'validate': {'type:values': com_const.EXT_NET_TYPE}},
    },
    'floatingip_qoss': {
        'floating_port_id': {'allow_post': True, 'allow_put': True,
               'validate': {'type:uuid': None},
               'is_visible': True,
               'primary_key': True},
        'max_rate':{ "allow_post":True,
                    'validate': {'type:range_or_none': positive_int},
                    "allow_put":True,
                    "is_visible":True,
                    },
        'src_ip':{ "allow_post":False,
                    "allow_put":False,
                    "is_visible":True,
                    },
        'type':{'allow_post':False,'allow_put':False,'is_visible':True,
            },
    },
}

l3_quota_opts = [
    cfg.IntOpt('quota_router',
               default=10,
               help=_('Number of routers allowed per tenant. '
                      'A negative value means unlimited.')),
    cfg.IntOpt('quota_floatingip',
               default=50,
               help=_('Number of floating IPs allowed per tenant. '
                      'A negative value means unlimited.')),
]
cfg.CONF.register_opts(l3_quota_opts, 'QUOTAS')


class L3(extensions.ExtensionDescriptor):

    @classmethod
    def get_name(cls):
        return "Neutron L3 Router"

    @classmethod
    def get_alias(cls):
        return "router"

    @classmethod
    def get_description(cls):
        return ("Router abstraction for basic L3 forwarding"
                " between L2 Neutron networks and access to external"
                " networks via a NAT gateway.")

    @classmethod
    def get_namespace(cls):
        return "http://docs.openstack.org/ext/neutron/router/api/v1.0"

    @classmethod
    def get_updated(cls):
        return "2012-07-20T10:00:00-00:00"

    @classmethod
    def get_resources(cls):
        """Returns Ext Resources."""
        plural_mappings = resource_helper.build_plural_mappings(
            {}, RESOURCE_ATTRIBUTE_MAP)
        plural_mappings['external_fixed_ips'] = 'external_fixed_ip'
        attr.PLURALS.update(plural_mappings)
        action_map = {'router': {'add_router_interface': 'PUT',
                                 'get_router_interface': 'GET',
                                 'remove_router_interface': 'PUT',
                                 'remove_router_gatewayip':'DELETE'
                                   }}
        return resource_helper.build_resource_info(plural_mappings,
                                                   RESOURCE_ATTRIBUTE_MAP,
                                                   constants.L3_ROUTER_NAT,
                                                   action_map=action_map,
                                                   register_quota=True)

    def update_attributes_map(self, attributes):
        super(L3, self).update_attributes_map(
            attributes, extension_attrs_map=RESOURCE_ATTRIBUTE_MAP)

    def get_extended_resources(self, version):
        if version == "2.0":
            return RESOURCE_ATTRIBUTE_MAP
        else:
            return {}


class RouterPluginBase(object):

    @abc.abstractmethod
    def create_router(self, context, router):
        pass

    @abc.abstractmethod
    def update_router(self, context, id, router):
        pass

    @abc.abstractmethod
    def get_router(self, context, id, fields=None):
        pass

    @abc.abstractmethod
    def delete_router(self, context, id):
        pass

    @abc.abstractmethod
    def get_routers(self, context, filters=None, fields=None,
                    sorts=None, limit=None, marker=None, page_reverse=False, offset=None):
        pass

    @abc.abstractmethod
    def add_router_interface(self, context, router_id, interface_info):
        pass

    @abc.abstractmethod
    def remove_router_interface(self, context, router_id, interface_info):
        pass

    @abc.abstractmethod
    def create_floatingip(self, context, floatingip):
        pass

    @abc.abstractmethod
    def update_floatingip(self, context, id, floatingip):
        pass

    @abc.abstractmethod
    def get_floatingip(self, context, id, fields=None):
        pass

    @abc.abstractmethod
    def delete_floatingip(self, context, id):
        pass

    @abc.abstractmethod
    def get_floatingips(self, context, filters=None, fields=None,
                        sorts=None, limit=None, marker=None,
                        page_reverse=False):
        pass

    def get_routers_count(self, context, filters=None):
        raise NotImplementedError()

    def get_floatingips_count(self, context, filters=None):
        raise NotImplementedError()

    def  get_userid_floatingips_count(self, context, filters=None):
        raise NotImplementedError()

    @abc.abstractmethod
    def  update_floatingip_qos(self,context,id,floatingip_qos):
        pass
    @abc.abstractmethod
    def  get_floatingip_qos(self,context,id, fields=None):
        pass
    @abc.abstractmethod
    def  remove_router_gatewayip(self, context, router_id):
         pass