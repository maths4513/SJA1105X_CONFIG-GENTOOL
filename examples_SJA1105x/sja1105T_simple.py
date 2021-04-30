# Copyright 2017, 2021 NXP. All rights reserved.
# Disclaimer
# 1. The NXP Software/Source Code is provided to Licensee "AS IS" without any
# warranties of any kind. NXP makes no warranties to Licensee and shall not
# indemnify Licensee or hold it harmless or any reason related to the NXP
# Software/Source Code or otherwise be liable to the NXP customer. The NXP
# customer acknowledges and agrees that the NXP Software/Source Code is
# provided AS-IS and accepts all risks of utilizing the NXP Software under the
# conditions set forth according to this disclaimer.
# *
# 2. NXP EXPRESSLY DISCLAIMS ALL WARRANTIES, EXPRESS OR IMPLIED, INCLUDING, BUT
# NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
# PARTICULAR PURPOSE, AND NON-INFRINGEMENT OF INTELLECTUAL PROPERTY RIGHTS. NXP
# SHALL HAVE NO LIABILITY TO THE NXP CUSTOMER, OR ITS SUBSIDIARIES, AFFILIATES,
# OR ANY OTHER THIRD PARTY FOR ANY DAMAGES, INCLUDING WITHOUT LIMITATION,
# DAMAGES RESULTING OR ALLEGED TO HAVE RESULTED FROM ANY DEFECT, ERROR OR
# OMISSION IN THE NXP SOFTWARE/SOURCE CODE, THIRD PARTY APPLICATION SOFTWARE
# AND/OR DOCUMENTATION, OR AS A RESULT OF ANY INFRINGEMENT OF ANY INTELLECTUAL
# PROPERTY RIGHT OF ANY THIRD PARTY. IN NO EVENT SHALL NXP
# BE LIABLE FOR ANY INCIDENTAL, INDIRECT, SPECIAL, EXEMPLARY, PUNITIVE, OR
# CONSEQUENTIAL DAMAGES (INCLUDING LOST PROFITS) SUFFERED BY NXP CUSTOMER OR
# ITS SUBSIDIARIES, AFFILIATES, OR ANY OTHER THIRD PARTY ARISING OUT OF OR
# RELATED TO THE NXP SOFTWARE/SOURCE CODE EVEN IF NXP HAS BEEN ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGES

#   from UM10944 (SJA1105TEL)
#   Name                                    ID  Mandatory
#   -------------------------------------------------------------------------------
#   Schedule table                          00h no
#   Schedule Entry Points table             01h yes, if Schedule table is loaded
#   VL Lookup table                         02h no
#   VL Policing table                       03h yes, if VL Lookup table is loaded
#   VL Forwarding table                     04h yes, if VL Lookup table is loaded
#   L2 Address Lookup table                 05h no
#   L2 Policing table                       06h yes, at least one entry
#   VLAN Lookup table                       07h yes, at least the default untagging VLAN
#   L2 Forwarding table                     08h yes
#   MAC Configuration table                 09h yes
#   Schedule Parameters table               0Ah yes, if Schedule table is loaded
#   Schedule Entry Points Parameters table  0Bh yes, if Schedule table is loaded
#   VL Forwarding Parameters table          0Ch yes, if VL Forwarding table is loaded
#   L2 Lookup Parameters table              0Dh no
#   L2 Forwarding Parameters table          0Eh yes
#   Clock Synchronization Parameters table  0Fh no
#   AVB Parameters table                    10h no
#   General Parameters table                11h yes
#   Retagging table                         12h no
#   xMII Mode Parameters table              4Eh yes

############################################################################
# SJA1105T simple example configuration
#
# This is a baseline SJA1105T example
#
############################################################################

import pathlib
import site
import os

# find the current directory
current_directoy = pathlib.Path(__file__).parent.resolve()
root = current_directoy.parent
# add the modules path using site
site.addsitedir(str(root))

from ethsw import configuration as conf
import ethsw.tables_sja1105 as sja1105

NO_CBS_BLOCKS = 16
NO_ETH_PORTS = 5
NO_PRIORITIES = 8
SJA1105T_DEVICEID = 0x9e00030e

c = conf.Configuration(deviceid=SJA1105T_DEVICEID)

#############################################################################
# General Parameters
#############################################################################

