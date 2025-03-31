import datetime
import time
import os
from dotenv import load_dotenv
from showinfm import show_in_file_manager
from src.ui.sorting_page import Ui_SortingPage
from src.utils.utils import Utils
from src.utils.workers import SeparationWorker, StorageWorker, RemoveWorker
from PyQt5.QtCore import pyqtSlot, QTimer, QThreadPool
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QMessageBox
from os import getenv


class SortingPage(QMainWindow):
    """Sorting Page"""
    def __init__(self, stacked_widget, gen_update_tm):
        super().__init__()
        load_dotenv('.env')
        self.JPEG_FOLDER_PATH = getenv("JPEG_FOLDER_PATH")
        #Objects Initialization
        self.utils = Utils()
        self.ui = Ui_SortingPage()
        self.threadpool = QThreadPool()
        #UI Setup
        self.ui.setupUi(self)
        #Widgets Value Initialization
        self.ui.rawJpegRadio.setChecked(True)
        self.ui.modeCheckBox.setChecked(False)
        self.ui.dateEdit.setDate(datetime.date.today())
        self.ui.stateLabel.setText("")
        #Widgets Visibility Initialization
        self.ui.settingsWidget.setHidden(True)
        self.ui.dateEdit.setHidden(True)
        self.ui.nPicLine.setHidden(True)
        self.ui.progressBar.setHidden(True)
        #Widgets Callback Initialization
        self.ui.accueilBtn.clicked.connect(lambda: stacked_widget.setCurrentIndex(0))
        self.ui.separationBtn.clicked.connect(lambda: self.separation())
        self.ui.rangementBtn.clicked.connect(lambda: self.storage())
        self.ui.suppressionBtn.clicked.connect(lambda: self.removing())
        self.ui.eventNameLine.textChanged.connect(self.eventNameLine_is_filled)
        self.ui.rawJpegRadio.clicked.connect(self.hide_date_edit)
        self.ui.rawOnlyRadio.clicked.connect(self.display_date_edit)
        self.ui.jpegOnlyRadio.clicked.connect(self.hide_date_edit)
        self.ui.modeCheckBox.stateChanged.connect(self.toggle_widgets)
        self.ui.okBtn.clicked.connect(lambda: self.ok_btn_is_cliked())
        self.ui.cancelBtn.clicked.connect(lambda: self.on_storage_cancel())
        #Other attributes
        self.camera_storage_state, self.camera_storage_path = self.utils.get_camera_storage()
        self.external_storage_state, self.external_storage_path = self.utils.get_external_storage()
        #Timers Initialization
        self.gen_update_tm = gen_update_tm
        self.gen_update_tm.timeout.connect(lambda: self.update_ui())
        self.action_timer = QTimer()
        self.action_timer.setSingleShot(True)
        self.action_timer.timeout.connect(lambda: self.reset_state_label())
        print("sorting page initialized")

    @pyqtSlot()
    def eventNameLine_is_filled(self):
        '''Returns True if the text is filled'''
        return self.ui.okBtn.setEnabled(bool(self.ui.eventNameLine.text().strip()))

    @pyqtSlot()
    def update_ui(self):
        ''' Update every ui element at the timer timeout '''
        self.camera_storage_state, self.camera_storage_path = self.utils.get_camera_storage()
        self.external_storage_state, self.external_storage_path = self.utils.get_external_storage()
        self.utils.update_status_labels(self.ui)

    @pyqtSlot(int)
    def toggle_widgets(self, state):
        '''Display or hide widgets dateEdit and nPicLine'''
        is_checked = state==2
        self.ui.dateEdit.setVisible(is_checked)
        self.ui.nPicLine.setVisible(is_checked)

    @pyqtSlot()
    def display_date_edit(self):
        '''Set dateEdit visible even is modeCheckBox is not checked'''
        self.ui.dateEdit.setVisible(True)

    @pyqtSlot()
    def hide_date_edit(self):
        '''set dateEdit hidden'''
        self.ui.dateEdit.setHidden(True)

    @pyqtSlot()
    def separation(self):
        ''' Process séparation '''
        if self.camera_storage_state:
            pic_folders_path = self.utils.get_pic_folders_path() 
            if pic_folders_path:
                if self.utils.get_storage_data()[2] != '0':  # Number of jpeg
                    if not self.utils.pics_in_folder(self.JPEG_FOLDER_PATH):
                        # UI update
                        self.ui.stateLabel.setText("Séparation en cours ...")
                        self.ui.rangementBtn.setDisabled(True)
                        self.ui.suppressionBtn.setDisabled(True)
                        # Transfer photos
                        worker = SeparationWorker(pic_folders_path,self.JPEG_FOLDER_PATH)
                        worker.signal.finished.connect(self.on_separation_finished)
                        self.threadpool.globalInstance().start(worker)
                    else:
                        self.display_error_message("Photos dans le dossier de tri")
                else:
                    self.display_error_message("Aucun jpeg à séparer dans la carte SD \n\nPassez directement à l'étape de tri")
            else:
                self.display_error_message("Aucune photos dans la carte SD")
        else:
            self.display_error_message("Carte SD manquante")
        return

    def pics_in_JPEG_FOLDER(self):
        '''Returns True if pics are already in the self.JPEG_FOLDER_PATH'''
        
    @pyqtSlot()
    def on_separation_finished(self):
        '''Set value of stateLabel to 'Séparation terminée' for 3 seconds'''
        self.display_success_message("Séparation terminée !")
        self.reset_state_label()
        self.action_timer.start(3000)
        self.ui.rangementBtn.setEnabled(True)
        self.ui.suppressionBtn.setEnabled(True)
        show_in_file_manager(self.JPEG_FOLDER_PATH)

    @pyqtSlot()
    def storage(self):
        ''' Stores photos in the external storage '''
        if self.camera_storage_state: 
            if self.external_storage_state:
                self.ui.stateLabel.setText("En attente, validation des réglages ...")
                self.ui.btnFrame.setHidden(True)
                self.ui.settingsWidget.setVisible(True)
                self.ui.okBtn.setDisabled(True)
                return
            else:
                self.display_error_message("SSD manquant")
                return 
        else:
            self.display_error_message("Carte SD manquante")
            return           

    @pyqtSlot()
    def ok_btn_is_cliked(self):  
        '''Retrieve the data and start the storage'''
        pic_folders_path = self.utils.get_pic_folders_path()
        if pic_folders_path:
            event_name = self.ui.eventNameLine.text().strip()
            if event_name:
                photo_format = self.get_radio_value()
                semi_auto_mode = self.ui.modeCheckBox.isChecked()
                event_date = self.ui.dateEdit.text().strip()
                part = self.ui.nPicLine.text().strip()
                if not semi_auto_mode or part:
                    # UI update
                    self.ui.okBtn.setDisabled(True)
                    self.ui.cancelBtn.setDisabled(True)
                    self.ui.stateLabel.setText('Rangement en cours ...')
                    # Store photos
                    worker = StorageWorker(
                        self.JPEG_FOLDER_PATH,
                        pic_folders_path, 
                        event_name, 
                        photo_format, 
                        semi_auto_mode,
                        event_date,
                        part
                    )
                    worker.signal.error.connect(self.on_storage_error)
                    worker.signal.finished.connect(self.on_storage_finished)
                    self.threadpool.globalInstance().start(worker, )
                else:
                    self.display_error_message("Préciser la partie des photos à ranger")
            else:
                self.display_error_message("Entrez un nom d'évènement dans un premier temps")
        else:
            self.display_error_message("Photos non trouvé dans la carte SD")
            self.on_storage_cancel()          
        return

    def get_radio_value(self):
        '''Return the photo format selected'''
        if self.ui.rawJpegRadio.isChecked():
            return 'RJ'
        elif self.ui.rawOnlyRadio.isChecked():
            return 'R'
        elif self.ui.jpegOnlyRadio.isChecked():
            return 'J'

    @pyqtSlot(str)
    def on_storage_error(self, message):
        ''''''
        self.display_error_message(message)
        self.on_storage_cancel()

    @pyqtSlot(str)
    def on_storage_finished(self, event_path):  
        '''Set ui back to normal status and display message'''
        self.display_success_message("Rangement terminé !")
        self.reset_state_label()
        self.ui.okBtn.setEnabled(True)
        self.ui.cancelBtn.setEnabled(True)
        self.on_storage_cancel()

        if self.ui.modeCheckBox.isChecked():  # Semi Automatic mode
            # Future update
            pass
        show_in_file_manager(event_path)

    @pyqtSlot()
    def on_storage_cancel(self):
        ''''''
        self.ui.eventNameLine.setText("")
        self.ui.rawJpegRadio.click()
        self.ui.btnFrame.setVisible(True)
        self.ui.settingsWidget.setHidden(True)

        if self.ui.modeCheckBox.isChecked():  # Semi Automatic mode
            # Future update
            pass

    @pyqtSlot()
    def removing(self):
        ''''''
        if self.camera_storage_state:
            # get the list of the paths to the photos to remove
            jpegs = self.utils.get_glob_list(self.JPEG_FOLDER_PATH)
            DCIM_path = os.path.join(self.camera_storage_path, 'DCIM')
            if os.path.exists(DCIM_path): 
                pic_folders = self.utils.get_glob_list(DCIM_path)
            else:
                pic_folders = []
            if jpegs or pic_folders:
                # UI update
                self.ui.stateLabel.setText("Suppression en cours ...")
                self.ui.separationBtn.setDisabled(True)
                self.ui.rangementBtn.setDisabled(True)
                # Remove photos
                worker = RemoveWorker(jpegs, pic_folders)
                worker.signal.error.connect(self.on_removing_error)
                worker.signal.finished.connect(self.on_removing_finished)
                self.threadpool.globalInstance().start(worker)
            else:
                self.display_error_message(f"Aucune photo à supprimer")
        else:
            self.display_error_message("Carte SD manquante")
            
    @pyqtSlot(str)
    def on_removing_error(self, message):
        ''''''
        self.display_error_message(message)
        self.reset_state_label()
        self.ui.separationBtn.setEnabled(True)
        self.ui.rangementBtn.setEnabled(True)
    
    @pyqtSlot()
    def on_removing_finished(self):
        self.display_success_message("Suppression terminée !")
        self.reset_state_label()
        self.ui.separationBtn.setEnabled(True)
        self.ui.rangementBtn.setEnabled(True)
        show_in_file_manager(os.path.join(self.utils.get_camera_storage()[1], 'DCIM'))
    
    def display_success_message(self, message):
        '''Dsiplay a QMessageBox with the success message'''
        error_popup = QMessageBox()
        error_popup.setWindowTitle("Succès")
        error_popup.setIconPixmap(QIcon("ressources/icons/white_heavy_check_mark.svg").pixmap(64,64))
        error_popup.setText(message)
        error_popup.setStandardButtons(QMessageBox.StandardButton.Ok)
        error_popup.exec_()

    def display_error_message(self, message):
        '''Display a QMessageBox with the error message'''
        error_popup = QMessageBox()
        error_popup.setIcon(QMessageBox.Icon.Critical)
        error_popup.setWindowTitle("Erreur")
        error_popup.setText(message)
        error_popup.setStandardButtons(QMessageBox.StandardButton.Ok)
        error_popup.exec_()

    def reset_state_label(self):
        '''Reinitialize the state label to "".'''
        self.ui.stateLabel.setText("")
