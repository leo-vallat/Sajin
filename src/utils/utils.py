import glob
import json
import os

class Utils():
    def __init__(self):
        self.camera_storage_path = 'data/camera_storage.json'
        self.external_storage_path = 'data/external_storage.json'

    def get_camera_storage(self):
        '''return a tuple with the state of the storage and the path of SD Card or SSD that are active'''
        with open(self.camera_storage_path, 'r') as f:
                camera_storage = json.load(f)
        active_storage_path = [path for path in camera_storage['external_storage'] if os.path.exists(path)]
        if active_storage_path:
            return (True, active_storage_path)
        return (False, [])
        
    def get_external_storage(self):
        '''return the state of the external storage connexion'''
        with open(self.external_storage_path, 'r') as f:
                external_storage = json.load(f) 
        path = external_storage['external_storage']
        if os.path.exists(path):
            return(True, path)
        return(False, None)

        
    def get_glob_list(self, folder_path):
        '''Return the list of all the path of photos in a folder'''
        return list(glob.glob(os.path.join(folder_path, '*')))

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
