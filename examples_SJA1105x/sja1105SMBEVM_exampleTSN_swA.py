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
# SJA1105PQ example configuration
#
# This is an example showcasing many of the configuration possibilities.
# This includes
# * Example CBS configuration on port 0
# * An example policer setup with policing on port 1 and 2
# * Port speed and MII mode parameters
# * MAC filtering configuration for gPTP
# * Examples of ARL and VLAN table configuration
#
############################################################################

import pathlib
import site
import os
import math

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
        "SWITCHID": 0,  # SwitchA == 0
        "HOSTPRIO": 5,
        "MAC_FLTRES[0]": 0x0180C200000E,  # PTP Multicast Address
        "MAC_FLTRES[1]": 0x0180C2000003,  # EAPOL Multicast Address (for 802.1X)
        "MAC_FLT[0]": 0xFFFFFF0000FF,
        "MAC_FLT[1]": 0xFFFFFF0000FF,
        "INCL_SRCPT[0]": 1,
        "INCL_SRCPT[1]": 1,
        "SEND_META[0]": 1,
        "SEND_META[1]": 0,
        "CASC_PORT": 4,  # cascading to SwitchB via p4
        "MIRR_PORT": 6,  # No default mirror port. Set through reconfiguration
        "HOST_PORT": 0,  # host is Calypso on p0
        "VIMARKER": 0x00109400,  # criterion for critical traffic when VLLUPFORMAT = 1
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

# SJA1105SMBEVM - A
# P0 - Calypso    - MII 100MBps
# P1 - TJA1102S   - RMII 100MBps
# P2 - KSZ9031    - RGMII 1000MBps  - ANEG
# P3 - KSZ9031    - RGMII 1000MBps  - ANEG
# P4 - cascading  - SGMII 1000MBps
speed = [SPEED_100MBPS, SPEED_100MBPS, SPEED_HOST, SPEED_HOST, SPEED_1GBPS]
speed_Mbps = [10**(4 - x) if x > 0 else 1000 for x in speed]

default_vlan = 555  # Default VLAN ID on all ports for untagged frames is 555

queue_enable = [1, 1, 1, 1, 1, 1, 1, 1]
prio_queue0 = [0, 63]
prio_queue1 = [64, 127]
prio_queue2 = [128, 191]
prio_queue3 = [192, 255]
prio_queue4 = [256, 319]
prio_queue5 = [320, 383]
prio_queue6 = [384, 447]
prio_queue7 = [448, 511]

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

credit_based_shaping_table = conf.make_table_by_layout(
    sja1105pqrs.credit_based_shaping_table_layout, sja1105pqrs.layoutid_map)
c.append(credit_based_shaping_table)

# bandwidth given in Mbit/s
# Example configuration for 4 shapers in port 0
shapers = [
    {
        "bandwidth": 0.5,
        "prio": 7,
        "port": 0
    }, {
        "bandwidth": 5,
        "prio": 6,
        "port": 0
    }, {
        "bandwidth": 10,
        "prio": 5,
        "port": 0
    }, {
        "bandwidth": 20,
        "prio": 4,
        "port": 0
    }
]

assert len(shapers) <= NO_CBS_BLOCKS, "No of shapers configured exceeds %d" % (NO_CBS_BLOCKS)

for shaper in shapers:
    idle_slope = shaper["bandwidth"] / 8.0 * 10**6  # conversion from Mbit/s to byte/s
    rate = speed_Mbps[shaper["port"]] / 8.0 * 10**6  # rate at the port in byte/s
    send_slope = rate - idle_slope
    credit_based_shaping_table.append(
        {
            "IDLE_SLOPE": int(idle_slope),
            "SEND_SLOPE": int(send_slope),
            "CREDIT_HI": 0x7FFFFFFF,
            "CREDIT_LO": 0x7FFFFFFF,
            "CBS_PRIO": shaper["prio"],
            "CBS_PORT": shaper["port"]
        })

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

# Enable VLANs 0 to 15
for i in range(16):
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
        "MACADDR": 0x001094000001,
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

