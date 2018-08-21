f = open('blockdata.txt')

blocks = []
editor_ids = []

lines = f.readlines()
for line in lines:
    line = line.rstrip().replace('\t', ' ')
    tokens = line.split(' ')
    blocks.append(tokens[0])
    editor_ids.append(tokens[1])

buff = 'BLOCKS = {\n'

def write_python_dict(li, name, swap):
    buff = name + ' = {\n'
    for i in range(len(li)):
        if i == len(li) - 1:
            end = '\n'
        else:
            end = ',\n'

        k = '\'' + li[i] + '\''
        v = str(i+1)
        if swap:
            k = str(i+1)
            v = '\'' + li[i] + '\''

        buff += '\t' + k + ': ' + v + end
    buff += '}\n'

    return buff
    

res = write_python_dict(blocks, 'BLOCKS', False)
res += '\n'
res += write_python_dict(editor_ids, 'EDITOR_IDS', True)

print(res)