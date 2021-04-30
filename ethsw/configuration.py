# Copyright 2017, 2019-2021 NXP. All rights reserved.
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

"""Classes used for the configuration of the SJA11xx switch family

"""

from __future__ import print_function

import struct
import binascii

try:
    import pkg_resources
    pkg_resources.require("intelhex>=2.2.1")
    import intelhex
except ImportError:
    pkg_resources = None
    import intelhex

try:
    from prettytable import PrettyTable
except ImportError:
    PrettyTable = None

# Mandatory tables for SJA1110
REQ_TABS_SJA1110 = [6, 8, 9, 14, 17, 28]
REQ_TABS_SJA1110_DEPS = {
    0: [1, 10, 11],
    2: [3, 4, 12],
    4: [12],
}

# Mandatory tables for SJA1105Q/S
REQ_TABS_SJA1105QS = [6, 8, 9, 14, 17, 78]
REQ_TABS_SJA1105QS_DEPS = {
    0: [1, 10, 11],
    2: [3, 4, 12],
    4: [12],
}

# Mandatory tables for SJA1105P/R
REQ_TABS_SJA1105PR = [6, 8, 9, 14, 17, 78]
REQ_TABS_SJA1105PR_DEPS = {}

# Mandatory tables for SJA1105T
REQ_TABS_SJA1105T = [6, 8, 9, 14, 17, 78]
REQ_TABS_SJA1105T_DEPS = {
    0: [1, 10, 11],
    2: [3, 4, 12],
    4: [12],
}

# Mandatory tables for SJA1105
REQ_TABS_SJA1105 = [6, 8, 9, 14, 17, 78]
REQ_TABS_SJA1105_DEPS = {}

# Mapping of mandatory tables to deviceID
REQ_TABS = {
    0xb700030e: [REQ_TABS_SJA1110, REQ_TABS_SJA1110_DEPS],  # SJA11110 Rev A
    0xb700030f: [REQ_TABS_SJA1110, REQ_TABS_SJA1110_DEPS],  # SJA1110 Rev B/C
    0xae00030e: [REQ_TABS_SJA1105QS, REQ_TABS_SJA1105QS_DEPS],  # SJA1105QS
    0xaf00030e: [REQ_TABS_SJA1105PR, REQ_TABS_SJA1105PR_DEPS],  # SJA1105PR
    0x9E00030E: [REQ_TABS_SJA1105T, REQ_TABS_SJA1105T_DEPS],  # SJA1105T
    0x9F00030E: [REQ_TABS_SJA1105, REQ_TABS_SJA1105_DEPS],  # SJA1105
}


def make_table_by_id(tableid):
    return Table(tableid=tableid)


def make_table_by_layout(layout, layoutid_map):
    tableid = get_tableid_for_layout(layout, layoutid_map)

    # For DPI the different layouts have different entry size
    if tableid == 27:
        fields = [Field(l) for l in layout]
        bits = sum([field.len for field in fields])
        # align MSB of first field to MSB of the next 32 bit boundary
        entry_len_words = (bits + 32 - 1) // 32
    # For other tables, different layouts have the same size
    else:
        # Obtain entry size
        layouts = [(x[0], x[2]) for x in layoutid_map if x[1] == tableid]
        entry_len_words = 0
        for _layout, func in layouts:

            fields = [Field(l) for l in _layout]
            bits = sum([field.len for field in fields])
            # align MSB of first field to MSB of the next 32 bit boundary
            entry_len_words = max(entry_len_words, (bits + 32 - 1) // 32)

    return Table(layout=layout, tableid=tableid, entry_len_words=entry_len_words)


def get_tableid_for_layout(layout, layoutid_map):
    tableids = [t[1] for t in layoutid_map if t[0] is layout]
    if len(tableids) == 0:
        Exception("No table id found for layout")
    assert len(
        tableids) == 1, "more than two tables for a given layout available: %s" % (str(tableids))
    return tableids[0]


def crc32(bytes):
    return binascii.crc32(bytes) & 0xffffffff


class Field(object):
    def __init__(self, l=None):
        self.name = None
        self.len = 0
        self.value = 0
        self.offset = 0

        if l is not None:
            self.from_list(l)

    def from_list(self, l):
        self.name = l[0]
        self.len = l[1]
        self.value = l[2]

    def __str__(self):
        return "%s: %x, len:%d, offset: %d" % (self.name, self.value, self.len, self.offset)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__

        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)


