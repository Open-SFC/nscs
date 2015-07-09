# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2011 Nicira Networks, Inc
# All Rights Reserved.
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

"""
Crd base exception handling.
"""

from nscs.crdserver.openstack.common.exception import Error
from nscs.crdserver.openstack.common.exception import OpenstackException


class CrdException(OpenstackException):
    """Base Crd Exception

    To correctly use this class, inherit from it and define
    a 'message' property. That message will get printf'd
    with the keyword arguments provided to the constructor.

    """
    message = _("An unknown exception occurred.")


class BadRequest(CrdException):
    message = _('Bad %(resource)s request: %(msg)s')


class NotFound(CrdException):
    pass


class Conflict(CrdException):
    pass


class NotAuthorized(CrdException):
    message = _("Not authorized.")


class ServiceUnavailable(CrdException):
    message = _("The service is unavailable")


class AdminRequired(NotAuthorized):
    message = _("User does not have admin privileges: %(reason)s")


class PolicyNotAuthorized(NotAuthorized):
    message = _("Policy doesn't allow %(action)s to be performed.")


class ClassNotFound(NotFound):
    message = _("Class %(class_name)s could not be found")


class NetworkNotFound(NotFound):
    message = _("Network %(net_id)s could not be found")


class SubnetNotFound(NotFound):
    message = _("Subnet %(subnet_id)s could not be found")


class PortNotFound(NotFound):
    message = _("Port %(port_id)s could not be found")


class PolicyNotFound(NotFound):
    message = _("Policy configuration policy.json could not be found")


class StateInvalid(BadRequest):
    message = _("Unsupported port state: %(port_state)s")


class InUse(CrdException):
    message = _("The resource is inuse")


class NetworkInUse(InUse):
    message = _("Unable to complete operation on network %(net_id)s. "
                "There are one or more ports still in use on the network.")


class SubnetInUse(InUse):
    message = _("Unable to complete operation on subnet %(subnet_id)s. "
                "One or more ports have an IP allocation from this subnet.")


class PortInUse(InUse):
    message = _("Unable to complete operation on port %(port_id)s "
                "for network %(net_id)s. Port already has an attached"
                "device %(device_id)s.")


class MacAddressInUse(InUse):
    message = _("Unable to complete operation for network %(net_id)s. "
                "The mac address %(mac)s is in use.")


class HostRoutesExhausted(BadRequest):
    # NOTE(xchenum): probably make sense to use quota exceeded exception?
    message = _("Unable to complete operation for %(subnet_id)s. "
                "The number of host routes exceeds the limit %(quota)s.")


class DNSNameServersExhausted(BadRequest):
    # NOTE(xchenum): probably make sense to use quota exceeded exception?
    message = _("Unable to complete operation for %(subnet_id)s. "
                "The number of DNS nameservers exceeds the limit %(quota)s.")


class IpAddressInUse(InUse):
    message = _("Unable to complete operation for network %(net_id)s. "
                "The IP address %(ip_address)s is in use.")


class VlanIdInUse(InUse):
    message = _("Unable to create the network. "
                "The VLAN %(vlan_id)s on physical network "
                "%(physical_network)s is in use.")


class FlatNetworkInUse(InUse):
    message = _("Unable to create the flat network. "
                "Physical network %(physical_network)s is in use.")


class TunnelIdInUse(InUse):
    message = _("Unable to create the network. "
                "The tunnel ID %(tunnel_id)s is in use.")


class TenantNetworksDisabled(ServiceUnavailable):
    message = _("Tenant network creation is not enabled.")


class ResourceExhausted(ServiceUnavailable):
    pass


class NoNetworkAvailable(ResourceExhausted):
    message = _("Unable to create the network. "
                "No tenant network is available for allocation.")


class AlreadyAttached(Conflict):
    message = _("Unable to plug the attachment %(att_id)s into port "
                "%(port_id)s for network %(net_id)s. The attachment is "
                "already plugged into port %(att_port_id)s")


class SubnetMismatchForPort(Conflict):
    message = _("Subnet on port %(port_id)s does not match "
                "the requested subnet %(subnet_id)s")


