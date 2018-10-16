import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf, GLib

import pickle
import os, sys
import time, threading
import gbx
import blocks as bl
from config import NET_CONFIG
from block_offsets import rotate_track_tuples

IMG_SIZE = 30

class TrackVisualizationWindow(Gtk.Window):
    def __init__(self, current_idx):
        Gtk.Window.__init__(self, title='Visualization')
        self.timeout_ids = []
        self.denied = []
        self.rot_images = []
        self.current_idx = current_idx

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

        rebuild_button = Gtk.Button.new_with_label('Rebuild')
        rebuild_button.connect('clicked', lambda w: self.build())

        self.track_label = Gtk.Label('Track: ' + str(self.current_idx + 1) + ', ' + data[self.current_idx][0])

        sidebar = Gtk.Box.new(Gtk.Orientation.VERTICAL, 12)
        sidebar.set_valign (Gtk.Align.CENTER)
        sidebar.set_vexpand(True)
        sidebar.set_hexpand(True)
        sidebar.set_margin_left(12)
        sidebar.set_margin_right(12)
        sidebar.set_margin_bottom(12)
        sidebar.set_margin_top(12)
        sidebar.add(self.track_label)
        sidebar.add(accept_button)
        sidebar.add(discard_button)
        sidebar.add(rebuild_button)

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
        
    def on_accept(self, button):
        self.current_idx += 1
        if self.current_idx < len(data) - 1:
            self.build()
        self.track_label.set_label('Track: ' + str(self.current_idx + 1) + ', ' + data[self.current_idx][0])

    def on_discard(self, button):
        self.denied.append(data[self.current_idx][0])
        self.current_idx += 1
        if current_idx < len(data) - 1:
            self.build()
        self.track_label.set_label('Track: ' + str(self.current_idx + 1) + ', ' + data[self.current_idx][0])

    def on_destroy(self, window):
        print('Denied maps:')
        print(self.denied)
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

        track = data[self.current_idx][1]
        print(track)

        i = 1
        for block in track:
            self.timeout_ids.append(GLib.timeout_add(200 * i, self.add_block, block))
            i += 1

print('Loading training data...')
current_idx = 0
if len(sys.argv) > 1:
    if not sys.argv[1].isdigit():
        load_fname = sys.argv[1]
        track = pickle.load(open(load_fname, 'rb+'))
        data = [('', track)]
    else:
        data = pickle.load(open(NET_CONFIG['train_fname'], 'rb'))
        current_idx = int(sys.argv[1])

win = TrackVisualizationWindow(current_idx)
win.build()
win.show_all()

Gtk.main()