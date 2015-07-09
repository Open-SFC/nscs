# -*- encoding: utf-8 -*-
#
# Author: Purandhar Sairam Mannidi <sairam.mp@freescale.com>
#
"""
Model classes for use in the storage API.
"""

import uuid
from nscs.nscsas.storage.base import Model


class VirtualNetwork(Model):
    """
    Virtual Network details.

    :param id: UUID of the virtual network
    :param type: type of the virtual network
    :param name: The virtual network name
    :param state: virtual network admin state (active/inactive)
    :param tenant: Tenant Name to which this virtual network belongs
    :param segmentation_id: VLAN/VXLAN ID
    :param vxlan_service_port: VXLAN Service port for this network
    :param status: Virtual Network status (UP/DOWN)
    :param external: Is Virtual Network external (True/False)
    """

    def __init__(self, id, name, tenant,
                 type, segmentation_id, vxlan_service_port, status, state, external):
        Model.__init__(
            self,
            id=id,
            type=type,
            name=name,
            state=state,
            tenant=tenant,
            segmentation_id=segmentation_id,
            vxlan_service_port=vxlan_service_port,
            status=status,
            external=external,
        )


class Subnet(Model):
    """
    Subnet details.

    :param id: UUID of the subnet
    :param name: The subnet name
    :param nw_id: The virtual network UUID to which the subnet belongs
    :param dhcp: DHCP Status
    :param ip_version: IP version
    :param cidr: CIDR address of the subnet
    :param gateway_ip: Gateway IP Address
    :param pools: Allocation Pools
    :param dns_servers: DNS Server IP Addresses
    """

    def __init__(self, id, name, nw_id,
                 dhcp, ip_version, cidr, pools, dns_servers, gateway_ip=None, vnname=''):
        Model.__init__(
            self,
            id=id,
            name=name,
            nw_id=nw_id,
            dhcp=dhcp,
            ip_version=ip_version,
            cidr=cidr,
            gateway_ip=gateway_ip,
            pools=pools,
            dns_servers=dns_servers,
            vnname=vnname
        )


class Pool(Model):
    """
    Pool details.

    :param id: UUID of the Pool
    :param start: The Pool start IP address
    :param end: The Pool End IP Address
    :param subnet_id: Subnet UUID to which this pool belongs
    """

    def __init__(self, id, start, end, subnet_id):
        Model.__init__(
            self,
            id=id,
            start=start,
            end=end,
            subnet_id=subnet_id
        )


class VirtualMachine(Model):
    """
    Virtual Machine Details

    :param id: Virtual Machine UUID
    :param name: Virtual Machine Name
    :param state: Virtual Machine State
    :param tenant: Tenant ID to which the virtual machine belongs
    :param created_at: virtual machine created time
    :param launched_at: virtual machine launched time
    :param host: Compute Node address / IP where the virtual Machine is brought up
    :param user_id: User ID who created the virtual machine
    :param reservation_id:
    :param state_description: Virtual machine state description
    """
    def __init__(self, id, name, state, tenant, created_at, host, type,
                 user_id, reservation_id, state_description='', launched_at=None):
        Model.__init__(
            self,
            id=id,
            name=name,
            state=state,
            tenant=tenant,
            created_at=created_at,
            launched_at=launched_at,
            host=host,
            user_id=user_id,
            reservation_id=reservation_id,
            state_description=state_description,
            type=type
        )


class Port(Model):
    """
    Port Details

    :param id: Port UUID
    :param name: Port Name
    :param state: Port admin State (True / False)
    :param tenant: Tenant ID to which the port belongs
    :param type: port type
    :param host: Compute Node address / IP where the virtual Machine is brought up
    :param mac_address: User ID who created the virtual machine
    :param ip_address:
    :param status: Port status (active / inactive)
    :param device_owner: compute Node name
    :param security_groups: Security Group UUIDs to be applied on this port
    :param subnet_id: Subnet UUID of this Port
    :param nw_id: Virtual Network UUID
    :param device_id: Virtual Machine ID to which this port belongs
    """
    def __init__(self, id, name, state, tenant, type,
                 mac_address, status, device_owner, ip_address,
                 subnet_id, nw_id, device_id, security_groups=[], bridge=None):
        Model.__init__(
            self,
            id=id,
            name=name,
            state=state,
            tenant=tenant,
            bridge=bridge,
            type=type,
            mac_address=mac_address,
            ip_address=ip_address,
            status=status,
            device_owner=device_owner,
            device_id=device_id,
            security_groups=security_groups,
            subnet_id=subnet_id,
            nw_id=nw_id
        )


class Domain(Model):
    """
    Domain Details

    :param id: Domain UUID
    :param name: Domain Name
    :param subject: Domain Subject name
    """

    def __init__(self, name, id=None, subject='', ttp_name='openstack'):
        if not id:
            id = str(uuid.uuid4())
        Model.__init__(self, id=id, name=name, subject=subject, ttp_name=ttp_name)


class Switch(Model):
    """
    Switch Details

    :param id: Switch UUID
    :param name: Switch Name
    :param fqdn: Switch FQDN
    :param type: Switch Type (Physical / Virtual)
    :param baddr: Is Switch Binary IPv4 / IPv6 Address
    :param ip_address: Switch IP Address
    """
    def __init__(self, name, fqdn, type=False, baddr=False, ip_address='', id=None):
        if not id:
            id = str(uuid.uuid4())
        Model.__init__(
            self,
            id=id,
            name=name,
            fqdn=fqdn,
            type=type,
            baddr=baddr,
            ip_address=ip_address
        )


class Datapath(Model):
    """
    Datapath Details

    :param id: Datapath ID
    :param subject: Datapath subject
    :param switch: Switch UUID
    :param domain: Domain UUID
    :param switchname: Switch name
    :param domainname: Domain name
    """
    def __init__(self, id, name, subject, switch, domain, switchname='', domainname=''):
        Model.__init__(
            self,
            id=id,
            name=name,
            subject=subject,
            switch=switch,
            domain=domain,
            switchname=switchname,
            domainname=domainname
        )


class NWPort(Model):
    """
    Network Side Port Details

    """
    def __init__(self, id, name, network_type, data_ip,
                 bridge, vxlan_vni, vxlan_port, ip_address,
                 flow_type, ovs_port, local_data_ip,host):
        Model.__init__(
            self,
            id=id,
            name=name,
            network_type=network_type,
            data_ip=data_ip,
            bridge=bridge,
            vxlan_vni=vxlan_vni,
            vxlan_port=vxlan_port,
            ip_address=ip_address,
            #vlan_id=vlan_id,
            flow_type=flow_type,
            ovs_port=ovs_port,
            local_data_ip=local_data_ip,
            host=host,
        )