class MalformedRequestBody(BadRequest):
    message = _("Malformed request body: %(reason)s")


class Invalid(Error):
    pass


class InvalidInput(BadRequest):
    message = _("Invalid input for operation: %(error_message)s.")


class InvalidAllocationPool(BadRequest):
    message = _("The allocation pool %(pool)s is not valid.")


class OverlappingAllocationPools(Conflict):
    message = _("Found overlapping allocation pools:"
                "%(pool_1)s %(pool_2)s for subnet %(subnet_cidr)s.")


class OutOfBoundsAllocationPool(BadRequest):
    message = _("The allocation pool %(pool)s spans "
                "beyond the subnet cidr %(subnet_cidr)s.")


class NotImplementedError(Error):
    pass


class MacAddressGenerationFailure(ServiceUnavailable):
    message = _("Unable to generate unique mac on network %(net_id)s.")


class IpAddressGenerationFailure(Conflict):
    message = _("No more IP addresses available on network %(net_id)s.")


class BridgeDoesNotExist(CrdException):
    message = _("Bridge %(bridge)s does not exist.")


class PreexistingDeviceFailure(CrdException):
    message = _("Creation failed. %(dev_name)s already exists.")


class SudoRequired(CrdException):
    message = _("Sudo priviledge is required to run this command.")


class QuotaResourceUnknown(NotFound):
    message = _("Unknown quota resources %(unknown)s.")


class OverQuota(Conflict):
    message = _("Quota exceeded for resources: %(overs)s")


class QuotaMissingTenant(BadRequest):
    message = _("Tenant-id was missing from Quota request")


class InvalidQuotaValue(Conflict):
    message = _("Change would make usage less than 0 for the following "
                "resources: %(unders)s")


class InvalidSharedSetting(Conflict):
    message = _("Unable to reconfigure sharing settings for network "
                "%(network)s. Multiple tenants are using it")


class InvalidExtensionEnv(BadRequest):
    message = _("Invalid extension environment: %(reason)s")


class TooManyExternalNetworks(CrdException):
    message = _("More than one external network exists")


class InvalidConfigurationOption(CrdException):
    message = _("An invalid value was provided for %(opt_name)s: "
                "%(opt_value)s")


class GatewayConflictWithAllocationPools(InUse):
    message = _("Gateway ip %(ip_address)s conflicts with "
                "allocation pool %(pool)s")
    
class InstanceNotFound(NotFound):
    message = _("Instance %(instance_id)s could not be found")


class ComputeNotFound(NotFound):
    message = _("Compute %(compute_id)s could not be found")


###Modifications by Srikanth
class ConfigurationNotFound(NotFound):
    message = _("Configuration %(config_id)s could not be found")
    
class PoolNotFound(NotFound):
    message = _("Pool %(pool_id)s could not be found")
    
class PoolMemberNotFound(NotFound):
    message = _("Pool Member %(member_id)s could not be found")

class HealthMonitorNotFound(NotFound):
    message = _("Health Monitor %(monitor_id)s could not be found")
    
class VIPNotFound(NotFound):
    message = _("Virtual IP %(vip_id)s could not be found")
    
class SessionPersistanceNotFound(NotFound):
    message = _("Sesssion Persistance %(session_id)s could not be found")
    
class PoolDeltaNotFound(NotFound):
    message = _("Pool Delta %(delta_id)s could not be found")

class PoolMemberDeltaNotFound(NotFound):
    message = _("Pool Member Delta %(delta_id)s could not be found")
    
class MonitorDeltaNotFound(NotFound):
    message = _("Health Monitor Delta %(delta_id)s could not be found")

class TooManyExternalNetworks(CrdException):
    message = _("More than one external network exists")

class VIPDeltaNotFound(NotFound):
    message = _("Virtual IP Delta %(delta_id)s could not be found")
    
class CategoryDeltaNotFound(NotFound):
    message = _("Category Delta %(delta_id)s could not be found")
    
class VendorDeltaNotFound(NotFound):
    message = _("Vendor Delta %(delta_id)s could not be found")
    
class CategoryNFDeltaNotFound(NotFound):
    message = _("Category - Network Function Delta %(delta_id)s could not be found")
    
