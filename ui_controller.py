import time

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileDialog

from UI.main_screen import Ui_MainWindow
from music_utils import MusicUtils


class EqualizerWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    freq_labels = []
    freq_sliders = []
    freq_values = []
    bandwidths = []

    def __init__(self, music_utils: MusicUtils, bandwidth_count, *args, **kwargs):
        super(EqualizerWindow, self).__init__(*args, **kwargs)
        self.music_utils = music_utils

        self.setupUi(self)
        self.prepare_sliders(bandwidth_count)
        self.set_click_listeners()

    def prepare_sliders(self, bandwidth_count):
        self.bandwidths = MusicUtils.init_bandwidth(bandwidth_count, 0, 22000)
        labels_layout = self.freq_labels_layout
        sliders_layout = self.slider_layout
        values_layout = self.freq_values_layout
        for i in range(10):
            label = labels_layout.itemAt(i)
            slider = sliders_layout.itemAt(i)
            value = values_layout.itemAt(i)
            if i < bandwidth_count:
                label.widget().setText(str(self.bandwidths[i-1]) + " - " + str(self.bandwidths[i]) + "Hz" if i > 0
                                       else "0 - " + str(self.bandwidths[i]) + "Hz")
                self.freq_labels.append(label.widget())
                self.freq_sliders.append(slider.widget())
                self.freq_values.append(value.widget())
            else:
                label.widget().deleteLater()
                slider.widget().deleteLater()
                value.widget().deleteLater()

    def set_click_listeners(self):
        self.song_name_text.mousePressEvent = lambda event: self.select_music_file()
        self.play_pause_button.clicked.connect(self.control_music_player)
        self.stop_button.clicked.connect(self.control_music_player)
        for slider in self.freq_sliders:
            slider.sliderReleased.connect(self.control_equaliser)

    def select_music_file(self):
        path = QFileDialog.getOpenFileName(QFileDialog(), caption="Select music file")[0]
        if path != '':
            self.music_utils.music_file_path = path
            self.music_utils.load_music()
        else:
            self.music_utils.music_file_path = None
        self.update_music_file_loaded_state(not(self.music_utils.music_file_path is None))

    def control_music_player(self):
        if self.sender() == self.play_pause_button and not self.music_utils.music_is_playing and not self.music_utils.music_is_paused:
            self.music_utils.play_music()
            self.play_pause_button.setText("Пауза")
        elif self.sender() == self.play_pause_button and not self.music_utils.music_is_playing and self.music_utils.music_is_paused:
            self.music_utils.unpause_music()
            self.play_pause_button.setText("Пауза")
        elif self.sender() == self.play_pause_button and self.music_utils.music_is_playing:
            self.music_utils.pause_music()
            self.play_pause_button.setText("Продолжить")
        elif self.sender() == self.stop_button:
            self.music_utils.stop_music()
            self.play_pause_button.setText("Воспроизвести")

    def update_music_file_loaded_state(self, load_state):
        self.play_pause_button.setEnabled(load_state)
        self.stop_button.setEnabled(load_state)
        self.effect_1_checkbox.setEnabled(load_state)
        self.effect_2_checkbox.setEnabled(load_state)
        self.song_name_text.setText(self.music_utils.music_file_path.split("/")[-1] if load_state else "Выберите песню")

    def control_equaliser(self):
        slider_index = self.freq_sliders.index(self.sender())
        low_freq = self.bandwidths[slider_index - 1] if slider_index > 0 else 0
        high_freq = self.bandwidths[slider_index]
        value = self.freq_sliders[slider_index].value()
        self.freq_values[slider_index].setText(str(value) + " dB")
        self.music_utils.equaliser_music_edit(low_freq, high_freq, value)
        self.music_utils.update_music()