l2_policing_table = conf.make_table_by_layout(
    sja1105pqrs.l2_policing_table_layout, sja1105pqrs.layoutid_map)
c.append(l2_policing_table)

# In this example, every port/priority is assigned a dedicated policer.
# By use of SHARINDX, multiple ports/priorities can be mapped to a single policer.

# defines the rate in Mbit/s for a prio/port combination
allowed_mbps = [
    [100, 100, 100, 100, 100, 100, 100, 100],  # Port 0 - no policing
    [100, 10, 10, 10, 10, 10, 10, 10],  # Port 1 - 10Mbps for at each prio, except prio 0
    [1000, 0, 0, 0, 0, 0, 0, 0],  # Port 2 - only lowest prio allowed
    [1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000],  # Port 3 - no policing
    [1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000]
]  # Port 4 - no policing

for port in range(NO_ETH_PORTS):
    for prio in range(NO_PRIORITIES):
        l2_policing_table.append(
            {
                "SHARINDX": port * NO_PRIORITIES
                + prio,  # individual policing block for each priority
                "SMAX": 10 * 1526,  # Maximum burst as 10 maximum sized, double tagged frames
                "RATE": int(allowed_mbps[port][prio] * 64),  # Unit: [15.625 kbps]
                "MAXLEN": 1526,
                "PARTITION": prio  # memory is partitioned towards the priorities
            })

# Broadcast Storm Prevention
# Defines the ratio of available bandwidth that is admitted for a port
# ratio = [port 0, port 1, ..., port 4]
allowed_mbps = [100, 100, 1000, 1000, 1000]  # All ports admit up to 100% broadcast traffic
for port in range(NO_ETH_PORTS):
    l2_policing_table.append(
        {
            "SHARINDX": 40 + port,  # individual policing block for each priority
            "SMAX": 10 * 1526,  # Maximum burst as 10 maximum sized, double tagged frames
            "RATE": int(allowed_mbps[port] * 64),  # Unit: [15.625 kbps]
            "MAXLEN": 1526,
            "PARTITION": 0  # memory is partitioned towards the priorities
        })

############################################################################
# L2 Forwarding Table
#############################################################################

l2_forwarding_table = conf.make_table_by_layout(
    sja1105pqrs.l2_forwarding_table_layout, sja1105pqrs.layoutid_map)
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
    sja1105pqrs.l2_forwarding_parameters_table_layout, sja1105pqrs.layoutid_map)
c.append(l2_forwarding_parameters_table)

l2_forwarding_parameters_table.append(
    {
        "MAX_DYNP": 0,
        "PART_SPC[7]": 88,
        "PART_SPC[6]": 88,
        "PART_SPC[5]": 88,
        "PART_SPC[4]": 88,
        "PART_SPC[3]": 88,
        "PART_SPC[2]": 88,
        "PART_SPC[1]": 88,
        "PART_SPC[0]": 198
    })

assert sum(
    [l2_forwarding_parameters_table.entries[0]["PART_SPC[%d]" % i]
     for i in range(8)]) <= 910, 'sum of paritions must not exceed 910 (if retagging used)'

#############################################################################
# Schedule Table (Time Aware Shaper)
#############################################################################

schedule_table = conf.make_table_by_layout(
    sja1105pqrs.schedule_table_layout, sja1105pqrs.layoutid_map)
c.append(schedule_table)

cycle_time = 0.1  # cycle time of the TAS schedule in seconds (s)

CLSD = 1
OPEN = 0

# gate control list (per port)
# time_interval: Time in seconds (s) for which the gate action is defined
# gate_control: List of gate state open/closed for each priority (0-7)
# beware: due to HW contraints, DIFFERENT gate state actions for more than one port at the same time are NOT allowed
# however: IDENTICAL gate state actions (same patterns of OPEN/CLSD actions for the ports) at the same time ARE allowed
# in case of a conflict, try to shift the action time for the ports
#

