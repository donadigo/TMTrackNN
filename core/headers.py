from core.block_utils import BID, BX, BY, BZ, BROT, BFLAGS, get_block_name
from core.stadium_blocks import STADIUM_BLOCKS
import math


class CGameHeader(object):
    def __init__(self, id):
        self.id = id


class CGameCtnCollectorList(object):
    def __init__(self, id):
        self.id = id
        self.stocks = []


class CollectorStock(object):
    def __init__(self, block_name, collection, author):
        self.block_name = block_name
        self.collection = collection
        self.author = author


class MapBlock(object):
    @staticmethod
    def from_tup(tup):
        block = MapBlock()
        block.name = get_block_name(tup[BID], STADIUM_BLOCKS)
        block.rotation = tup[BROT]
        block.position = Vector3(tup[BX], tup[BY], tup[BZ])
        if len(tup) > 5:
            block.flags = 0x1000 if tup[BFLAGS] == 1 else 0
        return block

    def __init__(self):
        self.name = None
        self.rotation = 0
        self.position = Vector3()
        self.speed = 0
        self.flags = 0
        self.params = 0
        self.skin_author = None
        self.skin = 0

    # 0b1000000000000
    # (flags & 0x1000) != 0     is on terrain
    # (flags & 0x1) != 0        connected once with another RoadMain
    # (flags & 0x2) != 0        connected twice with blocks (curve line)
    # (flags & 0x3) != 0        connected twice with blocks (straight line)
    # (flags & 0x4) != 0        connected three times with blocks
    # (flags & 0x5) != 0        connected four times with blocks
    # 6?
    # (flags & 0x7) == 0        not connected to any blocks
    def __str__(self):
        return (
            'Name: {}\n'
            'Rotation: {}\n'
            'Position: {}\n'
            'Flags: {}\n'
        ).format(self.name, self.rotation, self.position.as_array(), bin(self.flags))

    def to_tup(self):
        try:
            return (STADIUM_BLOCKS[self.name], self.position.x, self.position.y, self.position.z, self.rotation, self.flags, self.speed)
        except KeyError:
            return None


class Vector3(object):
    def __init__(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z

    def add(self, other):
        return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)

    def subtract(self, other):
        return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)

    def __getitem__(self, key):
        if key == 0:
            return self.x
        elif key == 1:
            return self.y
        elif key == 2:
            return self.z
        return None

    def __eq__(self, other):
        if isinstance(other, list):
            return self.x == other[0] and self.y == other[1] and self.z == other[2]

        return self.x == other.x and self.y == other.y and self.z == other.z

    def as_array(self):
        return [self.x, self.y, self.z]


class CGameChallenge(CGameHeader):
    def __init__(self, id):
        self.id = id
        self.times = {}
        self.map_uid = None
        self.environment = None
        self.map_author = None
        self.map_name = None
        self.mood = None
        self.env_bg = None
        self.env_author = None
        self.map_size = ()
        self.flags = 0
        self.req_unlock = 0
        self.blocks = []
        self.items = []
        self.password_hash = None
        self.password_crc = None


class CGameBlockItem(CGameHeader):
    def __init__(self):
        self.id = id
        self.path = None
        self.collection = None
        self.author = None
        self.waypoint = None
        self.position = Vector3()
        self.rotation = 0.0


class CGameWaypointSpecialProperty(CGameHeader):
    def __init__(self, id):
        self.id = id
        self.tag = None
        self.spawn = 0
        self.order = 0


class CGameCommon(CGameHeader):
    def __init__(self, id):
        self.id = id
        self.track_name = None


class CGameReplayRecord(CGameCommon):
    def __init__(self, id):
        self.id = id
        self.track = None
        self.nickname = None
        self.driver_login = None


class CGameGhost(CGameHeader):
    def __init__(self, id):
        self.id = id
        self.records = []
        self.sample_period = None


class CGameCtnGhost(CGameGhost):
    def __init__(self, id):
        self.id = id
        self.race_time = 0
        self.num_respawns = 0
        self.light_trail_color = Vector3()
        self.stunts_score = 0
        self.uid = None
        self.login = None
        self.cp_times = []
        self.control_entries = []
        self.control_names = []
        self.events_duration = 0
        super(CGameCtnGhost, self).__init__(id)

class ControlEntry(object):
    def __init__(self, time, event_name, enabled, flags):
        self.time = time
        self.event_name = event_name
        self.enabled = enabled
        self.flags = flags

class GhostSampleRecord(object):
    BLOCK_SIZE_XZ = 32
    BLOCK_SIZE_Y = 8

    def __init__(self, position, angle, axis_heading, axis_pitch, speed, vel_heading, vel_pitch):
        self.position = position
        self.angle = angle
        self.axis_heading = axis_heading
        self.axis_pitch = axis_pitch
        self.speed = speed
        self.vel_heading = vel_heading
        self.vel_pitch = vel_pitch

    @property
    def display_speed(self):
        if self.speed == 0x8000:
            return 0

        return int(abs(math.exp(self.speed / 1000.0) * 3.6))

    def get_block_position(self, xoff=0, yoff=0, zoff=0):
        x = int((self.position.x + xoff) / self.BLOCK_SIZE_XZ)
        y = int((self.position.y + yoff) / self.BLOCK_SIZE_Y)
        z = int((self.position.z + zoff) / self.BLOCK_SIZE_XZ)
        return Vector3(x, y, z)
