import os
import pickle
import sys

from PyQt5.QtCore import Qt, QThread, pyqtSignal, QObject, QPoint
from PyQt5.QtGui import QIntValidator, QIcon
from PyQt5.QtWidgets import *

os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

def get_resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

if os.name == 'nt':
    import ctypes
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('com.github.donadigo.TMTrackNN')

class GenerateThread(QThread):
    progress_sig = pyqtSignal(int)
    status_sig = pyqtSignal(str, bool)

    def __init__(self):
        super(GenerateThread, self).__init__()
        self.progress_bar = None
        self.map_name = None
        self.length = 0
        self.variety = 0
        self.train_data = None
        self.pattern_data = None
        self.scaler = None
        self.stopped = False
        self.builder = None
        self.save_fname = None

    def progress_callback(self, completed, total):
        self.progress_sig.emit(int(completed / float(total) * 100))

    def run(self):
        self.stopped = False
        self.status_sig.emit('Initializing...', True)
        from builder import Builder
        from config import NET_CONFIG
        from savegbx import save_gbx

        from keras.models import load_model

        data_path = get_resource_path('data')
        if not self.scaler:
            self.status_sig.emit('Loading data...', True)
            with open(os.path.join(data_path, 'position_scaler.pkl'), 'rb') as scaler_file:
                self.scaler = pickle.load(scaler_file)

        if self.stopped:
            return

        if not self.pattern_data:
            with open(os.path.join(data_path, 'pattern_data.pkl'), 'rb') as pattern_file:
                self.pattern_data = pickle.load(pattern_file)


        if self.stopped:
            return

        models_path = get_resource_path('models')
        if not self.builder:
            self.status_sig.emit('Loading models...', True)
            block_model = load_model(os.path.join(models_path, 'block_model_300_300.h5'))
            pos_model = load_model(os.path.join(models_path, 'position_model_512_512_256.h5'))

            self.builder = Builder(block_model, pos_model,
                                   NET_CONFIG['lookback'], None, self.pattern_data, self.scaler, temperature=self.variety)

        if self.stopped:
            return

        self.status_sig.emit('Building...', False)
        track = self.builder.build(self.length, verbose=False, save=False,
                                   progress_callback=self.progress_callback)

        if track and self.save_fname:
            save_gbx({'track_data': track, 'map_name': self.map_name},
                     os.path.join(data_path, 'Template.Challenge.Gbx'), self.save_fname)
            self.status_sig.emit('Done.', False)

    def stop(self):
        self.stopped = True
        if self.builder:
            self.builder.stop()

        self.status_sig.emit('Stopped.', False)


class ProgressBar(QProgressBar):
    def __init__(self):
        super().__init__()
        self.setAlignment(Qt.AlignCenter)
        self._text = None

    def setText(self, text):
        self._text = text

    def text(self):
        return self._text