class Entry(object):
    def __init__(self, layout=None, data=None, num_words=0):
        self.fields = None
        self.len = 0
        self.num_words = num_words
        self._process_layout(layout)

        if data is not None:
            for key, value in data.items():
                self[key] = value

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            if (self.fields is None) and (other.fields is None):
                return True
            if (self.fields is None) or (other.fields is None):
                return False
            eq = True
            if len(self.fields) != len(other.fields):
                return False
            for ind, el in enumerate(self.fields):
                eq = eq & (self.fields[ind] == other.fields[ind])

            return eq

        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def has_key(self, name):
        if self._get_field_by_name(name) is None:
            return False
        return True

    def _gen_fields(self, layout):
        self.fields = [Field(l) for l in layout]

    def _process_layout(self, layout):
        assert layout is not None

        self._gen_fields(layout)

        self.len = self.num_words * 32
        top = (self.num_words * 32)
        if self.num_words == 0:
            bits = sum([field.len for field in self.fields])
            words = (bits + 32 - 1) // 32
            self.len = words * 32
            top = (words * 32)

        for field in self.fields:
            field.offset = top - field.len
            top = field.offset
            # print "%s, %d" %(field.name, field.offset)

    def _get_field_by_name(self, name):
        for field in self.fields:
            if field.name == name:
                return field
        return None

    def __setitem__(self, key, value):
        f = self._get_field_by_name(key)
        if f is None:
            raise KeyError('no Field %s in layout' % key)
        # long got removed in python3
        if not isinstance(value, int):
            print("Warning type of %s is not int or long but %s" % (key, type(value)))
        f.value = value & ((1 << f.len) - 1)
        if value != f.value:
            print("WARNING: %s truncated" % key)

    def __getitem__(self, key):
        f = self._get_field_by_name(key)
        if f is None:
            raise KeyError('no Field %s in layout' % key)
        return f.value

    def __str__(self):
        if PrettyTable is not None:
            table = PrettyTable(["Name", "Value", "Len", "Offset"])
            for f in self.fields:
                table.add_row((f.name, f.value, f.len, f.offset))
            return table.get_string()
        else:
            s = '\n\t' + '\n\t'.join([str(f) for f in self.fields])
            return 'ENTRY:' + s

    def __len__(self):
        return len(self.fields) if self.fields is not None else 0

    def to_bytes(self):
        d = 0
        for field in self.fields:
            d |= field.value << field.offset

        byte_like = list()
        for i in range(self.len // 8):
            byte_like.append((d >> i * 8) & 0xff)

        bytes = bytearray(byte_like)

        assert len(bytes) > 0
        return bytes

    def from_bytes(self, bytes):
        d = 0
        for b in reversed(bytes):
            d <<= 8
            d |= b

        for f in self.fields:
            f.value = (d >> f.offset) & ((1 << f.len) - 1)


class Table(object):
    def __init__(self, layout=None, tableid=-1, entry_len_words=0):
        """

        :param tableid: the table id (block id)
        :param layout:  the layout as a list of fields (not an entry)
        :return:
        """
        self.tableid = tableid
        self.entries = list()
        self.layout = layout
        self.entry_len_words = entry_len_words

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            if self.tableid != other.tableid:
                return False

            if len(self.entries) != len(other.entries):
                return False

            eq = True
            ind = 0
            while eq and ind < len(self.entries):
                eq = eq & (self.entries[ind] == other.entries[ind])
                ind += 1
            return eq

        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __len__(self):
        return len(self.entries)

    def append(self, entry):

        if isinstance(entry, dict):
            self.entries.append(
                Entry(layout=self.layout, data=entry, num_words=self.entry_len_words))
        else:
            self.entries.append(entry)

    def to_bytes(self):
        payload_bytes = bytearray()
        for entry in self.entries:
            payload_bytes += entry.to_bytes()

        bytes = bytearray()
        bytes += struct.pack("<I", self.tableid << 24)
        bytes += struct.pack("<I", len(payload_bytes) // 4)
        bytes += struct.pack("<I", crc32(bytes))
        bytes += payload_bytes
        bytes += struct.pack("<I", crc32(payload_bytes))

        return bytes

    def _get_layouts_for_id(self, tableid, layoutid_map):
        layouts = [(x[0], x[2]) for x in layoutid_map if x[1] == tableid]
        assert len(layouts) > 0, "no layout found for tableid %d" % (tableid)
        return layouts

    def _select_layout(self, layouts, configuration, bytes):
        if len(layouts) == 1:
            return layouts[0][0]
        else:
            for layout, func in layouts:
                assert func is not None, "no selction function available"
                if func(configuration, bytes) is True:
                    return layout

        return None

    def from_bytes(self, bytes, layoutid_map, configuration):
        self.bytes = bytes

        layouts = self._get_layouts_for_id(self.tableid, layoutid_map)
        if len(layouts) > 1:
            #print("INFO: Skipping table %d for now. Retry in second pass" % (self.tableid))
            pass
        else:
            self.second_stage(layoutid_map, configuration)

    def second_stage(self, layoutid_map, configuration):
        # we dont know which layout exactly we see,
        # but to get the size any will do

        # if we have entries, the table was already decoded in the first stage and we can skip the rest
        if len(self.entries) > 0:
            #print ("calling 2nd stage, but already read %d entries. table id %d" % (len(self.entries), self.tableid))
            return

        bytes = self.bytes

        layouts = self._get_layouts_for_id(self.tableid, layoutid_map)

        entry_len_words = 0
        for layout, func in layouts:
            # For DPI the different layouts have different entry size;
            # so take correct one only
            if self.tableid == 27:
                if not func(configuration, bytes):
                    break

            fields = [Field(l) for l in layout]
            bits = sum([field.len for field in fields])
            # align MSB of first field to MSB of the next 32 bit boundary
            entry_len_words = max(entry_len_words, (bits + 32 - 1) // 32)

        while len(bytes) > 0:
            lay = self._select_layout(layouts, configuration, bytes)

            if (self.tableid == 27):  # For DPI the different layouts have different entry size;
                bytes_per_entry = Entry(lay).len // 8
            else:  # For others entry size can be calculated from entry_len_words
                bytes_per_entry = 4 * entry_len_words

            assert len(
                bytes
            ) % bytes_per_entry == 0, "Number of bytes left to process is not a full entry"

            layout = self._select_layout(layouts, configuration, bytes)

            if layout is None:
                raise Exception("No layout for table %d in second pass found" % (self.tableid))

            e = Entry(layout=layout, num_words=entry_len_words)
            e.from_bytes(bytes[:bytes_per_entry])
            self.append(e)
            bytes = bytes[bytes_per_entry:]

    def __str__(self):
        output = "Table ID: %d #entries: %d\n" % (self.tableid, len(self.entries))

        for idx, entry in enumerate(self.entries):
            output += "======= entry #%d =======\n" % (idx)
            output += str(entry) + "\n"
        return output


class Configuration(object):
    def __init__(self, deviceid=0, validating=1):
        self.deviceid = deviceid
        self.tables = list()
        self.validating = validating

    def cmp(self, other):
        """Compared two cpnfigurations.

        :param other: configuration to compare with
        :type other: `Configuration`
        :return: Returns:
                 0 if differ;
                 1 if same (taking order of tables into account);
                 2 if same (not taking order of tables into account)
        :rtype: [type]
        """
        if isinstance(other, self.__class__):
            # Device ID check
            if self.deviceid != other.deviceid:
                print('Different deviceids')
                return 0

            # Check that both tables are valid:
            if not self.isValid():
                print('First configuration not valid')
            if not other.isValid():
                print('Second configuration not valid')

            # Numer of tables
            if len(self.tables) != len(other.tables):
                print('Different number of tables')
                return 0

            # Check tables taking ordering into account
            if len(self.tables) == len(other.tables) and len(self.tables) == sum(
                [1 for i, j in zip(self.tables, other.tables) if i == j]):
                return 1
            else:
                # Check tables ignoring order
                for el in self.tables:
                    if el.tableid > 0:
                        a = [
                            index for index, tab in enumerate(other.tables)
                            if tab.tableid == el.tableid
                        ]
                        if not a:
                            print(
                                "Table of first config missing in second (tabid {:})".format(
                                    el.tableid))
                        if not el == other.tables[a[0]]:
                            print("Table differ (tabid {:})".format(el.tableid))
                            return 0

                print('Configurations are equal, but order of tables differs')
                return 2
        else:
            return 0

    def __eq__(self, other):
        return self.cmp(other) == 1

    def __ne__(self, other):
        return not self.__eq__(other)

    def append(self, table):
        self.tables.append(table)

    def to_hex(self, filename):

        if self.validating and not self.isValid():
            raise Exception(
                'Error in config. Not creating .hex file. (Check can be disabled by using validating=0'
            )

        bytes = self.to_bytes()

        ihex = intelhex.IntelHex()
        ihex.frombytes(bytes)
        ihex.write_hex_file(filename, write_start_addr=False, eolstyle='native', byte_count=4)

    def from_hex(self, filename, layoutid_map):
        ihex = intelhex.IntelHex()
        ihex.loadhex(filename)
        bytes = ihex.tobinarray()
        assert len(bytes) % 4 == 0, "Hex file does contain an integer number of bytes"
        self.from_bytes(bytes, layoutid_map)
        if self.validating and not self.isValid():
            print('Loaded configuration is errorneous.')

    def _decode_table(self, bytes, layoutid_map):
        tableid = struct.unpack("<I", bytes[0:4])[0] >> 24
        length = struct.unpack("<I", bytes[4:8])[0]
        # crc1 = struct.unpack("<I", bytes[8:12])[0]

        bytes = bytes[12:length * 4 + 12]

        # Do not add 'delimiter' as table.
        if not (tableid == 0 and length == 0):
            table = Table(tableid=tableid)
            table.from_bytes(bytes, layoutid_map, self)
            self.append(table)
        return length

    def peek_device_id_hex(self, filename):
        ihex = intelhex.IntelHex()
        ihex.loadhex(filename)
        bytes = ihex.tobinarray()
        return self.peek_device_id(bytes)

    def peek_device_id(self, bytes):
        return struct.unpack("<I", bytes[0:4])[0]

    def from_bytes(self, bytes, layoutid_map):
        assert len(bytes) % 4 == 0
        self.deviceid = self.peek_device_id(bytes)

        bytes = bytes[4:]

        while len(bytes) > 0:
            length = self._decode_table(bytes, layoutid_map)
            bytes = bytes[(4 + length) * 4:]

        for t in self.tables:
            t.second_stage(layoutid_map, self)

    def to_bytes(self):
        self.tables.sort(key=lambda x: x.tableid)
        # note that we write tables always in order of table ids
        # tttech tries also to do it that way, but fails for some tables
        # this is why the hex output will not look identical

        bytes = bytearray()
        bytes += struct.pack("<I", self.deviceid)

        for table in self.tables:
            if len(table.entries) > 0:
                bytes += table.to_bytes()

        bytes += struct.pack("<I", 0)
        bytes += struct.pack("<I", 0)

        bytes += struct.pack("<I", crc32(bytes))

        return bytes

    def __str__(self):
        self.tables.sort(key=lambda x: x.tableid)
        output = "Configuration for switch device id: %08X\n" % (self.deviceid)
        for table in self.tables:
            if len(table.entries) > 0:  # Only output tables with entries
                output += str(table)

        return output

    def isValid(self):
        """Checks if configuration is valid

        Only checks if:
          * all mandatory tables are present
          * no duplicates exists

        :return: 1/True when valid
        """

        # Testing for mandatory tables:
        if self.deviceid not in REQ_TABS.keys():
            # Skip test
            print('No test implemented')
        else:
            # Build list of mandatoy Tables
            mandatory_tables = set(REQ_TABS[self.deviceid][0])
            seen_tables = []
            for tab in self.tables:
                if tab.tableid in seen_tables:
                    print('Found duplicate table id ({:}).'.format(tab.tableid))
                    return 0
                seen_tables.append(tab.tableid)
                if tab.tableid in REQ_TABS[self.deviceid][1].keys():
                    mandatory_tables.update(set(REQ_TABS[self.deviceid][1][tab.tableid]))
            # Check if required tables present
            for tab in mandatory_tables:
                if tab not in seen_tables:
                    print(
                        'Mandatory table ({:}) is missing. (Tables present: {:})'.format(
                            tab, seen_tables))
                    return 0
            return 1
        return 0