general_parameters = conf.make_table_by_layout(
    sja1105.general_parameters_table_layout, sja1105.layoutid_map)
c.append(general_parameters)
general_parameters.append(
    {
        "VLLUPFORMAT": 0,
        "MIRR_PTACU": 1,  # Dynamic change of Mirror Port is enabled
        "SWITCHID": 0,
        "HOSTPRIO": 5,
        "MAC_FLTRES[0]": 0x0180C200000E,  # PTP Multicast Address
        "MAC_FLTRES[1]": 0xFFFFFFFFFFFF,
        "MAC_FLT[0]": 0xFFFFFF0000FF,
        "MAC_FLT[1]": 0x000000000000,
        "INCL_SRCPT[0]": 0,
        "INCL_SRCPT[1]": 0,
        "SEND_META[0]": 0,
        "SEND_META[1]": 0,
        "CASC_PORT": 6,
        "MIRR_PORT": 4,  # No default mirror port. Set through reconfiguration
        "HOST_PORT": 2,
        "TPID": 0x8100,
        "IGNORE2STF": 0,
        "TPID2": 0x88a8,
    })

#############################################################################
# MAC Configuration Table
#############################################################################

SPEED_HOST = 0  # speed set by host during run-time
SPEED_1GBPS = 1
SPEED_100MBPS = 2
SPEED_10MBPS = 3

speed = [SPEED_1GBPS, SPEED_1GBPS, SPEED_1GBPS, SPEED_1GBPS, SPEED_1GBPS]
speed_Mbps = [10**(4 - x) for x in speed]

default_vlan = 0  # Default VLAN ID on all ports for untagged frames is 0

queue_enable = [1, 0, 0, 0, 0, 0, 0, 0]
prio_queue0 = [0, 511]
prio_queue1 = [0, 0]
prio_queue2 = [0, 0]
prio_queue3 = [0, 0]
prio_queue4 = [0, 0]
prio_queue5 = [0, 0]
prio_queue6 = [0, 0]
prio_queue7 = [0, 0]

mac_configuration_table = conf.make_table_by_layout(
    sja1105.mac_configuration_table_layout, sja1105.layoutid_map)
c.append(mac_configuration_table)

for i in range(NO_ETH_PORTS):
    mac_configuration_table.append(
        {
            "INGRESS": 1,
            "EGRESS": 1,
            "DYN_LEARN": 1,
            "RETAG": 0,
            "DRPUNTAG": 0,
            "DRPDTAG": 0,
            "DRPNONA664": 0,
            "EGR_MIRR": 0,
            "ING_MIRR": 0,
            "VLANID": default_vlan,
            "VLANPRIO": 0,
            "TP_DELOUT": 0,
            "TP_DELIN": 0,
            "SPEED": speed[i],
            "IFG": 0,
            "ENABLED[0]": queue_enable[0],  # enable the queue
            "BASE[0]": prio_queue0[0],  # start
            "TOP[0]": prio_queue0[1],  # set the size of the queue to maximum size
            "ENABLED[1]": queue_enable[1],
            "BASE[1]": prio_queue1[0],
            "TOP[1]": prio_queue1[1],
            "ENABLED[2]": queue_enable[2],
            "BASE[2]": prio_queue2[0],
            "TOP[2]": prio_queue2[1],
            "ENABLED[3]": queue_enable[3],
            "BASE[3]": prio_queue3[0],
            "TOP[3]": prio_queue3[1],
            "ENABLED[4]": queue_enable[4],
            "BASE[4]": prio_queue4[0],
            "TOP[4]": prio_queue4[1],
            "ENABLED[5]": queue_enable[5],
            "BASE[5]": prio_queue5[0],
            "TOP[5]": prio_queue5[1],
            "ENABLED[6]": queue_enable[6],
            "BASE[6]": prio_queue6[0],
            "TOP[6]": prio_queue6[1],
            "ENABLED[7]": queue_enable[7],
            "BASE[7]": prio_queue7[0],
            "TOP[7]": prio_queue7[1]
        })

#############################################################################
# VLAN Lookup Table
#############################################################################

vlan_lookup_table = conf.make_table_by_layout(
    sja1105.vlan_lookup_table_layout, sja1105.layoutid_map)
c.append(vlan_lookup_table)

