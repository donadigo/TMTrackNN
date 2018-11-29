from blocks import BLOCKS, BID, BX, BY, BZ, BROT, BFLAGS, get_block_name


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
    def rotation_to_deg(rotation):
        if rotation == 1:
            return 90
        elif rotation == 2:
            return 180
        elif rotation == 3:
            return 270

        return 0

    @staticmethod
    def from_tup(tup):
        block = MapBlock()
        block.name = get_block_name(tup[BID])
        block.rotation = tup[BROT]
        block.position = [tup[BX], tup[BY], tup[BZ]]
        if len(tup) > 5:
            block.flags = 0x1000 if tup[BFLAGS] == 1 else 0
        return block

    def __init__(self):
        self.name = None
        self.rotation = 0
        self.position = []
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
        ).format(self.name, self.rotation, self.position, bin(self.flags))

    def to_tup(self):
        try:
            terrain_bit = 1 if (self.flags & 0x1000 != 0) else 0
            return (BLOCKS[self.name], self.position[0], self.position[1], self.position[2], self.rotation, terrain_bit)
        except KeyError:
            return None


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


class CGameBlockItem(CGameHeader):
    def __init__(self):
        self.id = id
        self.path = None
        self.collection = None
        self.author = None
        self.waypoint = None
        self.position = (0, 0, 0)
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
        self.ghosts = []


class CGameGhost(object):
    def __init__(self, id):
        self.id = id
        self.records = []


class CGameCtnGhost(CGameGhost):
    def __init__(self, id):
        self.id = id
        self.race_time = 0
        self.num_respawns = 0
        self.light_trail_color = (0, 0, 0)
        self.stunts_score = 0
        self.uid = None
        self.login = None
        super(CGameCtnGhost, self).__init__(id)


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

    def get_block_position(self, xoff=0, zoff=0):
        x = int((self.position[0] + xoff) / self.BLOCK_SIZE_XZ)
        y = int((self.position[1]) / self.BLOCK_SIZE_Y)
        z = int((self.position[2] + zoff) / self.BLOCK_SIZE_XZ)
        return [x, y, z]
