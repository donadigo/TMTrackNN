from blocks import BLOCKS

TECH_BLOCK_WEIGHTS = [1.0] * len(BLOCKS)

# StadiumRoadMain
TECH_BLOCK_WEIGHTS[6-1] = 0.5

# StadiumPlatformTo*
TECH_BLOCK_WEIGHTS[127-1] = 0.7
TECH_BLOCK_WEIGHTS[128-1] = 0.7
TECH_BLOCK_WEIGHTS[129-1] = 0.7


# Circuit blocks
for i in range(131, 195+1):
    TECH_BLOCK_WEIGHTS[i-1] = 27

# StadiumPlatformToRoadMain
TECH_BLOCK_WEIGHTS[130-1] = 18

# StadiumCircuitBase
TECH_BLOCK_WEIGHTS[136-1] = 25

# Dirt blocks
for i in range(196, 233+1):
    TECH_BLOCK_WEIGHTS[i-1] = 120

# Decoration blocks that can be used to build
for i in range(264, 279+1):
    TECH_BLOCK_WEIGHTS[i-1] = 5
