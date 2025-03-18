import shutil
import os
import time
from PyQt5.QtCore import QRunnable, pyqtSlot, QObject, pyqtSignal
from src.utils.utils import Utils

class Signal(QObject):
    finished = pyqtSignal()


class SeparationWorker(QRunnable):  
    def __init__(self, pic_folders_path, jpeg_folder_path):
        super().__init__()
        self.utils = Utils()
        self.pic_folders_path = pic_folders_path
        self.jpeg_folder_path = jpeg_folder_path
        self.signal = Signal()

    @pyqtSlot()
    def run(self):
        jpeg_paths = []
        for folder_path in self.pic_folders_path:
            pic_paths = self.utils.get_glob_list(folder_path)
            jpeg_paths += [path for path in pic_paths if path.lower().endswith('.jpg')]
        for path in jpeg_paths:
            shutil.copy(path, os.path.join(self.jpeg_folder_path, os.path.basename(path)))
        self.signal.finished.emit()
