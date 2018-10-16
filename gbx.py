import struct
import lzo
import logging
from enum import IntEnum

from bytereader import ByteReader
import headers

class GbxType(IntEnum):
    CHALLENGE = 0x03043000
    COLLECTOR_LIST = 0x0301B000
    CHALLENGE_PARAMS = 0x0305B000
    BLOCK_SKIN = 0x03059000
    WAYPOINT_SPECIAL_PROP = 0x0313B000
    REPLAY_RECORD = 0x03093000
    GAME_GHOST = 0x0303F005
    CTN_GHOST = 0x03092000
    CTN_COLLECTOR = 0x0301A000
    CTN_OBJECT_INFO = 0x0301C000
    CTN_DECORATION = 0x03038000
    CTN_COLLECTION = 0x03033000
    GAME_SKIN = 0x03031000
    GAME_PLAYER_PROFILE = 0x0308C000
    MW_NOD = 0x01001000
    
class Gbx(object):
    def __init__(self, path):
        self.f = open(path, 'rb')
        self.pos = 0

        root_parser = ByteReader(self.f)

        self.magic = root_parser.read(3, '3s')
        self.valid = self.magic == 'GBX'
        self.version = root_parser.read(2, 'H')
        self.classes = {}
        self.num_blocks_offset = -1
        self.block_data_size = -1
        self.data_size_offset = -1

        root_parser.skip(3)
        if self.version >= 4:
            root_parser.skip(1)

        if self.version >= 3:
            self.class_id = root_parser.read_uint32()
            self.type = GbxType(self.class_id)

            if self.version >= 6:
                self.user_data_size = root_parser.read_uint32()
                root_parser.skip(self.user_data_size)

                self.num_nodes = root_parser.read_uint32()

        self.num_external_nodes = root_parser.read_uint32()
        if self.num_external_nodes != 0:
            print('The Gbx class does not support files with external dependencies yet.')
            self.valid = False
            return

        self.data_size_offset = root_parser.pos
        data_size = root_parser.read_uint32()
        compressed_data_size = root_parser.read_uint32()
        cdata = root_parser.read(compressed_data_size)
        self.data = bytearray(lzo.decompress(cdata, False, data_size))

        self.bp = ByteReader(self.data[:])
        self.read_node(self.class_id, -1)

    def get_class_by_id(self, id):
        for cl in self.classes.values():
            if cl.id == id:
                return cl

        return None

    def read_node(self, class_id, depth):
        oldcid = 0
        cid = 0

        game_class = headers.CGameHeader(class_id)
        if class_id == GbxType.CHALLENGE:
            game_class = headers.CGameChallenge(class_id)

        self.classes[depth] = game_class

        while True:
            oldcid = cid
            cid = self.bp.read_int32()
            logging.debug('Reading node {}'.format(hex(cid)))
            if cid == 0xFACADE01:
                break

            skipsize = -1
            skip = self.bp.read_int32()

            if skip == 0x534B4950:
                skipsize = self.bp.read_uint32()
            else:
                self.bp.pos -= 4

            if cid == 0x0304300D:
                self.bp.read_string_loopback()
                self.bp.read_string_loopback()
                self.bp.read_string_loopback()
            elif cid == 0x03043011:
                nodid = self.bp.read_uint32()
                if nodid >= 0 and nodid not in self.classes:
                    node_class_id = self.bp.read_int32()
                    self.read_node(node_class_id, nodid)

                nodid2 = self.bp.read_uint32()
                if nodid2 >= 0 and nodid2 not in self.classes:
                    node_class_id2 = self.bp.read_int32()
                    self.read_node(node_class_id2, nodid2)

                self.bp.read_uint32()
            elif cid == 0x301B000:
                itemsct = self.bp.read_uint32()
                for _ in range(itemsct):
                    self.bp.read_string_loopback()
                    self.bp.read_string_loopback()
                    self.bp.read_string_loopback()
                    self.bp.read_uint32()
            elif cid == 0x305B000:
                self.bp.skip(8 * 4)
            elif cid == 0x0305B001:
                self.bp.read_string()
                self.bp.read_string()
                self.bp.read_string()
                self.bp.read_string()
            elif cid == 0x0305B004:
                game_class.times = {
                    'bronze': self.bp.read_int32(),
                    'silver': self.bp.read_int32(),
                    'gold': self.bp.read_int32(),
                    'author': self.bp.read_int32()
                }

                self.bp.read_uint32()
            elif cid == 0x0305B008:
                self.bp.skip(2 * 4)
            elif cid == 0x0305B00A:
                self.bp.skip(9 * 4)
            elif cid == 0x0305B00D:
                self.bp.skip(1 * 4)
            elif cid == 0x0304301F:
                game_class.map_uid = self.bp.read_string_loopback()
                game_class.environment = self.bp.read_string_loopback()
                game_class.map_author = self.bp.read_string_loopback()
                game_class.map_name = self.bp.read_string()
                game_class.mood = self.bp.read_string_loopback()
                game_class.env_bg = self.bp.read_string_loopback()
                game_class.env_author = self.bp.read_string_loopback()

                game_class.map_size = (
                    self.bp.read_int32(),
                    self.bp.read_int32(),
                    self.bp.read_int32()
                )

                is_tm2 = game_class.map_size[1] == 40

                game_class.req_unlock = self.bp.read_int32()
                game_class.flags = self.bp.read_int32()

                self.num_blocks_offset = self.bp.pos
                num_blocks = self.bp.read_int32()
                i = 0
                one_more = False
                while i < num_blocks:
                    logging.debug('Reading block {}'.format(i))
                    block = headers.MapBlock()
                    block.name = self.bp.read_string_loopback()
                    if block.name != 'Unassigned1':
                        game_class.blocks.append(block)

                    block.rotation = self.bp.read_byte()
                    block.position = [
                        self.bp.read_byte(),
                        self.bp.read_byte(),
                        self.bp.read_byte()
                    ]

                    if is_tm2:
                        block.position = [block.position[0] - 1, block.position[1] - 8, block.position[2] - 1]

                    if game_class.flags > 0:
                        block.flags = self.bp.read_uint32()
                    else:
                        block.flags = self.bp.read_uint16()

                    if block.flags == 0xFFFFFFFF:
                        continue

                    if (block.flags & 0x8000) != 0:
                        block.skin_author = self.bp.read_string_loopback()
                        block.skin = self.bp.read_int32()
                        if block.skin >= 0 and block.skin not in self.classes:
                            cidd = self.bp.read_int32()
                            logging.debug(
                                'Reading block skin {}'.format(block.skin))
                            self.read_node(cidd, block.skin)

                    if (block.flags & 0x100000) != 0:
                        block.params = self.bp.read_int32()
                        if block.params >= 0 and block.params not in self.classes:
                            cidd = self.bp.read_int32()
                            logging.debug(
                                'Reading block params {}'.format(block.params))
                            self.read_node(cidd, block.params)

                    if one_more:
                        break

                    if i + 1 == num_blocks:
                        if self.bp.read_uint32() == 10:
                            one_more = True
                            i -= 1

                        self.bp.skip(-4)

                    i += 1

                self.block_data_size = self.bp.pos - self.num_blocks_offset
                self.bp.skip(12)
            elif cid == 0x03059002:
                self.bp.read_string()
                for _ in range(2):
                    version = self.bp.read_byte()
                    if version >= 3:
                        self.bp.skip(32)

                    file_path = self.bp.read_string()

                    # (?) according to https://wiki.xaseco.org/wiki/GBX
                    # we need to check if the file path is not empty
                    # here but it crashes reading the file for TM2 challenges
                    if len(file_path) > 0 and version >= 1:
                        self.bp.read_string()
            elif cid == 0x03043022:
                self.bp.read_int32()
            elif cid == 0x03043024:
                self.bp.read_byte()
                self.bp.skip(32)
                self.bp.read_string()
                self.bp.read_string()
            elif cid == 0x03043025:
                self.bp.skip(16)
            elif cid == 0x03043026:
                ind = self.bp.read_uint32()
                if ind >= 0 and ind not in self.classes:
                    cidd = self.bp.read_int32()
                    self.read_node(cidd, ind)
            elif cid == 0x03043028:
                p = self.bp.read_int32()
                if p != 0:
                    self.bp.skip(1 + 4 * 3 * 3 + 4 * 3 + 4 + 4 + 4)

                self.bp.read_string()
            elif cid == 0x0304302A:
                self.bp.read_uint32()
            elif cid == 0x2e009000:
                version = self.bp.read_uint32()
                if version == 1:
                    self.bp.read_uint32()
                    self.bp.read_uint32()
                elif version == 2:
                    self.bp.read_string()
                    self.bp.read_uint32()
            elif cid == 0x03059000:
                self.bp.read_string()
                self.bp.read_string()

            elif skipsize != -1:
                self.bp.skip(skipsize)
                cid = oldcid
            else:
                return