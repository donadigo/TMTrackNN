# from core.blocks import BLOCKS
# from core.blocks import GROUND_BLOCKS
# from core.block_offsets import BLOCK_OFFSETS

# contents = 'const std::string BLOCKS[] = {\n'
# for name in BLOCKS:
#     contents += '\t\"' + name + '\",\n'

# contents += '};\n\n'
# contents += 'const std::map<std::string, std::vector<Vector3i>> BLOCK_OFFSETS = {\n'
# for j, name in enumerate(BLOCK_OFFSETS):
#     s = '\t{ \"' + name + '\", {'
#     for i, off in enumerate(BLOCK_OFFSETS[name]):
#         s += '{ '
#         s += str(off[0]) + ', '
#         s += str(off[1]) + ', '
#         s += str(off[2])
#         s += ' }'

#         if i < len(BLOCK_OFFSETS[name]) - 1:
#             s += ', '

#     s += '} }'
#     if j < len(BLOCK_OFFSETS) - 1:
#         s += ','

#     contents += s + '\n'
# contents += '};\n\n'
# # print('\t{ \"' + name + '\", ' + BLOCK_OFFSETS[name])

# contents += 'const std::vector<int> GROUND_BLOCKS = { '
# for i, bid in enumerate(GROUND_BLOCKS):
#     contents += str(bid)
#     if i < len(GROUND_BLOCKS) - 1:
#         contents += ', '
# contents += ' };\n'

# with open('StadiumBlocks.h', 'w+') as f:
#     f.write(contents)

import json
import pickle

d = []

data = pickle.load(open('../data/pattern_data.pkl', 'rb'))
for key in data:
    arr = [int(key[0])]
    arr.append(int(key[1][0]))
    arr.append(int(key[1][1]))
    arr.append(int(key[1][2]))
    arr.append(int(key[1][3]))
    arr.append(int(key[1][4]))
    arr.append(int(data[key]))
    d.append(arr)

obj = {"data": d}

json.dump(obj, open('pattern_data.json', 'w+'))