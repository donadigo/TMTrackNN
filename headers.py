from blocks import BLOCKS


class CGameHeader(object):
    def __init__(self, id):
        self.id = id


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

    def __init__(self):
        self.name = None
        self.rotation = 0
        self.position = []
        self.flags = 0
        self.params = 0
        self.skin_author = None
        self.skin = 0

    # 0b1000000000000
    # (flags & 0x1000) != 0     is on ground
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
            return (BLOCKS[self.name], self.position[0], self.position[1], self.position[2], self.rotation)
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


class CGameCommon(CGameHeader):
    def __init__(self, id):
        self.id = id
        self.track_name = None
