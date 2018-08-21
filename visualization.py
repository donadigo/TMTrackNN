import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf, GLib

import pickle
import os, sys
import time, threading
import gbx
import blocks as bl

IMG_SIZE = 30

load_fname = None

current_idx = 0
if len(sys.argv) > 1:
    if not sys.argv[1].isdigit():
        load_fname = sys.argv[1]
    else:
        current_idx = int(sys.argv[1])

denied = []
rot_images = []

print('Loading training data...')
if not load_fname:
    data = pickle.load(open('train-data.bin', 'r'))
else:
    data = [('', pickle.load(open(load_fname, 'r')))]

def on_button_press(w, event):
    x = int(event.x / IMG_SIZE)
    z = int(event.y / IMG_SIZE)

    images[x][z].set_opacity(0.3)
    
def on_accept(button):
    global current_idx
    current_idx += 1
    if current_idx < len(data) - 1:
        build()
    track_label.set_label('Track: ' + str(current_idx + 1) + ', ' + data[current_idx][0])

def on_discard(button):
    global current_idx, denied
    denied.append(data[current_idx][0])
    current_idx += 1
    if current_idx < len(data) - 1:
        build()
    track_label.set_label('Track: ' + str(current_idx + 1) + ', ' + data[current_idx][0])

def on_destroy(window):
    print('Denied maps:')
    print(denied)
    Gtk.main_quit()

win = Gtk.Window()
win.connect('destroy', on_destroy)

def build():
    for row in images:
        for img in row:
            img.set_from_pixbuf(None)
            img.set_pixel_size(IMG_SIZE)
            img.set_property('icon-size', IMG_SIZE)

    for rot_img in rot_images:
        rot_img.destroy()

    track = data[current_idx][1]
    print(track)

    # print(track)
    for block in track:
        try:
            name = bl.EDITOR_IDS[block[0]]
        except KeyError:
            continue

        x = block[1]
        if x < 0:
            x = -x
        z = block[3]
        if z < 0:
            z = -z

        if x > 31:
            x = 31
        if z > 31:
            z = 31

        if block[0] == bl.START_LINE_BLOCK:
            print('Start block: {}'.format (block))

        r = block[4]

        rot_pix = GdkPixbuf.Pixbuf.new_from_file_at_size('blocks-images/arr.jpg', 12, 12)
        if r == 1:
            rot_pix = rot_pix.rotate_simple(GdkPixbuf.PixbufRotation.CLOCKWISE)
        elif r == 2:
            rot_pix = rot_pix.rotate_simple(GdkPixbuf.PixbufRotation.UPSIDEDOWN)
        elif r == 3:
            rot_pix = rot_pix.rotate_simple(GdkPixbuf.PixbufRotation.COUNTERCLOCKWISE)

        rot_img = Gtk.Image.new_from_pixbuf(rot_pix)
        rot_img.set_halign(Gtk.Align.END)
        rot_img.set_valign(Gtk.Align.END)
        rot_images.append(rot_img)
        overlays[31 - x][31 - z].add_overlay(rot_img)

        if os.path.isfile('blocks-images/{}.jpg'.format(name)):
            pix = GdkPixbuf.Pixbuf.new_from_file_at_size('blocks-images/{}.jpg'.format(name), IMG_SIZE, IMG_SIZE)
            images[31 - x][31 - z].set_from_pixbuf(pix)
        else:
            pix = GdkPixbuf.Pixbuf.new_from_file_at_size('blocks-images/empty.jpg', IMG_SIZE, IMG_SIZE)
            images[31 - x][31 - z].set_from_pixbuf(pix)

        win.show_all()

board = Gtk.Grid()

evbox = Gtk.EventBox()
evbox.add_events(256)
evbox.connect('button-press-event', on_button_press)
evbox.add(board)

images = [[None for x in range(32)] for y in range(32)]
overlays = [[None for x in range(32)] for y in range(32)]
for i in range(32):
    for j in range(32):
        overlay = Gtk.Overlay()
        overlay.add_events(256)
        img = Gtk.Image()
        img.add_events(256)
        img.set_pixel_size(IMG_SIZE)
        img.set_property('icon-size', IMG_SIZE)
        img.connect('button_press_event', on_button_press)
        images[i][j] = img

        overlay.add(img)

        overlays[i][j] = overlay
        board.attach(overlay, i, j, 1, 1)

sep = Gtk.Separator.new(Gtk.Orientation.VERTICAL)

accept_button = Gtk.Button.new_with_label('Accept')
accept_button.get_style_context ().add_class ('suggested-action')
accept_button.set_valign (Gtk.Align.START)
accept_button.connect('clicked', on_accept)

discard_button = Gtk.Button.new_with_label('Discard')
discard_button.get_style_context ().add_class ('destructive-action')
discard_button.connect('clicked', on_discard)

track_label = Gtk.Label('Track: ' + str(current_idx + 1) + ', ' + data[current_idx][0])

sidebar = Gtk.Box.new(Gtk.Orientation.VERTICAL, 12)
sidebar.set_valign (Gtk.Align.CENTER)
sidebar.set_vexpand(True)
sidebar.set_hexpand(True)
sidebar.set_margin_left(12)
sidebar.set_margin_right(12)
sidebar.set_margin_bottom(12)
sidebar.set_margin_top(12)
sidebar.add(track_label)
sidebar.add(accept_button)
sidebar.add(discard_button)

grid = Gtk.Grid()
grid.attach(evbox, 0, 0, 1, 1)
grid.attach(sep, 1, 0, 1, 1)
grid.attach(sidebar, 2, 0, 1, 1)

win.add(grid)
win.show_all()

build()

Gtk.main()