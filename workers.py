import time

from PyQt5.QtCore import QRunnable, pyqtSlot


class MusicWorker(QRunnable):
    @pyqtSlot()
    def run(self):
        print("Thread start")
        time.sleep(5)
        print("Thread complete")
