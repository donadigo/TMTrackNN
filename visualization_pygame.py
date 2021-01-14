import pygame
from block_utils import EDITOR_IDS
import pickle
import os
import sys

IMG_SIZE = 30

w = 32 * IMG_SIZE
h = 32 * IMG_SIZE


def rot_to_angle(rot):
    if rot == 1:
        return 270
    if rot == 2:
        return 180
    if rot == 3:
        return 90
    return 0


if len(sys.argv) <= 1:
    train_idx = 0
else:
    train_idx = int(sys.argv[1])
    
track = pickle.load(open('data/train_data.pkl', 'rb+'))[train_idx][1]
print(track)

arr_img = pygame.image.load('blocks-images/arr.jpg')
arr_img = pygame.transform.scale(arr_img, (10, 10))

screen = pygame.display.set_mode((w, h))

images = []
for block in track:
    try:
        eid = EDITOR_IDS[block[0]]
        f = eid + '.jpg'
    except KeyError:
        continue

    try:
        img = pygame.image.load(os.path.join('blocks-images', f))
        img = pygame.transform.scale(img, (IMG_SIZE, IMG_SIZE))

        images.append((img, block[1], block[2], block[3], block[4]))
    except pygame.error:
        img = pygame.image.load(os.path.join('blocks-images', 'empty.jpg'))
        img = pygame.transform.scale(img, (IMG_SIZE, IMG_SIZE))

        images.append((img, block[1], block[2], block[3], block[4]))
        continue


end = 1

running = True
frame = 0
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((255, 255, 255))
    for img in images[:end]:
        screen.blit(img[0], ((31 - img[1]) * IMG_SIZE,
                             (31 - img[3]) * IMG_SIZE))

        arr_img_r = pygame.transform.rotate(arr_img, rot_to_angle(img[4]))
        screen.blit(
            arr_img_r, ((31 - img[1]) * IMG_SIZE, (31 - img[3]) * IMG_SIZE))

    if frame % 100 == 0:
        end += 1
        end = min(end, len(track) - 1)

    pygame.display.flip()
    frame += 1

pygame.quit()