gate_control_list_per_port = [
    [ # Port 0
        {"time_interval": 0.010, "gate_control": [OPEN, OPEN, OPEN, OPEN, CLSD, CLSD, CLSD, CLSD]},
        {"time_interval": 0.050, "gate_control": [CLSD, CLSD, CLSD, CLSD, OPEN, OPEN, OPEN, OPEN]}
    ],
    [ # Port 1
        {"time_interval": 0.020, "gate_control": [OPEN, OPEN, OPEN, OPEN, CLSD, CLSD, CLSD, CLSD]},
        {"time_interval": 0.030, "gate_control": [CLSD, CLSD, CLSD, CLSD, OPEN, OPEN, OPEN, OPEN]}
    ],
    [ # Port 2
        {"time_interval": 0.011, "gate_control": [CLSD, CLSD, CLSD, CLSD, CLSD, CLSD, CLSD, OPEN]},
        {"time_interval": 0.011, "gate_control": [CLSD, CLSD, CLSD, CLSD, CLSD, CLSD, OPEN, CLSD]},
        {"time_interval": 0.011, "gate_control": [CLSD, CLSD, CLSD, CLSD, CLSD, OPEN, CLSD, CLSD]},
        {"time_interval": 0.011, "gate_control": [CLSD, CLSD, CLSD, CLSD, OPEN, CLSD, CLSD, CLSD]},
        {"time_interval": 0.011, "gate_control": [CLSD, CLSD, CLSD, OPEN, CLSD, CLSD, CLSD, CLSD]},
    ],
    [ # Port 3
        # not gate actions (all open)
    ],
    [ # Port 4
        # not gate actions (all open)
    ]
]

# Calculations below use ns as timebase to avoid floating point precision issues.
cycle_time = cycle_time * 1000000000

# compile a global gate control list
gate_control_list = list()

for port in range(NO_ETH_PORTS):
    time = 0
    for entry_ix, entry in enumerate(gate_control_list_per_port[port]):
        new_gate_control_entry = True
        entry["time_interval"] = entry["time_interval"] * 1000000000
        time = time + entry["time_interval"]
        for gate_control_entry in gate_control_list:
            if gate_control_entry["time"] == time:
                # An entry at the same point in time already exists. Merge them.
                assert gate_control_entry["gate_control"] == entry[
                    "gate_control"], "Illegal schedule configured (Multiple conflicting gate actions at the same time instance), time: %f s" % entry[
                        "time_interval"]
                gate_control_entry["ports"] = gate_control_entry["ports"] + (1 << port)
                new_gate_control_entry = False
                break
        if new_gate_control_entry == True:
            gate_control_list.append(
                {
                    "time": time,
                    "gate_control": entry["gate_control"],
                    "ports": 1 << port,
                    "time_interval": entry["time_interval"]
                })

# Sort the list with respect to absolute time
gate_control_list = sorted(gate_control_list, key=lambda k: k["time"])

# If needed, add final entry to make sure the cycle time is correct
assert gate_control_list[-1][
    "time"] <= cycle_time, "Schedule exceeds the configured cycle time (actual time required is %f)" % gate_control_list[
        -1]["time"]
if gate_control_list[-1]["time"] < cycle_time:
    # Add dummy to schedule table (no gate action) to conclude the cycle
    gate_control_list.append(
        {
            "time": cycle_time,
            "gate_control": gate_control_list[-1]["gate_control"],
            "ports": 0,
            "time_interval": cycle_time - gate_control_list[-1]["time"]
        })

# Fill with dummy entries (no change) if delta is too large
MAX_DELTA = (2**18 - 1) * 200  # maximum value in seconds (ns)

gate_control_list_dummies = list()
for entry_ix, entry in enumerate(gate_control_list):
    dummies_needed = int(math.floor(entry["time_interval"] / MAX_DELTA))
    if dummies_needed > 0:
        for i in range(dummies_needed):
            gate_control_list_dummies.append(
                {
                    "time_interval": MAX_DELTA,
                    "time": entry["time"] - (MAX_DELTA * i),
                    "gate_control": entry["gate_control"],
                    "ports": 0
                })
        entry["time_interval"] = entry["time_interval"] - (MAX_DELTA * dummies_needed)