class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.width = 350
        self.height = 400

        self.setWindowTitle('TMTrackNN')
        self.setGeometry(0, 0, self.width, self.height)

        script_dir = os.path.dirname(os.path.realpath(__file__))
        icon = QIcon(os.path.join(script_dir, 'icon.ico'))
        self.setWindowIcon(icon)

        fg = self.frameGeometry()
        center = QDesktopWidget().availableGeometry().center()
        fg.moveCenter(center)
        self.move(fg.topLeft())

        self.name_edit = QLineEdit()

        self.temp_slider = QSlider(Qt.Horizontal)
        self.temp_slider.setMinimum(6)
        self.temp_slider.setMaximum(20)
        self.temp_slider.setValue(12)
        self.temp_slider.setToolTip(
            'Higher: more creative, less certain\nLower: more conservative, more certain')

        self.rd_time = QRadioButton('Track length')
        self.rd_time.setChecked(True)
        self.rd_time.toggled.connect(self.time_type_changed)

        self.rd_custom = QRadioButton('Custom')
        self.rd_custom.toggled.connect(self.time_type_changed)

        self.rd15 = QRadioButton('15 seconds')
        self.rd30 = QRadioButton('30 seconds')
        self.rd1 = QRadioButton('1 minute')
        self.rd1.setChecked(True)

        time_layout = QHBoxLayout()
        time_layout.addWidget(self.rd15)
        time_layout.addWidget(self.rd30)
        time_layout.addWidget(self.rd1)
        time_layout.setContentsMargins(35, 0, 35, 0)

        self.time_widget = QWidget()
        self.time_widget.setLayout(time_layout)

        self.length_spin_box = QSpinBox()
        self.length_spin_box.setMaximum(1000)
        self.length_spin_box.setValue(50)

        custom_layout = QFormLayout()
        custom_layout.setVerticalSpacing(12)
        custom_layout.setHorizontalSpacing(12)
        custom_layout.addRow('Number of blocks:', self.length_spin_box)
        custom_layout.setContentsMargins(35, 0, 0, 0)

        box_layout = QVBoxLayout()
        box_layout.addWidget(self.rd_time)
        box_layout.addWidget(self.time_widget)
        box_layout.addWidget(self.rd_custom)
        box_layout.addLayout(custom_layout)
        box_layout.setAlignment(Qt.AlignHCenter)

        self.generate_btn = QPushButton('Generate')
        self.generate_btn.clicked.connect(self.generate)

        self.stop_btn = QPushButton('Stop')
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.on_stop)

        self.progress_bar = ProgressBar()

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.progress_bar)
        button_layout.addWidget(self.stop_btn)
        button_layout.addWidget(self.generate_btn)
        button_layout.setAlignment(Qt.AlignRight | Qt.AlignBottom)

        main_layout = QVBoxLayout()

        form = QFormLayout()
        form.setEnabled(False)
        form.setVerticalSpacing(12)
        form.setHorizontalSpacing(12)
        form.addRow('Map name:', self.name_edit)
        form.addRow('Variety:', self.temp_slider)
        main_layout.addLayout(form)
        main_layout.addLayout(box_layout)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

        self.generate_thread = GenerateThread()
        self.generate_thread.finished.connect(self.generate_finished)
        self.generate_thread.progress_sig.connect(self.on_progress)
        self.generate_thread.status_sig.connect(self.on_status)

        self.time_type_changed()

    def time_type_changed(self):
        toggled = self.rd_time.isChecked()
        self.rd15.setEnabled(toggled)
        self.rd30.setEnabled(toggled)
        self.rd1.setEnabled(toggled)
        self.rd_custom.setChecked(not toggled)
        self.rd_time.setChecked(toggled)
        self.length_spin_box.setEnabled(not toggled)

    def on_stop(self):
        self.generate_thread.stop()

    def on_progress(self, completed):
        self.progress_bar.setValue(completed)

    def on_status(self, status, init_phase):
        if init_phase:
            self.progress_bar.setRange(0, 0)
        else:
            self.progress_bar.setRange(0, 100)

        self.progress_bar.setText(status)

    def generate_finished(self):
        self.generate_thread.quit()

        self.generate_btn.setEnabled(True)
        self.progress_bar.setValue(0)
        self.progress_bar.setRange(0, 100)
        self.stop_btn.setEnabled(False)
        self.time_widget.setEnabled(True)
        self.rd_time.setEnabled(True)
        self.rd_custom.setEnabled(True)
        self.name_edit.setEnabled(True)
        self.temp_slider.setEnabled(True)
        self.length_spin_box.setEnabled(True)
        self.setWindowTitle('TMTrackNN')
        self.time_type_changed()

    @staticmethod
    def get_tm_maps_dir():
        p = os.path.join(os.path.expanduser(
            '~'), 'Documents', 'Maniaplanet', 'Maps')
        if os.path.exists(p):
            return p

        p = os.path.join(os.path.expanduser(
            '~'), 'Documents', 'TrackMania', 'Tracks', 'Challenges')
        if os.path.exists(p):
            return p

        return None

    def generate(self):
        fname = QFileDialog.getSaveFileName(
            self, 'Choose save location', self.get_tm_maps_dir())[0]
        if fname == '':
            return
            
        basename = os.path.basename(fname)
        if not basename.endswith('.Challenge.Gbx') and not basename.endswith('.Map.Gbx'):
            fname += '.Challenge.Gbx'

        self.stop_btn.setEnabled(True)
        self.generate_btn.setEnabled(False)
        self.time_widget.setEnabled(False)
        self.rd_time.setEnabled(False)
        self.rd_custom.setEnabled(False)
        self.name_edit.setEnabled(False)
        self.temp_slider.setEnabled(False)
        self.length_spin_box.setEnabled(False)

        length = 0
        if self.rd_time.isChecked():
            if self.rd15.isChecked():
                length = 27
            elif self.rd30.isChecked():
                length = 50
            elif self.rd1.isChecked():
                length = 110
        elif self.rd_custom.isChecked():
            length = self.length_spin_box.value()

        map_name = self.name_edit.text()
        if map_name.strip() == '':
            map_name = basename.replace(
                '.Challenge.Gbx', '').replace('.Map.Gbx', '')

        self.generate_thread.save_fname = fname
        self.generate_thread.map_name = map_name
        self.generate_thread.variety = self.temp_slider.value() / 10.
        self.generate_thread.length = length

        self.setWindowTitle('TMTrackNN | Generating...')
        self.generate_thread.start()


app = QApplication(sys.argv)
window = Window()
window.show()
app.exec_()
