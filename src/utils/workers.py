import os
import shutil
import sys
import time
from PIL import Image, ExifTags
from PyQt5.QtCore import QRunnable, pyqtSlot, QObject, pyqtSignal
from src.utils.utils import Utils

class Signal(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(str)

class SeparationWorker(QRunnable):  
    def __init__(self, pic_folders_path, JPEG_FOLDER_PATH):
        super().__init__()
        self.utils = Utils()
        self.signal = Signal()
        self.pic_folders_path = pic_folders_path
        self.JPEG_FOLDER_PATH = JPEG_FOLDER_PATH

    @pyqtSlot()
    def run(self):
        jpeg_paths = []
        for folder_path in self.pic_folders_path:
            pic_paths = self.utils.get_glob_list(folder_path)
            jpeg_paths += [path for path in pic_paths if path.lower().endswith('.jpg')]
        for path in jpeg_paths:
            shutil.copy(path, os.path.join(self.JPEG_FOLDER_PATH, os.path.basename(path)))
        self.signal.finished.emit()
        return


class StorageWorker(QRunnable):
    def __init__(self, JPEG_FOLDER_PATH, pic_folders_path, event_name, photo_format, semi_auto_mode, event_date, part):
        super().__init__()
        self.utils = Utils()
        self.signal = Signal()
        self.JPEG_FOLDER_PATH = JPEG_FOLDER_PATH
        self.pic_folders_path = pic_folders_path
        self.event_name = event_name
        self.photo_format = photo_format
        self.semi_auto_mode = semi_auto_mode
        self.initialize_date_attr(event_date)
        self.part = part
        self.external_storage_jpeg_path = os.path.join(self.utils.get_event_dir_path(self.day, self.month, self.year, self.event_name), 'OG', 'JPEG')
        self.external_storage_raw_path = os.path.join(self.utils.get_event_dir_path(self.day, self.month, self.year, self.event_name), 'OG', 'RAW')

    def initialize_date_attr(self, UI_event_date):
        '''Initialize date, month and day based on event_date'''
        if not self.semi_auto_mode:  # Auto mode
            if self.photo_format == 'RJ' or self.photo_format == 'J':
                path = self.utils.get_glob_list(self.JPEG_FOLDER_PATH)[0]  # get the first path containing '.JPEG'
                event_date = Image.open(path)._getexif()[36867]       
                event_date = event_date.split(' ')[0].split(':')
            else:
                event_date = UI_event_date.split('/')
                event_date.reverse()  
        else:  # Semi auto mode
            event_date = UI_event_date.split('/').reverse()
        self.year, self.month, self.day = event_date  # Initialize day, month, year

    @pyqtSlot()
    def run(self):
        ''''''
        if self.semi_auto_mode:  # Semi auto mode
            if self.photo_format == 'RJ':
                pass
            elif self.photo_format == 'J':
                pass
            elif self.photo_format == 'R':
                pass
        else:  # Auto mode
            print('AUTO MODE')
            self.create_event_dirs()
            try:
                if self.photo_format == 'RJ':
                        self.store_raw_and_jpeg()                    
                elif self.photo_format == 'J':
                        self.store_jpeg()
                elif self.photo_format == 'R':
                    self.store_raw()
            except Exception as e:
                self.signal.error.emit(f"Erreur lors du déplacement des photos : {e}")
                return

        self.signal.finished.emit()
        return
    
    def store_raw_and_jpeg(self, part='full'):
        '''FULL PART ONLY FOR NOW'''
        nj = 0
        nr = 0
        jpeg_paths = self.utils.get_glob_list(self.JPEG_FOLDER_PATH)
        for jpeg_path in jpeg_paths:
            new_jpeg_path = os.path.join(self.external_storage_jpeg_path, jpeg_path.split('/')[-1].strip())
            shutil.copy(jpeg_path, new_jpeg_path)  # Copy jpeg
            nj += 1
            raw_path = self.utils.get_equivalent_raw_path(jpeg_path, self.pic_folders_path)
            if raw_path:
                new_raw_path = os.path.join(self.external_storage_raw_path, raw_path.split('/')[-1].strip())
                shutil.copy(raw_path, new_raw_path)  # Copy raw
                nr += 1
        print(f"{nj} JPEG STORED")
        print(f"{nr} RAW STORED")

    def store_jpeg(self, part='full'):  # A TESTER
        '''FULL PART ONLY FOR NOW'''
        nj = 0
        jpeg_paths = self.utils.get_glob_list(self.JPEG_FOLDER_PATH)
        for jpeg_path in jpeg_paths:
            new_jpeg_path = os.path.join(self.external_storage_jpeg_path, jpeg_path.split('/')[-1].strip())
            shutil.copy(jpeg_path, new_jpeg_path)  # Copy jpeg
            nj += 1
        print(f"{nj} JPEG STORED")

    def store_raw(self, part='full'):  # A TESTER
        '''FULL PART ONLY FOR NOW'''
        nr = 0
        raw_paths = self.utils.get_raw_paths(self.pic_folders_path)
        for raw_path in raw_paths:
            new_raw_path = os.path.join(self.external_storage_raw_path, raw_path.split('/')[-1].strip())
            shutil.copy(raw_path, new_raw_path)  # Copy raw
            nr += 1
        print(f"{nr} RAW STORED")

    def create_event_dirs(self):
        '''
        Creates all the following directories if necessary.

        - Year (if necessary)
            - Month (if necessary)
                - Event
                    - OG
                        - JPEG
                        - RAW
                    - RT
        '''
        year_dir_path = os.path.join(self.utils.get_external_storage_base_dir(), self.year)
        month_dir_path = os.path.join(year_dir_path, self.utils.get_month_dir_name(self.month))
        event_dir_path = os.path.join(month_dir_path, f"{self.day}:{self.month} {self.event_name}")
        try:
            if not os.path.exists(year_dir_path): 
                os.mkdir(year_dir_path)
            if not os.path.exists(month_dir_path):
                os.mkdir(month_dir_path)
            os.mkdir(event_dir_path)
            for dir in self.utils.get_external_storage_event_dirs():
                os.mkdir(os.path.join(event_dir_path, dir))
        except Exception as e:
            self.signal.error.emit(f"[create_event_dirs] Erreur lors de la création d'un dossier : {e}")
            return
        print('DIR CREATED')


class RemoveWorker(QRunnable):
    def __init__(self, JPEG_FOLDER_PATH, camera_storage_path):
        super().__init__()
        self.utils = Utils()
        self.signal = Signal()
        self.JPEG_FOLDER_PATH = JPEG_FOLDER_PATH
        self.camera_storage_path = camera_storage_path
        print(camera_storage_path)
    
    @pyqtSlot()
    def run(self):
        try :
            # Remove jpegs from self.JPEG_FOLDER_PATH
            jpegs = self.utils.get_glob_list(self.JPEG_FOLDER_PATH)
            self.remove_element_from_dir(jpegs)
            # Remove folders from DCIM in the SD Card
            DCIM_path = os.path.join(self.camera_storage_path[0], 'DCIM')
            if os.path.exists(DCIM_path):
                pic_folders = self.utils.get_glob_list(DCIM_path)
                self.remove_element_from_sd_card(pic_folders)
        except Exception as e:
            self.signal.error.emit(f"Erreur lors de la suppression des photos : {e}")
        else:
            self.signal.finished.emit()
        
    def remove_element_from_dir(self, glob_list):
        for element in glob_list:
            os.remove(element)

    def remove_element_from_sd_card(self, glob_list):
        for element in glob_list:
            shutil.rmtree(element)