gate_control_list = gate_control_list + gate_control_list_dummies  # append dummies
gate_control_list = sorted(gate_control_list, key=lambda k: k["time"])  # sort again

# Compile actual table to be used in the switch
ENTRY_ENABLED = 1 << 8
for entry in gate_control_list:
    resmedia = sum([(entry["gate_control"][i] << i) for i in range(NO_PRIORITIES)]) \
               + ENTRY_ENABLED

    schedule_table.append(
        {
            "DELTA": int(entry["time_interval"] / 200.0),  # convert to multiple of 200 ns
            "RESMEDIA": resmedia,
            "DESTPORTS": entry["ports"],
        })

#############################################################################
# Schedule Entry Points Table (Time Aware Shaper)
#############################################################################

schedule_entry_points_table = conf.make_table_by_layout(
    sja1105pqrs.schedule_entry_points_table_layout, sja1105pqrs.layoutid_map)
c.append(schedule_entry_points_table)

schedule_entry_points_table.append(
    {
        "ADDRESS": 0,
        "DELTA": 1,  # start after 200 us (500*200 ns)
        "SUBSCHINDX": 0
    })

#############################################################################
# Schedule Entry Points Parameters (Time Aware Shaper)
#############################################################################

schedule_entry_points_parameters = conf.make_table_by_layout(
    sja1105pqrs.schedule_entry_points_parameters_table_layout, sja1105pqrs.layoutid_map)
c.append(schedule_entry_points_parameters)

schedule_entry_points_parameters.append(
    {
        "ACTSUBSCH": 0,  # number of active subschedules minus one
        "CLKSRC": 3  # 3 corresponds to the gPTP clock
    })

#############################################################################
# Schedule Parameters (Time Aware Shaper)
#############################################################################

schedule_parameters = conf.make_table_by_layout(
    sja1105pqrs.schedule_parameters_table_layout, sja1105pqrs.layoutid_map)
c.append(schedule_parameters)

schedule_parameters.append(
    {
        "SUBSCHEIND[0]": len(schedule_table) - 1  # Only one schedule, executed till the end
    })

#############################################################################
# VL Lookup Table (Stream Policing)
#############################################################################

assert general_parameters.entries[0][
    "VLLUPFORMAT"] == 0, "Using vl_lookup_table_layout_0, but VLLUPFORMAT %d ( != 0)" % general_parameters.entries[
        0]["VLLUPFORMAT"]

# For now empty, see Qci section
vl_lookup_table = conf.make_table_by_layout(
    sja1105pqrs.vl_lookup_table_layout_0, sja1105pqrs.layoutid_map)
c.append(vl_lookup_table)

#############################################################################
# VL Policing Table (Stream Policing)
#############################################################################

# For now empty, see Qci section
rc_vl = conf.make_table_by_layout(sja1105pqrs.rc_vl_layout, sja1105pqrs.layoutid_map)
c.append(rc_vl)

#############################################################################
# VL Forwarding Table (Stream Policing)
#############################################################################

# For now empty, see Qci section
vl_forwarding_table = conf.make_table_by_layout(
    sja1105pqrs.vl_forwarding_table_layout, sja1105pqrs.layoutid_map)
c.append(vl_forwarding_table)

#############################################################################
# 802.1Qci Helper
#############################################################################


def add_qci_entry(
        mac, in_vlanid, in_ports, in_vlanprio, max_len, max_rate, max_jitter, egress_ports,
        egress_prio, partition):

    vl_lookup_entry = {
        "ISCRITICAL": 1,
        "MACADDR": mac,
        "VLANID": in_vlanid,
        "PORT": in_ports,
        "VLANPRIO": in_vlanprio
    }

    vl_policer_entry = {
        "JITTER": int(max_jitter / 10),  # in multiples of 10 us: 0.2ms
        "BAG": int(math.ceil(((max_len * 8 * 10000.) / max_rate))),  # in multiples of 100 us
        "SHARINDX": 0,
        "MAXLEN": max_len
    }

    vl_forwarding_table_entry = {
        "DESTPORTS": egress_ports,  # Port 2
        "PARTITION": partition,
        "PRIORITY": egress_prio,
        "TYPE": 0
    }  # Rate constraint traffic

    return (vl_lookup_entry, vl_policer_entry, vl_forwarding_table_entry)


