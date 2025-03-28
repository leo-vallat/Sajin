import datetime
import os
from dotenv import load_dotenv
from src.ui.sorting_page import Ui_SortingPage
from src.utils.utils import Utils
from src.utils.workers import SeparationWorker, StorageWorker
from PyQt5.QtCore import pyqtSlot, QTimer, QThreadPool
from PyQt5.QtWidgets import QMainWindow, QMessageBox
from os import remove, mkdir, path, getenv
# from PIL import Image, ExifTags


class SortingPage(QMainWindow):
    """Sorting Page"""
    def __init__(self, stacked_widget, gen_update_tm):
        super().__init__()
        load_dotenv('.env')
        self.JPEG_FOLDER_PATH = getenv("JPEG_FOLDER_PATH")
        #Objects Initialization
        self.utils = Utils()
        self.ui = Ui_SortingPage()
        #UI Setup
        self.ui.setupUi(self)
        #Widgets Value Initialization
        self.ui.rawJpegRadio.setChecked(True)
        self.ui.modeCheckBox.setChecked(False)
        self.ui.dateEdit.setDate(datetime.date.today())
        self.ui.stateLabel.setText("")
        #Widgets Visibility Initialization
        self.ui.dateEdit.setVisible(False)
        self.ui.nPicLine.setVisible(False)
        self.ui.okBtn.setVisible(False)
        self.ui.progressBar.setVisible(False)
        #Widgets Callback Initialization
        self.ui.accueilBtn.clicked.connect(lambda: stacked_widget.setCurrentIndex(0))
        self.ui.separationBtn.clicked.connect(lambda: self.separation())
        self.ui.rangementBtn.clicked.connect(lambda: self.rangement())
    #     self.ui.suppressionBtn.clicked.connect(lambda: self.suppression)
        self.ui.okBtn.clicked.connect(lambda: self.ok_btn_is_cliked())
        self.ui.modeCheckBox.stateChanged.connect(self.toggle_widgets)
        #Other attributes
        self.camera_storage_state, self.camera_storage_device = self.utils.get_camera_storage()
        self.external_storage_state, self.external_storage_path = self.utils.get_external_storage()
        #Timers Initialization
        self.gen_update_tm = gen_update_tm
        self.gen_update_tm.timeout.connect(lambda: self.update_ui())
        self.action_timer = QTimer()
        self.action_timer.setSingleShot(True)
        self.action_timer.timeout.connect(lambda: self.reinitialize_state_label())

        print("sorting page initialized")

    def update_ui(self):
        ''' Update every ui element at the timer timeout '''
        self.camera_storage_state, self.camera_storage_device = self.utils.get_camera_storage()
        self.external_storage_state, self.external_storage_path = self.utils.get_external_storage()
        self.utils.update_status_labels(self.ui)

    @pyqtSlot(int)
    def toggle_widgets(self, state):
        '''Display or hide widgets dateEdit and nPicLine'''
        is_checked = state==2
        self.ui.dateEdit.setVisible(is_checked)
        self.ui.nPicLine.setVisible(is_checked)
        
    def separation(self):
        ''' Process séparation '''
        if self.camera_storage_state:
            pic_folders_path = self.get_pic_folders_path() 
            if pic_folders_path:
                # Transfer photos
                self.ui.stateLabel.setText("Séparation en cours ...")
                # Disable other action buttons
                self.ui.rangementBtn.setDisabled(True)
                self.ui.suppressionBtn.setDisabled(True)
                worker = SeparationWorker(pic_folders_path,self.JPEG_FOLDER_PATH)
                worker.signal.finished.connect(self.on_separation_finished)
                QThreadPool.globalInstance().start(worker)
            else:
                self.display_error_message("Photos non trouvé dans la carte SD")
                return
        else:
            self.display_error_message("Carte SD manquante")
            return

    def get_pic_folders_path(self):
        '''Return the list of paths to folders containing the photos'''
        DCIM_path = os.path.join(self.camera_storage_device[0], 'DCIM')
        if os.path.exists(DCIM_path):
            return [os.path.join(DCIM_path, folder) for folder in os.listdir(DCIM_path) if os.path.isdir(os.path.join(DCIM_path, folder))]
        return None

    def on_separation_finished(self):
        '''Set value of stateLabel to 'Séparation terminée' for 3 seconds'''
        self.ui.stateLabel.setText("Séparation terminée")
        self.action_timer.start(3000)
        self.ui.rangementBtn.setDisabled(False)
        self.ui.suppressionBtn.setDisabled(False)

    def rangement(self):  # A TESTER
        ''' Stores photos in the external storage '''
        print('RANGEMENT BUTTON CLICKED')
        if self.camera_storage_state: 
            if self.external_storage_state:
                print('SD AND SSD OK')
                self.ui.stateLabel.setText("En attente, validation des réglages ...")
                self.ui.separationBtn.setDisabled(True)
                self.ui.suppressionBtn.setDisabled(True)
                self.ui.okBtn.setVisible(True)
            else:
                self.display_error_message("SSD manquant")
                return 
        else:
            self.display_error_message("Carte SD manquante")
            return           

    def ok_btn_is_cliked(self):  # A TESTER
        '''Retrieve the data and start the storage'''
        print('OKAY BUTTON CLIKED')
        pic_folders_path = self.get_pic_folders_path()
        if pic_folders_path:
            print('PIC FOLDER PATH OK')
            event_name = self.ui.eventNameLine.text().strip()
            if event_name:
                print('EVENT NAME OK')
                photo_format = self.get_radio_value()
                semi_auto_mode = self.ui.modeCheckBox.isChecked()
                event_date = self.ui.dateEdit.text().strip()
                part = self.ui.nPicLine.text().strip()
                if semi_auto_mode and not part:
                    self.display_error_message("Préciser la partie des photos à ranger")
                    return
                print('START STORAGE')
                self.ui.stateLabel.setText('Rangement en cours ...')
                worker = StorageWorker(
                    self.JPEG_FOLDER_PATH,
                    pic_folders_path, 
                    event_name, 
                    photo_format, 
                    semi_auto_mode,
                    event_date,
                    part
                )
                worker.signal.finished.connect(self.on_storage_finished)
                QThreadPool.globalInstance().start(worker)
            else:
                self.display_error_message("Entrez un nom d'évènement dans un premier temps")
                return
        else:
            self.display_error_message("Photos non trouvé dans la carte SD")
            self.ui.separationBtn.setDisabled(False)
            self.ui.suppressionBtn.setDisabled(False)
            self.ui.okBtn.setVisible(False)
            self.reinitialize_state_label()
            return

    def get_radio_value(self):
        '''Return the photo format selected'''
        if self.ui.rawJpegRadio.isChecked():
            print('RADIO VALUE : RJ')
            return 'RJ'
        elif self.ui.rawOnlyRadio.isChecked():
            print('RADIO VALUE : R')
            return 'R'
        elif self.ui.jpegOnlyRadio.isChecked():
            print('RADIO VALUE : J')
            return 'J'

    def on_storage_finished(self):  # A TESTER
        '''Set ui back to normal status and display message'''
        print('STORAGE FINISHED')
        self.ui.stateLabel.setText("Rangement terminé")
        self.action_timer.start(5000)
        self.ui.separationBtn.setDisabled(False)
        self.ui.suppressionBtn.setDisabled(False)
        self.ui.eventNameLine.setText("")
        self.ui.okBtn.setVisible(False)

        if self.ui.modeCheckBox.isChecked():  # Semi Automatic mode
            # Future update
            pass

    # def coherence(self) :
    #     self.labelEtat.setText("mise en cohérence en cours ...")

    #     fPathJ = list(glob('/Users/leopold/Library/Mobile Documents/com~apple~CloudDocs/Photo/Jpeg/*'))
    #     fPathR = list(glob('/Users/leopold/Library/Mobile Documents/com~apple~CloudDocs/Photo/Raw/*'))

    #     for pic_pathR in fPathR :															#Itération sur chaque éléments des deux listes (correspondant à chaque photo)
    #         garder = False 																	#Condition de garder une photo

    #         for pic_pathJ in fPathJ :
    #             if pic_pathJ[-8:-4] == pic_pathR[-8:-4] : 								#Condition pour le tri de la photo avec les 2 numéros des photos  
    #                 garder = True 															#La condition passe à true si les numéros de photos correspondent

    #         if garder == False :
    #             remove(pic_pathR) 															#Efface la photo si condition est fausse

    #     self.labelEtat.setText("mise en cohérence ok")
    #     self.timer.start(3000)


    # def rangement(self) :
    #     fPathJ = list(glob('/Users/leopold/Library/Mobile Documents/com~apple~CloudDocs/Photo/Jpeg/*'))
    #     fPathR = list(glob('/Users/leopold/Library/Mobile Documents/com~apple~CloudDocs/Photo/Raw/*'))

    #     lDir = ['/OG', '/RT', '/OG/JPEG', '/OG/RAW']
    #     lMonth = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']
        
    #     pathDate = fPathJ[0] 																			#Création du chemin de la photo qui donnera la date du shooting 
        # date = Image.open(pathDate)._getexif()[36867]

    #     year = date[0:4]																				#On récupère l'année, le mois et le jour 
    #     month = date[5:7]
    #     day = date[8:10]

    #     if month[0] == 0 :
    #         monthLetter = month + ' ' + lMonth[int(month[1])-1]
    #     else :
    #         monthLetter = month + ' ' + lMonth[int(month)-1]


    #     if not path.exists(self.getpic_path(year)) : 														#Création des dossiers année, mois si nécessaire
    #         mkdir(self.getpic_path(year))

    #     if not path.exists(self.getpic_path(year + '/' + monthLetter)) :
    #         mkdir(self.getpic_path(year + '/' + monthLetter))	

    #     mkdir(self.getPathEvnmt(year, monthLetter, month, day, evnmt))										#Création du dossier de l'évènement

    #     for i in range(len(lDir)) :																		#Création des autres dossier	
    #         mkdir(self.getPathDirPhoto(year, monthLetter, month, day, evnmt, lDir[i]))


    #     for pic_path in fPathJ :																		#Copie des photos dans le DDE
    #         copy(pic_path, self.getPathDirPhoto(year, monthLetter, month, day, evnmt, '/OG/JPEG'))

    #     for pic_path in fPathR :
    #         copy(pic_path, self.getPathDirPhoto(year, monthLetter, month, day, evnmt, '/OG/RAW'))

    #     self.labelEtat.setText("rangement ok")
    #     self.timer.start(3000)

    #     self.btnSeparation.show()
    #     self.btnCohérence.show()
    #     self.btnRangement.show()
    #     self.btnSuppression.show()

    #     self.labelRangement.hide()
    #     self.evenementEdit.hide()
    #     self.btnOk.hide()


    # def suppression(self, fPathSD) :
    #     self.labelEtat.setText("Suppression en cours ...")

    #     fPathJ = list(glob('/Users/leopold/Library/Mobile Documents/com~apple~CloudDocs/Photo/Jpeg/*'))
    #     fPathR = list(glob('/Users/leopold/Library/Mobile Documents/com~apple~CloudDocs/Photo/Raw/*'))

    #     lPath = [fPathSD, fPathJ, fPathR]
    #     ls = ['SD', 'jpeg', 'raw']
        
    #     for path, directory in zip(lPath, ls) :
    #             for pic_path in path :
    #                 remove(pic_path)
    #             self.labelEtat.setText('Suppression ' + directory + ' ok')
    #             self.timer.start(1000)
    #     self.labelEtat.setText("Suppression ok\nArvi Pa SIUUUUUUU")
    #     self.timer.start(3000)


    # def getpic_path(self, path) :     
    #     return '/Volumes/Andúril/Prod/Photo/' + path 


    # def getPathEvnmt(self, year, monthLetter, month, day, evnmt) :     
    #     return self.getpic_path(year + '/' + monthLetter + '/' + day + ':' + month + ' ' + evnmt)


    # def getPathDirPhoto(self, year, monthLetter, month, day, evnmt, path) :   
    #     return self.getPathEvnmt(year, monthLetter, month, day, evnmt) + path
    
    def display_error_message(self, message):
        '''Display a QMessageBox with the error message'''
        error_popup = QMessageBox()
        error_popup.setIcon(QMessageBox.Icon.Critical)
        error_popup.setWindowTitle("Erreur")
        error_popup.setText(message)
        error_popup.setStandardButtons(QMessageBox.StandardButton.Ok)
        error_popup.exec_()

    def reinitialize_state_label(self):
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
        self.btnRangement.clicked.connect(self.rangement)
        self.btnSuppression.clicked.connect(lambda : self.suppression(fPathSD))

        self.labelEtat = QLabel("")
        layout.addWidget(self.labelEtat)

        self.labelRangement = QLabel("rangement")
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


    def rangement(self) :
        self.btnSeparation.hide()
        self.btnCohérence.hide()
        self.btnRangement.hide()
        self.btnSuppression.hide()

        self.labelRangement.show()
        self.evenementEdit.show()
        self.btnOk.show()

        self.okLoop.exec_()

        evnmt = self.evenementEdit.text()
        self.labelEtat.setText("rangement en cours ...")
        
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

        self.labelEtat.setText("rangement ok")
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