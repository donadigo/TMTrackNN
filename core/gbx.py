import logging
import struct
from enum import IntEnum

import lzo
import zlib
from io import IOBase

import core.headers as headers
from core.bytereader import ByteReader

class GbxType(IntEnum):
    CHALLENGE = 0x03043000
    CHALLENGE_OLD = 0x24003000
    COLLECTOR_LIST = 0x0301B000
    CHALLENGE_PARAMS = 0x0305B000
    BLOCK_SKIN = 0x03059000
    WAYPOINT_SPECIAL_PROP = 0x0313B000
    ITEM_MODEL = 0x2E002000
    REPLAY_RECORD = 0x03093000
    REPLAY_RECORD_OLD = 0x02407E000
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
            raise GbxLoadError(f'obj is not a valid Gbx data: magic string is incorrect')
        self.version = self.root_parser.read(2, 'H')
        self.classes = {}
        self.root_classes = {}
        self.positions = {}
        self.__current_waypoint = None

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

        bp = ByteReader(self.data[:])
        self._read_node(self.class_id, -1, bp)

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
        if cid == 0x03043003 or cid == 0x24003003:
            p = self.root_parser.pos
            self.root_parser.read_byte()
            for _ in range(3):
                self.root_parser.read_string_lookback()

            game_class = headers.CGameCommon(cid)

            self.root_parser.push_info()
            game_class.track_name = self.root_parser.read_string()
            self.positions['track_name'] = self.root_parser.pop_info()

            self.root_classes[cid] = game_class

            self.root_parser.pos = p + size
        elif cid == 0x03043005 or cid == 0x24003005:
            self.__community = self.root_parser.read_string()
        else:
            self.root_parser.skip(size)

    def _read_node(self, class_id, depth, bp, add=True):
        oldcid = 0
        cid = 0

        if class_id == GbxType.CHALLENGE or class_id == GbxType.CHALLENGE_OLD:
            game_class = headers.CGameChallenge(class_id)
            if hasattr(self, '__community'):
                game_class.community = self.__community
        elif class_id == GbxType.REPLAY_RECORD or class_id == GbxType.REPLAY_RECORD_OLD:
            game_class = headers.CGameReplayRecord(class_id)
        elif class_id == GbxType.WAYPOINT_SPECIAL_PROP or class_id == 0x2E009000:
            game_class = headers.CGameWaypointSpecialProperty(class_id)
            self.__current_waypoint = game_class
            add = False
        elif class_id == GbxType.CTN_GHOST:
            game_class = headers.CGameCtnGhost(class_id)
        elif class_id == GbxType.GAME_GHOST:
            game_class = headers.CGameGhost(class_id)
        elif class_id == GbxType.COLLECTOR_LIST:
            game_class = headers.CGameCtnCollectorList(class_id)
        else:
            game_class = headers.CGameHeader(class_id)

        if add:
            self.classes[depth] = game_class

        while True:
            oldcid = cid
            cid = bp.read_uint32()
            if cid == 0xFACADE01:
                break

            skipsize = -1
            skip = bp.read_int32()
            if skip == 0x534B4950:
                skipsize = bp.read_uint32()
            else:
                bp.pos -= 4

            if cid == 0x0304300D or cid == 0x2400300D:
                bp.read_string_lookback()
                bp.read_string_lookback()
                bp.read_string_lookback()
            elif cid == 0x03043011 or cid == 0x24003011:
                for _ in range(2):
                    idx = bp.read_uint32()
                    if idx >= 0 and idx not in self.classes:
                        _class_id = bp.read_int32()
                        self._read_node(_class_id, idx, bp)
                bp.read_uint32()
            elif cid == 0x301B000 or cid == 0x2403C000:
                itemsct = bp.read_uint32()
                for _ in range(itemsct):
                    bp.read_string_lookback()
                    bp.read_string_lookback()
                    bp.read_string_lookback()
                    bp.read_uint32()
            elif cid == 0x0305B001 or cid == 0x2400C001:
                bp.read_string()
                bp.read_string()
                bp.read_string()
                bp.read_string()
            elif cid == 0x0305B004 or cid == 0x2400C004:
                game_class.times = {
                    'bronze': bp.read_int32(),
                    'silver': bp.read_int32(),
                    'gold': bp.read_int32(),
                    'author': bp.read_int32()
                }

                bp.read_uint32()
            elif cid == 0x0305B005 or cid == 0x2400C005:
                bp.skip(4 * 3)
            elif cid == 0x0305B006 or cid == 0x2400C006:
                count = bp.read_uint32()
                bp.skip(count * 4)
            elif cid == 0x0305B008 or cid == 0x2400C008:
                bp.skip(2 * 4)
            elif cid == 0x0305B00A:
                bp.skip(9 * 4)
            elif cid == 0x0305B000 or cid == 0x2400C000:
                bp.skip(8 * 4)
            elif cid == 0x0305B00D:
                bp.skip(1 * 4)
            elif cid == 0x0304301F or cid == 0x2400301F:
                game_class.map_uid = bp.read_string_lookback()
                game_class.environment = bp.read_string_lookback()
                game_class.map_author = bp.read_string_lookback()

                bp.push_info()
                game_class.map_name = bp.read_string()
                self.positions['map_name'] = bp.pop_info()

                bp.push_info()
                game_class.mood = bp.read_string_lookback()
                self.positions['mood'] = bp.pop_info()
                game_class.env_bg = bp.read_string_lookback()
                game_class.env_author = bp.read_string_lookback()

                game_class.map_size = (
                    bp.read_int32(),
                    bp.read_int32(),
                    bp.read_int32()
                )

                game_class.req_unlock = bp.read_int32()
                game_class.flags = bp.read_int32()

                bp.push_info()
                num_blocks = bp.read_uint32()
                i = 0
                while i < num_blocks:
                    block = headers.MapBlock()
                    block.name = bp.read_string_lookback()
                    if block.name != 'Unassigned1':
                        game_class.blocks.append(block)

                    block.rotation = bp.read_byte()
                    block.position = headers.Vector3(
                        bp.read_byte(),
                        bp.read_byte(),
                        bp.read_byte()
                    )

                    if game_class.flags > 0:
                        block.flags = bp.read_uint32()
                    else:
                        block.flags = bp.read_uint16()

                    if block.flags == 0xFFFFFFFF:
                        continue

                    if (block.flags & 0x8000) != 0:
                        block.skin_author = bp.read_string_lookback()
                        block.skin = bp.read_int32()
                        if block.skin >= 0 and block.skin not in self.classes:
                            _class_id = bp.read_int32()
                            self._read_node(_class_id, block.skin, bp)

                        if (block.flags & 0x100000) != 0:
                            block.params = bp.read_int32()
                            if block.params >= 0 and block.params not in self.classes:
                                _class_id = bp.read_int32()
                                self._read_node(_class_id, block.params, bp)

                    i += 1

                self.positions['block_data'] = bp.pop_info()
            elif cid == 0x03043022:
                bp.skip(4)
            elif cid == 0x03043024:
                version = bp.read_byte()
                if version >= 3:
                    bp.skip(32)

                file_path = bp.read_string()
                if len(file_path) > 0 or version >= 3:
                    bp.read_string()
            elif cid == 0x03043025:
                bp.skip(4 * 4)
            elif cid == 0x03043026:
                idx = bp.read_int32()
                if idx >= 0 and idx not in self.classes:
                    _class_id = bp.read_int32()
                    self._read_node(_class_id, idx, bp)
            elif cid == 0x03043028:
                archive_gm_cam_val = bp.read_int32()
                if archive_gm_cam_val == 1:
                    bp.skip(1 + 4 * 7)

                bp.read_string()
            elif cid == 0x0304302A:
                bp.read_int32()
            elif cid == 0x3043040:
                bp.pos -= 4
                bp.push_info()
                bp.pos += 4
                self.positions['3043040_skipsize'] = bp.pop_info()

                item_bp = ByteReader(bp.data)
                item_bp.pos = bp.pos

                item_bp.skip(2 * 4)

                item_bp.push_info()
                item_bp.skip(2 * 4)

                num_items = item_bp.read_uint32()
                for i in range(num_items):
                    item_bp.skip(4 * 3)
                    item = headers.CGameBlockItem()
                    item.path = item_bp.read_string_lookback()
                    item.collection = item_bp.read_string_lookback()
                    item.author = item_bp.read_string_lookback()
                    item.rotation = item_bp.read_float()
                    item_bp.skip(15)

                    item.position = item_bp.read_vec3()

                    idx = item_bp.read_int32()
                    if idx >= 0:
                        self._read_node(0x2E009000, idx, item_bp)

                    item.waypoint = self.__current_waypoint
                    self.__current_waypoint = None

                    item_bp.skip(4 * 4 + 2)

                    self._read_node(0x3101004, 0, item_bp, add=False)

                    game_class.items.append(item)

                self.positions['items'] = item_bp.pop_info()
                item_bp.skip(4)
                bp.pos = item_bp.pos
            elif cid == 0x03059002 or cid == 0x2403A002:
                bp.read_string()
                for i in range(2):
                    version = bp.read_byte()
                    if version >= 3:
                        bp.skip(32)

                    file_path = bp.read_string()
                    # (?) according to https://wiki.xaseco.org/wiki/GBX
                    # we need to check if the file path is not empty
                    # here but it crashes reading the file for TM2 challenges
                    if len(file_path) > 0 and version >= 1:
                        bp.read_string()
            elif cid == 0x03043022:
                bp.read_int32()
            elif cid == 0x03043024:
                bp.read_byte()
                bp.skip(32)
                bp.read_string()
                bp.read_string()
            elif cid == 0x03043025:
                bp.skip(16)
            elif cid == 0x03043026:
                idx = bp.read_uint32()
                if idx >= 0 and idx not in self.classes:
                    _class_id = bp.read_int32()
                    self._read_node(_class_id, idx, bp)
            elif cid == 0x03043028:
                p = bp.read_int32()
                if p != 0:
                    bp.skip(1 + 4 * 3 * 3 + 4 * 3 + 4 + 4 + 4)

                bp.read_string()
            elif cid == 0x0304302A:
                bp.read_int32()
            elif cid == GbxType.WAYPOINT_SPECIAL_PROP or cid == 0x2E009000:
                version = bp.read_uint32()
                if version == 1:
                    game_class.spawn = bp.read_uint32()
                    game_class.order = bp.read_uint32()
                elif version == 2:
                    game_class.tag = bp.read_string()
                    game_class.order = bp.read_uint32()
            elif cid == 0x03059000:
                bp.read_string()
                bp.read_string()
            elif cid == 0x0303F005:
                self.read_ghost(game_class, bp)
            elif cid == 0x0303F006:
                bp.skip(4)
                self.read_ghost(game_class, bp)
            elif cid == 0x03093014:
                bp.skip(4)
                num_ghosts = bp.read_uint32()
                for _ in range(num_ghosts):
                    idx = bp.read_int32()
                    if idx >= 0 and idx not in self.classes:
                        _class_id = bp.read_uint32()
                        self._read_node(_class_id, idx, bp)

            elif cid == 0x03093002:
                map_gbx_size = bp.read_uint32()
                data = bytes(bp.read(map_gbx_size))
                game_class.track = Gbx(data)
            elif cid == 0x03092005:
                game_class.race_time = bp.read_uint32()
            elif cid == 0x03092008:
                game_class.num_respawns = bp.read_uint32()
            elif cid == 0x03092009:
                game_class.light_trail_color = bp.read_vec3()
            elif cid == 0x0309200A:
                game_class.stunts_score = bp.read_uint32()
            elif cid == 0x0309200E:
                game_class.uid = bp.read_string_lookback()
            elif cid == 0x0309200F:
                game_class.login = bp.read_string()
            elif skipsize != -1:
                bp.skip(skipsize)
                cid = oldcid
            else:
                return

    def read_ghost(self, game_class, bp):
        uncomp_sz = bp.read_uint32()
        comp_sz = bp.read_uint32()
        comp_data = bp.read(comp_sz)
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