def qci_add_to_table(qci_entries):

    # Sort the VL lookup table as per usermanual
    sort_key = lambda x: (x[0]['MACADDR'], x[0]['VLANID'], x[0]['PORT'], x[0]['VLANPRIO'])
    qci_entries = sorted(qci_entries, key=sort_key)

    for idx, val in enumerate(qci_entries):
        vl_lookup_entry, vl_policer_entry, vl_forwarding_table_entry = val
        vl_policer_entry['SHARINDX'] = idx

        rc_vl.append(vl_policer_entry)
        vl_lookup_table.append(vl_lookup_entry)
        vl_forwarding_table.append(vl_forwarding_table_entry)


#############################################################################
# 802.1Qci Entries
#############################################################################

qci_entries = list()

qci_entries.append(
    add_qci_entry(
        mac=0x001094000001,
        in_vlanid=5,  # ingress vlan
        in_ports=1,  # ingress ports
        in_vlanprio=2,  # ingress pcp
        max_len=128,  #max frame size in bytes
        max_rate=200000,  #rate in Bit/s
        max_jitter=20,  # jitter in us
        egress_ports=(1 << 1),  # forwarding vector
        egress_prio=2,  # egress prio (queue)
        partition=0))  # VL parition from which the memory is drawn

qci_entries.append(
    add_qci_entry(
        mac=0x001094000002,
        in_vlanid=5,
        in_ports=1,
        in_vlanprio=2,
        max_len=128,
        max_rate=200000,
        max_jitter=20,
        egress_ports=(1 << 1),
        egress_prio=2,
        partition=0))

qci_add_to_table(qci_entries)

#############################################################################
# VL Forwarding Parameters Table (Stream Policing)
#############################################################################

vl_forwarding_parameters_table = conf.make_table_by_layout(
    sja1105pqrs.vl_forwarding_parameters_table_layout, sja1105pqrs.layoutid_map)
c.append(vl_forwarding_parameters_table)

# current configuration allows one maximum sized frame in each partition
vl_forwarding_parameters_table.append(
    {
        "DEBUGEN": 1,
        "PART_SPC[7]": 12,
        "PART_SPC[6]": 12,
        "PART_SPC[5]": 12,
        "PART_SPC[4]": 12,
        "PART_SPC[3]": 12,
        "PART_SPC[2]": 12,
        "PART_SPC[1]": 12,
        "PART_SPC[0]": 12
    })

assert sum([l2_forwarding_parameters_table.entries[0]["PART_SPC[%d]" % i] for i in range(8)]) + \
       sum([vl_forwarding_parameters_table.entries[0]["PART_SPC[%d]" % i] for i in range(8)]) <= 910,\
       'sum of paritions must not exceed 910 (if retagging used)'

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
        "CAS_MASTER": 1,
        "L2CBS": 0
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

# P0 - Calypso    - MII 100MBps
# P1 - TJA1102S   - RMII 100MBps
# P2 - KSZ9031    - RGMII 1000MBps  - ANEG
# P3 - KSZ9031    - RGMII 1000MBps  - ANEG
# P4 - cascading  - SGMII 1000MBps

mii_mode_parameters.append(
    {
        "xMII_MODE[0]": MII,
        "PHY_MAC[0]": PHY_MODE,
        "xMII_MODE[1]": RMII,
        "PHY_MAC[1]": MAC_MODE,
        "xMII_MODE[2]": RGMII,
        "PHY_MAC[2]": 0,  # not applicable for RGMII,
        "xMII_MODE[3]": RGMII,
        "PHY_MAC[3]": 0,  # not applicable for RGMII,
        "xMII_MODE[4]": SGMII,
        "PHY_MAC[4]": 0,  # not applicable for SGMII,
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
