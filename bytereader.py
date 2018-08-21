import struct
import logging

class ByteReader(object):
    def __init__(self, obj):
        self.data = obj
        if type(obj) == file:
            self.get_bytes = self.get_bytes_file
        else:
            self.get_bytes = self.get_bytes_generic

        self.pos = 0
        self.seen_loopback = False
        self.stored_strings = []

    def read(self, num_bytes, typestr=None):
        val = self.get_bytes(num_bytes)
        self.pos += num_bytes
        if typestr == None:
            return val
        return struct.unpack(typestr, val)[0]

    def get_bytes_file(self, num_bytes):
        self.data.seek(self.pos)
        return self.data.read(num_bytes)

    def get_bytes_generic(self, num_bytes):
        return self.data[self.pos:self.pos + num_bytes]

    def read_uint32(self):
        return self.read(4, 'I')

    def read_int32(self):
        return self.read(4, 'i')

    def read_uint16(self):
        return self.read(2, 'H')

    def read_string(self):
        strlen = self.read_uint32()
        return self.read(strlen, str(strlen) + 's')

    def read_byte(self):
        val = self.get_bytes(1)[0]
        self.pos += 1
        return val   

    def skip(self, num_bytes):
        self.pos += num_bytes

    def read_string_loopback(self):
        if not self.seen_loopback:
            self.read_uint32()
        
        self.seen_loopback = True
        inp = self.read_uint32()
        if (inp & 0xc0000000) != 0 and (inp & 0x3fffffff) == 0:
            s = self.read_string()
            self.stored_strings.append(s)
            return s
        
        if inp == 0:
            print ("READ STRING")
            s = self.read_string()
            self.stored_strings.append(s)
            return s
        
        if inp == -1:
            return ''

        if (inp & 0x3fffffff) == inp:
            if inp == 11:
                return 'Valley'
            elif inp == 12:
                return 'Canyon'
            elif inp == 17:   
                return 'TMCommon'
            elif inp == 202:   
                return 'Storm'
            elif inp == 299:   
                return 'SMCommon'
            elif inp == 10003:   
                return 'Common'

        inp &= 0x3fffffff
        if inp - 1 >= len(self.stored_strings):
            logging.debug('String not found in list with index: {}'.format(bin(inp)))
            return ''
        return self.stored_strings[inp - 1]