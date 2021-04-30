# Copyright 2017-2018, 2021 NXP. All rights reserved.
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
# POSSIBILITY OF SUCH DAMAGES.

#   from UM11040 (SJA1105PQRS)
#   Name                                    ID  Mandatory                               variant
#   ---------------------------------------------------------------------------------------
#   Schedule table                          00h No                                      SJA1105Q/S
#   Schedule Entry Points Table             01h yes, if Schedule table is loaded        SJA1105Q/S
#   VL Lookup Table                         02h no                                      SJA1105Q/S
#   VL Policing table                       03h yes, if VL Lookup table is loaded       SJA1105Q/S
#   VL Forwarding Table                     04h yes, if VL Lookup table is loaded       SJA1105Q/S
#   L2 Address Lookup table                 05h no                                      all
#   L2 Policing table                       06h yes, at least one entry                 all
#   VLAN Lookup table                       07h no, by default VLAN 0 is enabled        all
#   L2 Forwarding table                     08h yes                                     all
#   MAC Configuration table                 09h yes                                     all
#   Schedule Parameters table               0Ah yes, if Schedule table is loaded        SJA1105Q/S
#   Schedule Entry Points Parameters table  0Bh yes, if Schedule table is loaded        SJA1105Q/S
#   VL Forwarding Parameters table          0Ch yes, if VL Forwarding table is loaded   SJA1105Q/S
#   L2 Lookup Parameters table              0Dh no                                      all
#   L2 Forwarding Parameters table          0Eh yes                                     all
#   Clock Synchronization Parameters table  0Fh no                                      SJA1105Q/S
#   AVB Parameters table                    10h no                                      all
#   General Parameters table                11h yes                                     all
#   Retagging table                         12h no                                      all
#   Credit-Based Shaping table              13h no                                      all
#   xMII Mode Parameters table              4Eh yes                                     all
#   CGU Config Parameters                   80h no                                      all
#   RGU Config Parameters                   81h no                                      all
#   ACU Config Parameters                   82h no                                      all
#   SGMII Config Parameters                 C8h no                                      SJA1105R/S

############################################################################
# SJA1105PQRS simple example configuration
#
# This is the adaption of the baseline SJA1105PQRS example
# to SJA1105SMBEVM switch B
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
import ethsw.tables_sja1105pqrs as sja1105pqrs

NO_CBS_BLOCKS = 16
NO_ETH_PORTS = 5
NO_PRIORITIES = 8

SJA1105QS_DEVICEID = 0xae00030e

c = conf.Configuration(deviceid=SJA1105QS_DEVICEID, validating=1)

#############################################################################
# General Parameters
#############################################################################

general_parameters = conf.make_table_by_layout(
    sja1105pqrs.general_parameters_table_layout, sja1105pqrs.layoutid_map)
c.append(general_parameters)
general_parameters.append(
    {
        "VLLUPFORMAT": 0,
        "MIRR_PTACU": 1,  # Dynamic change of Mirror Port is enabled
        "SWITCHID": 1,  # SwitchB == 1
        "HOSTPRIO": 5,
        "MAC_FLTRES[0]": 0x0180C200000E,
        "MAC_FLTRES[1]": 0x0180C2000003,
        "MAC_FLT[0]": 0xFFFFFF0000FF,
        "MAC_FLT[1]": 0xFFFFFF0000FF,
        "INCL_SRCPT[0]": 1,
        "INCL_SRCPT[1]": 1,
        "SEND_META[0]": 1,
        "SEND_META[1]": 0,
        "CASC_PORT": 4,  # cascading to SwitchA via p4
        "MIRR_PORT": 6,  # No default mirror port. Set through reconfiguration
        "HOST_PORT": 4,  # host port is reachable via SwitchA
        "VIMARKER": 0xFFFFFFFF,
        "VIMASK": 0xFFFFFFFF,
        "TPID": 0x88A8,
        "IGNORE2STF": 0,
        "TPID2": 0x8100,
        "QUEUE_TS": 0,
        "EGRMIRRVID": 0,
        "EGRMIRRPCP": 0,
        "EGRMIRRDEI": 0,
        "REPLAY_PORT": 7
    })

