import logging
import struct
from enum import IntEnum

import headers
import lzo
import zlib
from bytereader import ByteReader
from io import IOBase


class GbxType(IntEnum):
    CHALLENGE = 0x03043000
    COLLECTOR_LIST = 0x0301B000
    CHALLENGE_PARAMS = 0x0305B000
    BLOCK_SKIN = 0x03059000
    WAYPOINT_SPECIAL_PROP = 0x0313B000
    REPLAY_RECORD = 0x02407E000
    REPLAY_RECORD_TM2 = 0x03093000
    GAME_GHOST = 0x0303F005
    CTN_GHOST = 0x03092000
    CTN_COLLECTOR = 0x0301A000
    CTN_OBJECT_INFO = 0x0301C000
    CTN_DECORATION = 0x03038000
    CTN_COLLECTION = 0x03033000
    GAME_SKIN = 0x03031000
    GAME_PLAYER_PROFILE = 0x0308C000
    MW_NOD = 0x01001000


class GbxLoadError(Exception):
    def __init__(self, message):
        self.message = message


class Gbx(object):
    def __init__(self, obj):
        if isinstance(obj, str):
            self.f = open(obj, 'rb')
            self.root_parser = ByteReader(self.f)
        else:
            self.root_parser = ByteReader(obj)

        self.magic = self.root_parser.read(3, '3s')
        if self.magic.decode('utf-8') != 'GBX':
            print(self.magic)
            raise GbxLoadError(
                'obj is not a valid Gbx data: magic string is incorrect')
        self.version = self.root_parser.read(2, 'H')
        self.classes = {}
        self.root_classes = {}
        self.positions = {}

        self.root_parser.skip(3)
        if self.version >= 4:
            self.root_parser.skip(1)

        if self.version >= 3:
            self.class_id = self.root_parser.read_uint32()
            self.type = GbxType(self.class_id)

            if self.version >= 6:
                self._read_user_data()

            self.num_nodes = self.root_parser.read_uint32()

        self.num_external_nodes = self.root_parser.read_uint32()
        if self.num_external_nodes != 0:
            raise GbxLoadError('External dependencies are not supported yet')

        self.root_parser.push_info()
        self.positions['data_size'] = self.root_parser.pop_info()

        data_size = self.root_parser.read_uint32()
        compressed_data_size = self.root_parser.read_uint32()
        cdata = self.root_parser.read(compressed_data_size)
        self.data = bytearray(lzo.decompress(cdata, False, data_size))

        self.bp = ByteReader(self.data[:])
        self._read_node(self.class_id, -1)

    def get_class_by_id(self, _id):
        classes = self.get_classes_by_ids([_id])
        if len(classes) == 0:
            return None

        return classes[0]

    def get_classes_by_ids(self, ids):
        classes = []
        for cl in list(self.classes.values()) + list(self.root_classes.values()):
            if cl.id in ids:
                classes.append(cl)

        return classes

    def _read_user_data(self):
        entries = {}

        self.root_parser.push_info()
        self.user_data_size = self.root_parser.read_uint32()
        self.positions['user_data_size'] = self.root_parser.pop_info()

        user_data_pos = self.root_parser.pos
        num_chunks = self.root_parser.read_uint32()
        for _ in range(num_chunks):
            cid = self.root_parser.read_uint32()
            self.root_parser.push_info()
            size = self.root_parser.read_uint32()
            self.positions[str(cid)] = self.root_parser.pop_info()
            entries[cid] = size

        for cid, size in entries.items():
            self._read_header_entry(cid, size)

        self.root_parser.pos = user_data_pos + self.user_data_size

    def _read_header_entry(self, cid, size):
        if cid == 0x03043003:
            self.root_parser.read_byte()
            for _ in range(3):
                self.root_parser.read_string_lookback()

            game_class = headers.CGameCommon(cid)

            self.root_parser.push_info()
            game_class.track_name = self.root_parser.read_string()
            self.positions['track_name'] = self.root_parser.pop_info()

            self.root_classes[cid] = game_class
        else:
            self.root_parser.skip(size)

    def _read_node(self, class_id, depth):
        oldcid = 0
        cid = 0

        if class_id == GbxType.CHALLENGE:
            game_class = headers.CGameChallenge(class_id)
        elif class_id == GbxType.REPLAY_RECORD or class_id == GbxType.REPLAY_RECORD_TM2:
            game_class = headers.CGameReplayRecord(class_id)
        elif class_id == GbxType.CTN_GHOST:
            game_class = headers.CGameCtnGhost(class_id)
        elif class_id == GbxType.GAME_GHOST:
            game_class = headers.CGameGhost(class_id)
        else:
            game_class = headers.CGameHeader(class_id)

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
                self.bp.read_string_lookback()
                self.bp.read_string_lookback()
                self.bp.read_string_lookback()
            elif cid == 0x03043011:
                idx = self.bp.read_uint32()
                if idx >= 0 and idx not in self.classes:
                    _class_id = self.bp.read_int32()
                    self._read_node(_class_id, idx)

                idx = self.bp.read_uint32()
                if idx >= 0 and idx not in self.classes:
                    _class_id = self.bp.read_int32()
                    self._read_node(_class_id, idx)

                self.bp.read_uint32()
            elif cid == 0x301B000:
                itemsct = self.bp.read_uint32()
                for _ in range(itemsct):
                    self.bp.read_string_lookback()
                    self.bp.read_string_lookback()
                    self.bp.read_string_lookback()
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
                game_class.map_uid = self.bp.read_string_lookback()
                game_class.environment = self.bp.read_string_lookback()
                game_class.map_author = self.bp.read_string_lookback()

                self.bp.push_info()
                game_class.map_name = self.bp.read_string()
                self.positions['map_name'] = self.bp.pop_info()

                self.bp.push_info()
                game_class.mood = self.bp.read_string_lookback()
                self.positions['mood'] = self.bp.pop_info()
                game_class.env_bg = self.bp.read_string_lookback()
                game_class.env_author = self.bp.read_string_lookback()

                game_class.map_size = (
                    self.bp.read_int32(),
                    self.bp.read_int32(),
                    self.bp.read_int32()
                )

                is_tm2 = game_class.map_size[1] == 40

                game_class.req_unlock = self.bp.read_int32()
                game_class.flags = self.bp.read_int32()

                self.bp.push_info()
                num_blocks = self.bp.read_int32()
                i = 0
                one_more = False
                while i < num_blocks:
                    logging.debug('Reading block {}'.format(i))
                    block = headers.MapBlock()
                    block.name = self.bp.read_string_lookback()
                    if block.name != 'Unassigned1':
                        game_class.blocks.append(block)

                    block.rotation = self.bp.read_byte()
                    block.position = [
                        self.bp.read_byte(),
                        self.bp.read_byte(),
                        self.bp.read_byte()
                    ]

                    if is_tm2:
                        block.position = [
                            block.position[0] - 1, block.position[1] - 8, block.position[2] - 1]

                    if game_class.flags > 0:
                        block.flags = self.bp.read_uint32()
                    else:
                        block.flags = self.bp.read_uint16()

                    if block.flags == 0xFFFFFFFF:
                        continue

                    if (block.flags & 0x8000) != 0:
                        block.skin_author = self.bp.read_string_lookback()
                        block.skin = self.bp.read_int32()
                        if block.skin >= 0 and block.skin not in self.classes:
                            _class_id = self.bp.read_int32()
                            logging.debug(
                                'Reading block skin {}'.format(block.skin))
                            self._read_node(_class_id, block.skin)

                    if (block.flags & 0x100000) != 0:
                        block.params = self.bp.read_int32()
                        if block.params >= 0 and block.params not in self.classes:
                            _class_id = self.bp.read_int32()
                            logging.debug(
                                'Reading block params {}'.format(block.params))
                            self._read_node(_class_id, block.params)

                    if one_more:
                        break

                    if i + 1 == num_blocks:
                        if self.bp.read_uint32() == 10:
                            one_more = True
                            i -= 1

                        self.bp.skip(-4)

                    i += 1

                self.positions['block_data'] = self.bp.pop_info()
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
                    if len(file_path) > 0 or version >= 3:
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
                idx = self.bp.read_uint32()
                if idx >= 0 and idx not in self.classes:
                    _class_id = self.bp.read_int32()
                    self._read_node(_class_id, idx)
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
            elif cid == 0x0303F005:
                self.read_ghost(game_class)
            elif cid == 0x0303F006:
                self.bp.skip(4)
                self.read_ghost(game_class)
            elif cid == 0x03093014:
                self.bp.skip(4)
                num_ghosts = self.bp.read_uint32()
                for _ in range(num_ghosts):
                    idx = self.bp.read_int32()
                    if idx >= 0 and idx not in self.classes:
                        _class_id = self.bp.read_uint32()
                        self._read_node(_class_id, idx)

            elif cid == 0x03093002:
                map_gbx_size = self.bp.read_uint32()
                data = bytes(self.bp.read(map_gbx_size))
                game_class.track = Gbx(data)
            elif cid == 0x03092005:
                game_class.race_time = self.bp.read_uint32()
            elif cid == 0x03092008:
                game_class.num_respawns = self.bp.read_uint32()
            elif cid == 0x03092009:
                game_class.light_trail_color = self.bp.read_vec3()
            elif cid == 0x0309200A:
                game_class.stunts_score = self.bp.read_uint32()
            elif cid == 0x0309200E:
                game_class.uid = self.bp.read_string_lookback()
            elif cid == 0x0309200F:
                game_class.login = self.bp.read_string()
            elif skipsize != -1:
                self.bp.skip(skipsize)
                cid = oldcid
            else:
                return

    def read_ghost(self, game_class):
        uncomp_sz = self.bp.read_uint32()
        comp_sz = self.bp.read_uint32()
        comp_data = self.bp.read(comp_sz)
        data = zlib.decompress(comp_data, 0, uncomp_sz)

        gr = ByteReader(data)
        gr.skip(5 * 4)

        sample_data_sz = gr.read_uint32()
        sample_data_pos = gr.pos
        gr.skip(sample_data_sz)

        sample_sizes = []
        num_samples = gr.read_uint32()
        fso = 0
        if num_samples > 0:
            fso = gr.read_uint32()
            if num_samples > 1:
                sps = gr.read_int32()
                if sps == -1:
                    sample_sizes = []
                    for _ in range(num_samples - 1):
                        sample_sizes.append(gr.read_uint32())
                else:
                    sample_sizes.append(sps)

        gr.pos = sample_data_pos
        gr.skip(fso)
        for i in range(num_samples):
            sample_pos = gr.pos

            record = headers.GhostSampleRecord(
                gr.read_vec3(), gr.read_uint16(), gr.read_int16(),
                gr.read_int16(), gr.read_int16(),
                gr.read_int8(), gr.read_int8())

            if len(sample_sizes) == 1:
                sample_sz = sample_sizes[0]
            else:
                sample_sz = sample_sizes[i]

            gr.pos = sample_pos + sample_sz
            game_class.records.append(record)
