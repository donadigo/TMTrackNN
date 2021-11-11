from pygbx.headers import Vector3
from block_utils import BID, BROT, BX, BY, BZ
from track_utils import occupied_track_vectors


class GameMap(object):
    '''
    The GameMap class is responsible for managing the track as it is
    built in the main building loop. 
    '''
    def __init__(self, size: Vector3, start_pos: Vector3):
        self.size = size
        self.track = []
        self.decoded = []
        self.occupied = []
        self.start_pos = start_pos

    def __getitem__(self, key):
        return self.track[key]
    
    def __len__(self):
        return len(self.track)

    def add(self, block):
        self.track.append(block)
        self.update()

    def pop(self):
        self.track.pop()

    def get_bounds(self):
        min_vector = self.occupied[0]
        max_vector = self.occupied[1]

        for i in range(1, len(self.occupied)):
            off = self.occupied[i]
            min_vector.x = min(min_vector.x, off.x)
            min_vector.y = min(min_vector.y, off.y)
            min_vector.z = min(min_vector.z, off.z)
            max_vector.x = max(max_vector.x, off.x)
            max_vector.y = max(max_vector.y, off.y)
            max_vector.z = max(max_vector.z, off.z)

        return min_vector, max_vector

    def __decode(self):
        d = self.track[:]
        d[0] = (d[0][BID], self.start_pos.x, self.start_pos.y,
                self.start_pos.z, d[0][BROT])
        for i in range(1, len(d)):
            block = d[i]
            prev = d[i - 1]
            d[i] = (block[BID],
                    block[BX] + prev[BX],
                    block[BY] + prev[BY],
                    block[BZ] + prev[BZ],
                    block[BROT])
        return d

    def center(self):
        min_vector, max_vector = self.get_bounds()

        min_vector.y -= 1
        max_vector.y -= 1

        cx = 32 - (max_vector.x - min_vector.x + 1)
        if cx > 0:
            cx = int(cx / 2)
        cz = 32 - (max_vector.z - min_vector.z + 1)
        if cz > 0:
            cz = int(cz / 2)

        min_vector.x = 0 if min_vector.x >= 0 else min_vector.x
        min_vector.y = 0 if min_vector.y >= 0 else min_vector.y
        min_vector.z = 0 if min_vector.z >= 0 else min_vector.z

        max_vector.x = 0 if max_vector.x < 32 else max_vector.x - 31
        max_vector.y = 0 if max_vector.y < 32 else max_vector.y - 31
        max_vector.z = 0 if max_vector.z < 32 else max_vector.z - 31

        xoff = min_vector.x - max_vector.x
        zoff = min_vector.z - max_vector.z

        p = []
        for block in self.decoded:
            p.append((block[BID], block[BX] - xoff + cx, block[BY],
                      block[BZ] - zoff + cz, block[BROT]))

        return p

    def exceeds_map_size(self):
        min_vector, max_vector = self.get_bounds()
        return (max_vector.x - min_vector.x + 1 > self.size.x or
                max_vector.y - min_vector.y + 1 > self.size.y or
                max_vector.z - min_vector.z + 1 > self.size.z or
                min_vector.y < 1)

    def update(self):
        self.decoded = self.__decode()
        self.occupied = occupied_track_vectors(self.decoded)
