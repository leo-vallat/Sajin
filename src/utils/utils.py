import glob
import json
import os

class Utils():
    def __init__(self):
        self.camera_storage_json = 'data/camera_storage.json'
        self.external_storage_json = 'data/external_storage.json'

    #====== storage getters ======#
    def get_camera_storage(self):
        '''return a tuple with the state of the storage and the path of SD Card or SSD that are active'''
        with open(self.camera_storage_json, 'r') as f:
                camera_storage = json.load(f)
        active_storage_path = [path for path in camera_storage['external_storage'] if os.path.exists(path)]
        if active_storage_path:
            return (True, active_storage_path)
        return (False, [])
        
    def get_external_storage(self):
        '''Returns the state of the external storage connexion'''
        with open(self.external_storage_json, 'r') as f:
            external_storage = json.load(f) 
        path = external_storage['external_storage']
        if os.path.exists(path):
            return(True, path)
        return(False, None)

    def get_external_storage_base_dir(self): 
        '''Returns the path to the base dir in the external storage'''
        with open(self.external_storage_json, 'r') as f:
            external_storage = json.load(f)
        return external_storage['base_dir']

    def get_external_storage_event_dirs(self):
        '''Returns the list of dir name and path part of the event dir'''
        with open(self.external_storage_json, 'r') as f:
            external_storage = json.load(f)
        return external_storage['event_dirs']       
    
    #====== glob list getters ======#
    def get_glob_list(self, folder_path):
        '''Return the list of all the path of the files in a folder'''
        return list(glob.glob(os.path.join(folder_path, '*')))

    def get_raw_paths(self, pic_folders_path):  # A TESTER
        ''''''
        raw_paths = []
        for folder in pic_folders_path:
            paths = self.get_glob_list(folder)
            raw_paths += [path for path in paths if path.endswith('.ARW')]
        return raw_paths

    #====== other getters ======#
    def get_year_dir_path(self, year):  # A TESTER
        return os.path.join(self.get_external_storage_base_dir(), year)
    
    def get_month_dir_path(self, month, year):  # A TESTER
        return os.path.join(self.get_year_dir_path(year), self.get_month_dir_name(month))
    
    def get_event_dir_path(self, day, month, year, event_name):  # A TESTER
        return os.path.join(self.get_month_dir_path(month, year), f"{day}:{month} {event_name}")
    
    def get_month_dir_name(self, month):  # A TESTER
        ''''''
        months_dict = {'01':'Janvier', '02':'Février', '03':'Mars', '04':'Avril', '05':'Mai', 
                  '06':'Juin', '07':'Juillet', '08':'Août', '09':'Septembre', '10':'Octobre', 
                  '11':'Novembre', '12':'Décembre'}
        return f"{month} {months_dict[month]}"
    
    def get_equivalent_raw_path(self, jpeg_path, pic_folders_path):  # A TESTER
        ''''''
        jpeg_num = jpeg_path[-12:-4]
        equivalent_raw_name = f"{jpeg_num}.ARW"
        for folder_path in pic_folders_path:
            raw_path = os.path.join(folder_path, equivalent_raw_name)
            if os.path.exists(raw_path):
                return raw_path
        return None

    #====== ui update ======#
    def update_status_labels(self, ui):
        '''Update the text of the accueilBtn depending on storage device connection.'''
        # Retrieve Data
        camera_storage_state, active_storage_path = self.get_camera_storage()
        external_storage_status, _ = self.get_external_storage()
        tooltip_text = active_storage_path[0] if active_storage_path else "Aucun dispositif connecté"
        self.update_label(ui.camStoStatusLabel, "💾 : 🟢" if camera_storage_state else "💾 : 🔴", tooltip_text)
        self.update_label(ui.extStoStatusLabel, "🗡️ : 🟢" if external_storage_status else "🗡️ : 🔴")

    def update_label(self, label, new_text, tooltip=None):
        '''Update a QLabel only if the text or tooltip needs to change.'''
        if label.text() != new_text:
            label.setText(new_text)
        if tooltip and label.toolTip() != tooltip:
            label.setToolTip(tooltip)

    #====== other function ======#
    def pics_in_folder(self, folder, extension='JPG'):
        '''Returns True if at least one file with the right extension is in the folder'''
        for file in self.get_glob_list(folder):
            if file.endswith(extension):
                return True
        return False