# Default VLAN
vlan_lookup_table.append(
    {
        "VING_MIRR": 0,
        "VEGR_MIRR": 0,
        "VMEMB_PORT": 0x1F,  # All ports are member of the VLAN
        "VLAN_BC": 0x1F,  # Broadcast domain for the VLAN
        "TAG_PORT": 0x00,  # Egress frames are untagged
        "VLANID": default_vlan
    })

# Enable VLANs 1 and 73
for i in [1, 73]:
    vlan_lookup_table.append(
        {
            "VING_MIRR": 0,
            "VEGR_MIRR": 0,
            "VMEMB_PORT": 0x1F,  # all ports are member
            "VLAN_BC": 0x1F,  # Broadcast domain
            "TAG_PORT": 0x1F,  # Egress frames are tagged
            "VLANID": i
        })

#############################################################################
# L2 Lookup Parameters Table
#############################################################################

l2_lookup_parameters_table = conf.make_table_by_layout(
    sja1105.l2_lookup_parameters_table_layout, sja1105.layoutid_map)
c.append(l2_lookup_parameters_table)

l2_lookup_parameters_table.append(
    {
        "MAXAGE": 0,  # No aging
        "DYN_TBSZ": 4,
        "POLY": 0x97,  # def. by Koopman: HD=4 at max. length 501
        "SHARED_LEARN": 0
    })

#############################################################################
# L2 Address Lookup Table - optional
#############################################################################

l2_address_lookup_table = conf.make_table_by_layout(
    sja1105.l2_address_lookup_table_layout, sja1105.layoutid_map)
c.append(l2_address_lookup_table)

#l2_address_lookup_table.append({
#    "VLANID"            : 0,
#    "MACADDR"           : 0x0080168A7491,
#    "DESTPORTS"         : 0x08,
#    "INDEX"             : 0x1F8,
#    "ENFPORT"           : 0})

#############################################################################
# L2 Policing Table
#############################################################################

l2_policing_table = conf.make_table_by_layout(
    sja1105.l2_policing_table_layout, sja1105.layoutid_map)
c.append(l2_policing_table)

# In this example, every port/priority is assigned a dedicated policer.
# By use of SHARINDX, multiple ports/priorities can be mapped to a single policer.

# defines the ratio of available bandwidth that is admitted for a prio/port combination in %
# a value of 100 means that no policing is performed
ratio = [
    [100, 100, 100, 100, 100, 100, 100, 100],  # Port 0 - no policing
    [100, 100, 100, 100, 100, 100, 100, 100],  # Port 1 - no policing
    [100, 100, 100, 100, 100, 100, 100, 100],  # Port 2 - no policing
    [100, 100, 100, 100, 100, 100, 100, 100],  # Port 3 - no policing
    [100, 100, 100, 100, 100, 100, 100, 100]
]  # Port 4 - no policing

for port in range(NO_ETH_PORTS):
    for prio in range(NO_PRIORITIES):
        l2_policing_table.append(
            {
                "SHARINDX": port * NO_PRIORITIES
                + prio,  # individual policing block for each priority
                "SMAX": 10 * 1526,  # Maximum burst as 10 maximum sized, double tagged frames
                "RATE": int(speed_Mbps[port] * ratio[port][prio] / 100.0 * 1000
                            / 15.625),  # Unit: [15.625 kbps]
                "MAXLEN": 1526,
                "PARTITION": prio  # memory is partitioned towards the priorities
            })

# Broadcast Storm Prevention
# Defines the ratio of available bandwidth that is admitted for a port
# ratio = [port 0, port 1, ..., port 4]
ratio = [100, 100, 100, 100, 100]  # All ports admit up to 100% broadcast traffic
for port in range(NO_ETH_PORTS):
    l2_policing_table.append(
        {
            "SHARINDX": 40 + port,  # individual policing block for each priority
            "SMAX": 10 * 1526,  # Maximum burst as 10 maximum sized, double tagged frames
            "RATE": int(speed_Mbps[port] * ratio[port] / 100.0 * 1000
                        / 15.625),  # Unit: [15.625 kbps]
            "MAXLEN": 1526,
            "PARTITION": 0  # memory is partitioned towards the priorities
        })

############################################################################
# L2 Forwarding Table
#############################################################################

l2_forwarding_table = conf.make_table_by_layout(
    sja1105.l2_forwarding_table_layout, sja1105.layoutid_map)