#############################################################################
# MAC Configuration Table
#############################################################################

SPEED_HOST = 0  # speed set by host during run-time
SPEED_1GBPS = 1
SPEED_100MBPS = 2
SPEED_10MBPS = 3

# SJA1105SMBEVM - B
# P0 - TJA1102    - RMII 100MBps
# P1 - TJA1102    - RMII 100MBps
# P2 - TJA1102    - RMII 100MBps
# P3 - TJA1102    - RMII 100MBps
# P4 - cascading  - SGMII 1000MBps
speed = [SPEED_100MBPS, SPEED_100MBPS, SPEED_100MBPS, SPEED_100MBPS, SPEED_1GBPS]
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
    sja1105pqrs.mac_configuration_table_layout, sja1105pqrs.layoutid_map)
c.append(mac_configuration_table)

for i in range(NO_ETH_PORTS):
    mac_configuration_table.append(
        {
            "INGMIRRDEI": 0,
            "INGMIRRPCP": 0,
            "INGMIRRVID": 0,
            "MIRRCETAG": 0,
            "MIRRCIE": 0,
            "INGRESS": 1,
            "EGRESS": 1,
            "DYN_LEARN": 1,
            "DRPNONA664": 0,
            "EGR_MIRR": 0,
            "ING_MIRR": 0,
            "VLANID": default_vlan,
            "VLANPRIO": 0,
            "MAXAGE": 255,
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
# Credit-Based Shaping Table
#############################################################################

# No shapers configured

#############################################################################
# VLAN Lookup Table
#############################################################################

vlan_lookup_table = conf.make_table_by_layout(
    sja1105pqrs.vlan_lookup_table_layout, sja1105pqrs.layoutid_map)
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

#############################################################################
# L2 Lookup Parameters Table
#############################################################################

l2_lookup_parameters_table = conf.make_table_by_layout(
    sja1105pqrs.l2_lookup_parameters_table_layout, sja1105pqrs.layoutid_map)
c.append(l2_lookup_parameters_table)

l2_lookup_parameters_table.append(
    {
        "LEARN_ONCE": 0,
        "OWR_DYN": 0,
        "USE_STATIC": 0,
        "NO_MGMT_LEARN": 1,
        "NO_ENF_HOSTPRT": 0,
        "DRPNOLEARN": 0,
        "START_DYNSPC": 0,
        "MAXAGE": 0,
        "MAXADDRP[0]": 1024,
        "MAXADDRP[1]": 1024,
        "MAXADDRP[2]": 1024,
        "MAXADDRP[3]": 1024,
        "MAXADDRP[4]": 1024,
        "DRPUNI": 0,
        "DRPMC": 0,
        "DRPBC": 0
    })

#############################################################################
# L2 Address Lookup Table
#############################################################################

l2_address_lookup_table = conf.make_table_by_layout(
    sja1105pqrs.l2_address_lookup_table_layout, sja1105pqrs.layoutid_map)
c.append(l2_address_lookup_table)

l2_address_lookup_table.append(
    {
        "INDEX": 0,
        "ENFPORT": 0,
        "DESTPORTS": 1 << 0,
        "MACADDR": 0x001094000099,
        "VLANID": default_vlan,
        "IOTAG": 0,
        "MASK_MACADDR": 0xFFFFFFFFFFFF,
        "MASK_VLANID": 0xFFF,
        "MASK_IOTAG": 0x1,
        "RETAG": 0,
        "MIRR": 0,
        "TAKETS": 0,
        "MIRRVLAN": 0,
        "TSREG": 0
    })

#############################################################################
# L2 Policing Table
#############################################################################

# No policing

l2_policing_table = conf.make_table_by_layout(
    sja1105pqrs.l2_policing_table_layout, sja1105pqrs.layoutid_map)
c.append(l2_policing_table)

for i in range(NO_ETH_PORTS * NO_PRIORITIES):
    l2_policing_table.append(
        {
            "SHARINDX": int(
                i / NO_PRIORITIES
            ),  #setting nSharedIdx for a given port to a single policing block for all prios
            "SMAX": 2**16 - 1,
            "RATE": 2**16 - 1,
            "MAXLEN": 1526,
            "PARTITION": 0
        })

for port in range(NO_ETH_PORTS):
    l2_policing_table.append(
        {
            "SHARINDX": 40
            + port,  #setting nSharedIdx for a given port to a single policing block for all prios
            "SMAX": 2**16 - 1,
            "RATE": 2**16 - 1,  # 1000*2**6
            "MAXLEN": 1526,
            "PARTITION": 0
        })

############################################################################
# L2 Forwarding Table
#############################################################################

l2_forwarding_table = conf.make_table_by_layout(
    sja1105pqrs.l2_forwarding_table_layout, sja1105pqrs.layoutid_map)
c.append(l2_forwarding_table)

# retain the priority of the frames at ingress
for i in range(NO_ETH_PORTS):
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

# how to map it to the egress queue: all get mapped to queue 0
for i in range(NO_PRIORITIES):
    l2_forwarding_table.append(
        {
            "VLAN_PMAP[0]": 0,
            "VLAN_PMAP[1]": 0,
            "VLAN_PMAP[2]": 0,
            "VLAN_PMAP[3]": 0,
            "VLAN_PMAP[4]": 0
        })

#############################################################################
# L2 Forwarding Parameters Table
#############################################################################

l2_forwarding_parameters_table = conf.make_table_by_layout(
    sja1105pqrs.l2_forwarding_parameters_table_layout, sja1105pqrs.layoutid_map)
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
    sja1105pqrs.avb_parameters_table_layout, sja1105pqrs.layoutid_map)
c.append(avb_parameters)

avb_parameters.append(
    {
        "SRCMETA": 0x026037C0FFEE,
        "DESTMETA": 0x026037DECADE,
        "CAS_MASTER": 0,  # SwitchB is timestamp counter Slave
        "L2CBS": 0
    })

#############################################################################
# SGMII Configuration Parameters - ignored on SJA1105PQ
#############################################################################

sgmii_configuration = conf.make_table_by_layout(
    sja1105pqrs.sgmii_configuration_table_layout, sja1105pqrs.layoutid_map)
c.append(sgmii_configuration)

sgmii_configuration.append(
    {
        "BASIC_CONTROL": 0x1140,  # 1Gbps, Aneg, FD
        "AUTONEG_ADV": 0x20,  # adv FD only
        "DIGITAL_CONTROL_1": 0x2400,  # CLOCK_STOP_EN, VSMMD1
        "AUTONEG_CONTROL": 0,
        "TEST_CONTROL": 0,  # no test patterns
        "DEBUG_CONTROL": 0,  # no debug enabled
        "DIGITAL_CONTROL_2": 0x10,  # use normal polarity
        "DIGITAL_ERROR_CNT": 0,  # no error counting
    })

#############################################################################
# MII Mode Control Parameters
#############################################################################

mii_mode_parameters = conf.make_table_by_layout(
    sja1105pqrs.mii_mode_parameters_table_layout, sja1105pqrs.layoutid_map)
c.append(mii_mode_parameters)

MII = 0
RMII = 1
RGMII = 2
UNUSED = 3
SGMII = 3

PHY_MODE = 1
MAC_MODE = 0

# SJA1105SMBEVM - B
# P0 - TJA1102    - RMII 100MBps
# P1 - TJA1102    - RMII 100MBps
# P2 - TJA1102    - RMII 100MBps
# P3 - TJA1102    - RMII 100MBps
# P4 - cascading  - SGMII 1000MBps
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
        "xMII_MODE[4]": SGMII,
        "PHY_MAC[4]": 0,  # not applicable for SGMII,
    })

#############################################################################
# Write out hex file
#############################################################################

filename = os.path.basename(__file__)
filename = filename.replace(".py", ".hex")

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
