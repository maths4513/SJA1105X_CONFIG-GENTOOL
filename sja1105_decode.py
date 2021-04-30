# Copyright 2019-2021 NXP. All rights reserved.
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

from __future__ import print_function


import argparse

from ethsw.configuration import Configuration
import ethsw.tables_sja1105pqrs
import ethsw.tables_sja1105

# Arguments parser
parser = argparse.ArgumentParser()
parser.add_argument("--hex", help="Hex file to load", default='simpleT_SJA1110.hex')
args = parser.parse_args()


c = Configuration()
device_id = c.peek_device_id_hex(args.hex)

SJA1105QS_DEVICEID = 0xae00030e
SJA1105PR_DEVICEID = 0xaf00030e
SJA1105_DEVICEID = 0x9f00030e
SJA1105T_DEVICEID = 0x9e00030e

table_map = {SJA1105QS_DEVICEID: ethsw.tables_sja1105pqrs.layoutid_map,
             SJA1105PR_DEVICEID: ethsw.tables_sja1105pqrs.layoutid_map,
             SJA1105_DEVICEID: ethsw.tables_sja1105.layoutid_map,
             SJA1105T_DEVICEID: ethsw.tables_sja1105.layoutid_map, }

c.from_hex(args.hex, table_map[device_id])

print("Number of bytes: %d" % (len(c.to_bytes())))
print("======================")
print(c)
