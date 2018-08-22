import pickle
import sys
import blocks

if len(sys.argv) < 2:
    print('No filename specified.')
    quit()

if len(sys.argv) < 3:
    print('No output filename specified.')
    quit()

track = pickle.load(open(sys.argv[1], 'rb'))
f = open(sys.argv[2], 'w+')
for block in track:
    f.write('{}: X: {}, Y: {}, Z: {}, R: {}\n'.format(blocks.EDITOR_IDS[block[0]], block[1], block[2], block[3], block[4]))

f.close()
