import os
import pickle
import sys
import threading
import time

from keras.models import load_model

import core.stadium_blocks as bl
import core.gbx as gbx
from builder import Builder
from config import load_config

import gi
gi.require_version('Gtk', '3.0')

from gi.repository import GdkPixbuf, GLib, Gtk

IMG_SIZE = 30

class LiveBuildWindow(Gtk.Window):
    def __init__(self, block_model, pos_model, lookback, pattern_data, scaler):
        Gtk.Window.__init__(self, title='Live Build')
        self.timeout_ids = []
        self.rot_images = []
        self.lookback = lookback
        self.builder = Builder(block_model, pos_model, self.lookback, None, pattern_data, scaler, reset=False)
        self.track = []

        board = Gtk.Grid()

        evbox = Gtk.EventBox()
        evbox.add_events(256)
        evbox.connect('button-press-event', self.on_button_press)
        evbox.add(board)

        self.images = [[None for x in range(32)] for y in range(32)]
        self.overlays = [[None for x in range(32)] for y in range(32)]
        for i in range(32):
            for j in range(32):
                overlay = Gtk.Overlay()
                overlay.add_events(256)
                img = Gtk.Image()
                img.add_events(256)
                img.set_pixel_size(IMG_SIZE)
                img.set_property('icon-size', IMG_SIZE)
                img.connect('button_press_event', self.on_button_press)
                self.images[i][j] = img

                overlay.add(img)

                self.overlays[i][j] = overlay
                board.attach(overlay, i, j, 1, 1)

        sep = Gtk.Separator.new(Gtk.Orientation.VERTICAL)

        accept_button = Gtk.Button.new_with_label('Accept')
        accept_button.get_style_context ().add_class ('suggested-action')
        accept_button.set_valign (Gtk.Align.START)
        accept_button.connect('clicked', self.on_accept)

        discard_button = Gtk.Button.new_with_label('Discard')
        discard_button.get_style_context ().add_class ('destructive-action')
        discard_button.connect('clicked', self.on_discard)

        clear_button = Gtk.Button.new_with_label('Clear')
        clear_button.connect('clicked', self.on_clear)

        track_label = Gtk.Label()

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
        sidebar.add(clear_button)

        grid = Gtk.Grid()
        grid.attach(evbox, 0, 0, 1, 1)
        grid.attach(sep, 1, 0, 1, 1)
        grid.attach(sidebar, 2, 0, 1, 1)

        self.add(grid)
        self.connect('destroy', self.on_destroy)

    def on_button_press(self, w, event):
        x = int(event.x / IMG_SIZE)
        z = int(event.y / IMG_SIZE)

        self.images[x][z].set_opacity(0.3)
        
    def on_clear(self, button):
        self.builder.gmap = None
        self.track = []
        self.build()

    def on_accept(self, button):
        self.track = self.builder.build(len(self.track) + 1, put_finish=False, failsafe=False)
        self.build()

    def on_discard(self, button):
        self.builder.gmap.pop()
        self.track = self.builder.build(len(self.track), put_finish=False, failsafe=False)
        self.build()

    def on_destroy(self, window):
        Gtk.main_quit()

    def add_block(self, block):
        try:
            name = bl.EDITOR_IDS[block[0]]
        except KeyError:
            return

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
        self.rot_images.append(rot_img)
        self.overlays[31 - x][31 - z].add_overlay(rot_img)

        if os.path.isfile('blocks-images/{}.jpg'.format(name)):
            pix = GdkPixbuf.Pixbuf.new_from_file_at_size('blocks-images/{}.jpg'.format(name), IMG_SIZE, IMG_SIZE)
            self.images[31 - x][31 - z].set_from_pixbuf(pix)
        else:
            pix = GdkPixbuf.Pixbuf.new_from_file_at_size('blocks-images/empty.jpg', IMG_SIZE, IMG_SIZE)
            self.images[31 - x][31 - z].set_from_pixbuf(pix)

        self.show_all()

    def build(self):
        for tid in self.timeout_ids:
            GLib.Source.remove(tid)
        
        self.timeout_ids = []

        for row in self.images:
            for img in row:
                img.set_from_pixbuf(None)
                img.set_pixel_size(IMG_SIZE)
                img.set_property('icon-size', IMG_SIZE)

        for rot_img in self.rot_images:
            rot_img.destroy()

        i = 1
        for block in self.track:
            self.add_block(block)
            i += 1

if len(sys.argv) > 2:
    block_model_fname = sys.argv[1]
    pos_model_fname = sys.argv[2]
    config_fname = sys.argv[3]
else:
    print(f'Usage: ./{sys.argv[0]} block-model-filename position-model-filename config-filename')
    quit()

block_model = load_model(block_model_fname)
pos_model = load_model(pos_model_fname)
config = load_config(config_fname)

pattern_data = pickle.load(open(config['pattern_data'], 'rb'))
scaler = pickle.load(open(config['position_scaler'], 'rb'))

block_model.summary()
pos_model.summary()

win = LiveBuildWindow(block_model, pos_model, config['lookback'], pattern_data, scaler)
win.build()
win.show_all()

Gtk.main()

pickle.dump(win.track, open('generated-track.bin', 'wb+'))
