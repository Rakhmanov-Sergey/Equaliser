from PyQt5.QtCore import QThreadPool
from PyQt5.QtWidgets import QApplication

from music_utils import MusicUtils
from ui_controller import EqualizerWindow


class EqualizerApp:
    def __init__(self, bandwidth_count):
        self.music_utils = MusicUtils()

        self.app = QApplication([])
        self.window = EqualizerWindow(self.music_utils, bandwidth_count)

        self.music_worker = None
        self.thread_pool = QThreadPool()

    def run(self):
        self.window.show()
        self.app.exec_()


if __name__ == '__main__':
    app = EqualizerApp(10)
    app.run()


#
# app = EqualizerApp()
# app.create_ui()
#
# music_utils = MusicUtils("/Users/sergey/Cabinet/BMSTU/cos_kurs/cos_kurs_code/Resources/song_wav.wav")
# music_utils.init_music()
#
# app.play_music(music_utils)
#
#