'''
class Tri(FenetrePrincipale):
    def __init__(self, parent=None):
        super().__init__(parent)

        fPathSD = list(glob('/Volumes/NIKON D5600/DCIM/111D5600/*'))

        self.setWindowTitle("Tri")

        # Créer un widget central qui contiendra le layout
        widgetCentral = QWidget(self)
        self.setCentralWidget(widgetCentral)

        # Créer un layout vertical pour organiser les boutons
        layout = QVBoxLayout(widgetCentral)

        # Créer les boutons
        self.btnSeparation = QPushButton("Séparation")
        self.btnCohérence = QPushButton("Cohérence")
        self.btnRangement = QPushButton("Rangement")
        self.btnSuppression = QPushButton("Suppression")

        # Ajouter les boutons au layout
        layout.addWidget(self.btnSeparation)
        layout.addWidget(self.btnCohérence)
        layout.addWidget(self.btnRangement)
        layout.addWidget(self.btnSuppression)  
        
        self.btnSeparation.clicked.connect(lambda : self.separation(fPathSD))
        self.btnCohérence.clicked.connect(self.coherence)
        self.btnRangement.clicked.connect(self.storage)
        self.btnSuppression.clicked.connect(lambda : self.suppression(fPathSD))

        self.labelEtat = QLabel("")
        layout.addWidget(self.labelEtat)

        self.labelRangement = QLabel("storage")
        layout.addWidget(self.labelRangement)
        self.labelRangement.hide()

        self.evenementEdit = QLineEdit()
        layout.addWidget(self.evenementEdit)
        self.evenementEdit.hide()

        self.okLoop = QEventLoop()          #Loop pour le bouton ok 
        self.btnOk = QPushButton("Ok")
        layout.addWidget(self.btnOk)
        self.btnOk.hide()
        self.btnOk.clicked.connect(self.okLoop.quit)

        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.finTimer)


    def separation(self, fPathSD) :
        self.labelEtat.setText("séparation en cours ...")

        for pic_path in fPathSD :															#Itérations sur tous les chemins
            
            if pic_path[-1] == 'G' : 														#Condition de tri d'un JPEG
                copy(pic_path, '/Users/leopold/Library/Mobile Documents/com~apple~CloudDocs/Photo/Jpeg/' + pic_path[-12:]) 	#Enregistrement dans le bon dossier
            
            else : 
                copy(pic_path, '/Users/leopold/Library/Mobile Documents/com~apple~CloudDocs/Photo/Raw/' + pic_path[-12:])
        self.labelEtat.setText("séparation ok")
        self.timer.start(3000)


    def coherence(self) :
        self.labelEtat.setText("mise en cohérence en cours ...")

        fPathJ = list(glob('/Users/leopold/Library/Mobile Documents/com~apple~CloudDocs/Photo/Jpeg/*'))
        fPathR = list(glob('/Users/leopold/Library/Mobile Documents/com~apple~CloudDocs/Photo/Raw/*'))

        for pic_pathR in fPathR :															#Itération sur chaque éléments des deux listes (correspondant à chaque photo)
            garder = False 																	#Condition de garder une photo

            for pic_pathJ in fPathJ :
                if pic_pathJ[-8:-4] == pic_pathR[-8:-4] : 								#Condition pour le tri de la photo avec les 2 numéros des photos  
                    garder = True 															#La condition passe à true si les numéros de photos correspondent

            if garder == False :
                remove(pic_pathR) 															#Efface la photo si condition est fausse

        self.labelEtat.setText("mise en cohérence ok")
        self.timer.start(3000)


    def storage(self) :
        self.btnSeparation.hide()
        self.btnCohérence.hide()
        self.btnRangement.hide()
        self.btnSuppression.hide()

        self.labelRangement.show()
        self.evenementEdit.show()
        self.btnOk.show()

        self.okLoop.exec_()

        evnmt = self.evenementEdit.text()
        self.labelEtat.setText("storage en cours ...")
        
        fPathJ = list(glob('/Users/leopold/Library/Mobile Documents/com~apple~CloudDocs/Photo/Jpeg/*'))
        fPathR = list(glob('/Users/leopold/Library/Mobile Documents/com~apple~CloudDocs/Photo/Raw/*'))

        lDir = ['/OG', '/RT', '/OG/JPEG', '/OG/RAW']
        lMonth = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']
        
        pathDate = fPathJ[0] 																			#Création du chemin de la photo qui donnera la date du shooting 
        date = Image.open(pathDate)._getexif()[36867]

        year = date[0:4]																				#On récupère l'année, le mois et le jour 
        month = date[5:7]
        day = date[8:10]

        if month[0] == 0 :
            monthLetter = month + ' ' + lMonth[int(month[1])-1]
        else :
            monthLetter = month + ' ' + lMonth[int(month)-1]


        if not path.exists(self.getpic_path(year)) : 														#Création des dossiers année, mois si nécessaire
            mkdir(self.getpic_path(year))

        if not path.exists(self.getpic_path(year + '/' + monthLetter)) :
            mkdir(self.getpic_path(year + '/' + monthLetter))	

        mkdir(self.getPathEvnmt(year, monthLetter, month, day, evnmt))										#Création du dossier de l'évènement

        for i in range(len(lDir)) :																		#Création des autres dossier	
            mkdir(self.getPathDirPhoto(year, monthLetter, month, day, evnmt, lDir[i]))


        for pic_path in fPathJ :																		#Copie des photos dans le DDE
            copy(pic_path, self.getPathDirPhoto(year, monthLetter, month, day, evnmt, '/OG/JPEG'))

        for pic_path in fPathR :
            copy(pic_path, self.getPathDirPhoto(year, monthLetter, month, day, evnmt, '/OG/RAW'))

        self.labelEtat.setText("storage ok")
        self.timer.start(3000)

        self.btnSeparation.show()
        self.btnCohérence.show()
        self.btnRangement.show()
        self.btnSuppression.show()

        self.labelRangement.hide()
        self.evenementEdit.hide()
        self.btnOk.hide()


    def suppression(self, fPathSD) :
        self.labelEtat.setText("Suppression en cours ...")

        fPathJ = list(glob('/Users/leopold/Library/Mobile Documents/com~apple~CloudDocs/Photo/Jpeg/*'))
        fPathR = list(glob('/Users/leopold/Library/Mobile Documents/com~apple~CloudDocs/Photo/Raw/*'))

        lPath = [fPathSD, fPathJ, fPathR]
        ls = ['SD', 'jpeg', 'raw']
        
        for path, directory in zip(lPath, ls) :
                for pic_path in path :
                    remove(pic_path)
                self.labelEtat.setText('Suppression ' + directory + ' ok')
                self.timer.start(1000)
        self.labelEtat.setText("Suppression ok\nArvi Pa SIUUUUUUU")
        self.timer.start(3000)


    def getpic_path(self,path) :     
        return '/Volumes/Andúril/Prod/Photo/' + path 


    def getPathEvnmt(self, year, monthLetter, month, day, evnmt) :     
        return self.getpic_path(year + '/' + monthLetter + '/' + day + ':' + month + ' ' + evnmt)


    def getPathDirPhoto(self, year, monthLetter, month, day, evnmt, path) :   
        return self.getPathEvnmt(year, monthLetter, month, day, evnmt) + path
    

    def finTimer(self):
        self.labelEtat.setText("")
'''