class ImageDeltaNotFound(NotFound):
    message = _("Image Map Delta %(delta_id)s could not be found")
    
class ChainDeltaNotFound(NotFound):
    message = _("Chain Delta %(delta_id)s could not be found")
    
class ChainImageDeltaNotFound(NotFound):
    message = _("ChainImage Delta %(delta_id)s could not be found")
    
class ChainImagesNetworkDeltaNotFound(NotFound):
    message = _("Chain Images Network Delta %(delta_id)s could not be found")
###Modifications done by Veera
class CategoryNotFound(NotFound):
    message = _("Category %(category_id)s could not be found ")
    
class VendorNotFound(NotFound):
    message = _("Vendor %(vendor_id)s could not be found ")
    
class ImageNotFound(NotFound):
    message = _("Image Map %(image_id)s could not be found ")
    
class MetadataNotFound(NotFound):
    message = _("Metadata %(metadata_id)s could not be found ")
class PersonalityNotFound(NotFound):
    message = _("Personality %(personality_id)s could not be found ")
    
class ChainNotFound(NotFound):
    message = _("Chain %(chain_id)s could not be found ")
    
class Chain_imageNotFound(NotFound):
    message = _("Image Chain %(chain_image_id)s could not be found ")
    
class Chain_image_networkNotFound(NotFound):
    message = _("Image Chain  network%(chain_image_network_id)s could not be found ")
    
class Chain_image_confNotFound(NotFound):
    message = _("Image Chain  configuration%(chain_image_conf_id)s could not be found ")
    
class Chain_image_networkExist(NotFound):
    message = _("Network%(chain_image_network_id)s already mapped ")
    
class Chain_image_confExist(NotFound):
    message = _("Already %(chain_image_id)s Mapped ")
    
class NetworkfunctionNotFound(NotFound):
    message = _("Networkfunction %(networkfunction_id)s could not be found ")
    
class Category_networkfunctionNotFound(NotFound):
    message = _("Id for Category %(category_id)s Networkfunction %(networkfunction_id)s could not be found ")

class InvalidConfigurationOption(CrdException):
    message = _("An invalid value was provided for %(opt_name)s: "
                "%(opt_value)s")

class Config_handleNotFound(NotFound):
    message = _("Config_handle %(config_handle_id)s could not be found ")
    
class ChainmapNotFound(NotFound):
    message = _("Chain map %(chainmap_id)s could not be found ")

class InstanceNotFound(NotFound):
    message = _("No Instance exists for Configuration Handle Id %(config_handle_id)")

class InstanceErrorState(CrdException):
    message = _("Instance with id '%(instance_uuid)' is unable to start")

class GatewayConflictWithAllocationPools(InUse):
    message = _("Gateway ip %(ip_address)s conflicts with "
                "allocation pool %(pool)s")
class ServiceCatalogException(CrdException):
    """
    Raised when a requested service is not available in the ``ServiceCatalog``
    returned by Context.
    """
    message = _("Invalid service catalog service: %(service_name)")
    
class ChainMapNotFound(NotFound):
    message = _("Chain Map for the Chain Set %(chainset_id)s could not be found")



class NetworkVlanRangeError(CrdException):
    message = _("Invalid network VLAN range: '%(vlan_range)s' - '%(error)s'")

    def __init__(self, **kwargs):
        # Convert vlan_range tuple to 'start:end' format for display
        if isinstance(kwargs['vlan_range'], tuple):
            kwargs['vlan_range'] = "%d:%d" % kwargs['vlan_range']
        super(NetworkVlanRangeError, self).__init__(**kwargs)


class NetworkVxlanPortRangeError(CrdException):
    message = _("Invalid network VXLAN port range: '%(vxlan_range)s'")


class VxlanNetworkUnsupported(CrdException):
    message = _("VXLAN Network unsupported.")


class DuplicatedExtension(CrdException):
    message = _("Found duplicate extension: %(alias)s")


class DeviceIDNotOwnedByTenant(Conflict):
    message = _("The following device_id %(device_id)s is not owned by your "
                "tenant or matches another tenants router.")
