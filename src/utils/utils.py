import glob
import json
import os

class Utils():
    def __init__(self):
        self.camera_storage_path = 'data/camera_storage.json'

    def get_storage(self):
        '''return a tuple with the state of the storage and the path of SD Card or SSD that are active'''
        with open(self.camera_storage_path, 'r') as f:
                camera_storage = json.load(f)
        
        active_storage_path = [path for path in camera_storage['external_storage'] if os.path.exists(path)]

        if active_storage_path:
            return (True, active_storage_path)
        else:
             return (False, [])
        
    def get_glob_list(self, folder_path):
        '''Return the list of all the path of photos in a folder'''
        return list(glob.glob(os.path.join(folder_path, '*')))