c.append(l2_forwarding_table)

# retain the priority of the frames at ingress
for i in range(NO_ETH_PORTS):
    if (i == general_parameters.entries[0]["HOST_PORT"]):
        reachable_ports = 0x1F  # host port is reachable by itself, needed for hybrid AVB implementation with endpoint and bridge stack on a single host
    else:
        reachable_ports = 0x1F & ~(1 << i)
    broadcast_domain = 0x1F & ~(1 << i)
    default_route = 0x1F & ~(1 << i)

    # Priority regeneration
    priority_map = [0, 1, 2, 3, 4, 5, 6, 7]  # No PCP modification

    l2_forwarding_table.append(
        {
            "FL_DOMAIN": default_route,
            "BC_DOMAIN": broadcast_domain,
            "REACH_PORT": reachable_ports,
            "VLAN_PMAP[0]": priority_map[0],
            "VLAN_PMAP[1]": priority_map[1],
            "VLAN_PMAP[2]": priority_map[2],
            "VLAN_PMAP[3]": priority_map[3],
            "VLAN_PMAP[4]": priority_map[4],
            "VLAN_PMAP[5]": priority_map[5],
            "VLAN_PMAP[6]": priority_map[6],
            "VLAN_PMAP[7]": priority_map[7]
        })

# Output PCP to queue mapping
# map priority i to queue i on all ports
for i in range(NO_PRIORITIES):
    l2_forwarding_table.append(
        {
            "VLAN_PMAP[0]": i,
            "VLAN_PMAP[1]": i,
            "VLAN_PMAP[2]": i,
            "VLAN_PMAP[3]": i,
            "VLAN_PMAP[4]": i
        })

#############################################################################
# L2 Forwarding Parameters Table
#############################################################################

l2_forwarding_parameters_table = conf.make_table_by_layout(
    sja1105.l2_forwarding_parameters_table_layout, sja1105.layoutid_map)
c.append(l2_forwarding_parameters_table)

l2_forwarding_parameters_table.append(
    {
        "MAX_DYNP": 0,
        "PART_SPC[7]": 0,
        "PART_SPC[6]": 0,
        "PART_SPC[5]": 0,
        "PART_SPC[4]": 0,
        "PART_SPC[3]": 0,
        "PART_SPC[2]": 0,
        "PART_SPC[1]": 0,
        "PART_SPC[0]": 910
    })

assert sum(
    [l2_forwarding_parameters_table.entries[0]["PART_SPC[%d]" % i]
     for i in range(8)]) <= 910, 'sum of paritions must not exceed 910 (if retagging used)'

#############################################################################
# AVB Parameters
#############################################################################

avb_parameters = conf.make_table_by_layout(
    sja1105.avb_parameters_table_layout, sja1105.layoutid_map)
c.append(avb_parameters)

avb_parameters.append({"SRCMETA": 0x026037C0FFEE, "DESTMETA": 0x026037DECADE})

#############################################################################
# MII Mode Control Parameters
#############################################################################

mii_mode_parameters = conf.make_table_by_layout(
    sja1105.mii_mode_parameters_table_layout, sja1105.layoutid_map)
c.append(mii_mode_parameters)

MII = 0
RMII = 1
RGMII = 2
UNUSED = 3

PHY_MODE = 1
MAC_MODE = 0

mii_mode_parameters.append(
    {
        "xMII_MODE[0]": RMII,
        "PHY_MAC[0]": MAC_MODE,
        "xMII_MODE[1]": RMII,
        "PHY_MAC[1]": MAC_MODE,
        "xMII_MODE[2]": RMII,
        "PHY_MAC[2]": MAC_MODE,
        "xMII_MODE[3]": RMII,
        "PHY_MAC[3]": MAC_MODE,
        "xMII_MODE[4]": RMII,
        "PHY_MAC[4]": PHY_MODE,
    })

#############################################################################
# Write out hex file
#############################################################################

filename = os.path.basename(__file__)
filename = filename.replace(".py", ".hex")

c.deviceid = SJA1105T_DEVICEID
c.to_hex(filename)

#############################################################################
# Executive Summary
#############################################################################

print("Number of bytes: %d" % (len(c.to_bytes())))
print("======================")

if c.isValid():
    print(c)
else:
    print('Error in config.')
