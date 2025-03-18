import datetime
from dotenv import load_dotenv
from src.ui.sortingPage import Ui_SortingPage
from src.utils.utils import Utils
from PyQt5.QtCore import pyqtSlot, QEventLoop, QTimer
from PyQt5.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel, QLineEdit
from os import remove, mkdir, path, getenv
from shutil import copy
from glob import glob
# from PIL import Image, ExifTags


class SortingPage(QMainWindow):
    """Sorting Page"""
    def __init__(self, stacked_widget, gen_update_timer):
        super().__init__()
        load_dotenv('.env')
        RAW_FOLDER_PATH = getenv("RAW_FOLDER_PATH")
        JPEG_FOLDER_PATH = getenv("JPEG_FOLDER_PATH")
        self.utils = Utils()

        self.ui = Ui_SortingPage()
        self.ui.setupUi(self)
        self.ui.accueilBtn.clicked.connect(lambda: stacked_widget.setCurrentIndex(0))
        #Timer Initialization
        self.gen_update_timer = gen_update_timer
        self.gen_update_timer.timeout.connect(lambda: self.update_accueilBtn())

        self.ui.modeCheckBox.setChecked(False)
        self.ui.dateEdit.setVisible(False)
        self.ui.nPicLine.setVisible(False)
        self.ui.statelabel.setVisible(False)
        self.ui.progressBar.setVisible(False)

        self.ui.modeCheckBox.stateChanged.connect(self.toggle_widgets)

        self.ui.dateEdit.setDate(datetime.date.today())

    #     self.ui.separationBtn.clicked.connect(lambda: self.separation)
    #     self.ui.coherenceBtn.clicked.connect(lambda: self.coherence)
    #     self.ui.rangementBtn.clicked.connect(lambda: self.rangement)
    #     self.ui.suppressionBtn.clicked.connect(lambda: self.suppression)

    @pyqtSlot(int)
    def toggle_widgets(self, state):
        '''Display or hide widgets dateEdit and nPicLine'''
        is_checked = state==2
        self.ui.dateEdit.setVisible(is_checked)
        self.ui.nPicLine.setVisible(is_checked)

        self.ui.statelabel.setVisible(is_checked)
        self.ui.progressBar.setVisible(is_checked)
        
    def update_accueilBtn(self):
        '''Update the text of the accueilBtn depending if a storage device is connected'''
        storage_state, active_storage_path = self.utils.check_storage()
        print('[SORTING PAGE] STORAGE CHECKED')
        if storage_state:
            self.ui.accueilBtn.setText("Accueil 💾")
            self.ui.accueilBtn.setToolTip(f"{active_storage_path[0]}")
        else:
            self.ui.accueilBtn.setText("Accueil ❌")
            self.ui.accueilBtn.setToolTip("Aucun dispositif connecté")

    # def separation(self) :
    #     self.ui.statelabel.setText("séparation en cours ...")

    #     for pathPhoto in fPathSD:  #Itérations sur tous les chemins
            
    #         if pathPhoto[-1] == 'G':  #Condition de tri d'un JPEG
    #             copy(pathPhoto, '/Users/leopold/Library/Mobile Documents/com~apple~CloudDocs/Photo/Jpeg/' + pathPhoto[-12:])  #Enregistrement dans le bon dossier
            
    #         else : 
    #             copy(pathPhoto, '/Users/leopold/Library/Mobile Documents/com~apple~CloudDocs/Photo/Raw/' + pathPhoto[-12:])
    #     self.labelEtat.setText("séparation ok")
    #     self.timer.start(3000)


    # def coherence(self) :
    #     self.labelEtat.setText("mise en cohérence en cours ...")

    #     fPathJ = list(glob('/Users/leopold/Library/Mobile Documents/com~apple~CloudDocs/Photo/Jpeg/*'))
    #     fPathR = list(glob('/Users/leopold/Library/Mobile Documents/com~apple~CloudDocs/Photo/Raw/*'))

    #     for pathPhotoR in fPathR :															#Itération sur chaque éléments des deux listes (correspondant à chaque photo)
    #         garder = False 																	#Condition de garder une photo

    #         for pathPhotoJ in fPathJ :
    #             if pathPhotoJ[-8:-4] == pathPhotoR[-8:-4] : 								#Condition pour le tri de la photo avec les 2 numéros des photos  
    #                 garder = True 															#La condition passe à true si les numéros de photos correspondent

    #         if garder == False :
    #             remove(pathPhotoR) 															#Efface la photo si condition est fausse

    #     self.labelEtat.setText("mise en cohérence ok")
    #     self.timer.start(3000)


    # def rangement(self) :
    #     self.btnSeparation.hide()
    #     self.btnCohérence.hide()
    #     self.btnRangement.hide()
    #     self.btnSuppression.hide()

    #     self.labelRangement.show()
    #     self.evenementEdit.show()
    #     self.btnOk.show()

    #     self.okLoop.exec_()

    #     evnmt = self.evenementEdit.text()
    #     self.labelEtat.setText("rangement en cours ...")
        
    #     fPathJ = list(glob('/Users/leopold/Library/Mobile Documents/com~apple~CloudDocs/Photo/Jpeg/*'))
    #     fPathR = list(glob('/Users/leopold/Library/Mobile Documents/com~apple~CloudDocs/Photo/Raw/*'))

    #     lDir = ['/OG', '/RT', '/OG/JPEG', '/OG/RAW']
    #     lMonth = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']
        
    #     pathDate = fPathJ[0] 																			#Création du chemin de la photo qui donnera la date du shooting 
    #     date = Image.open(pathDate)._getexif()[36867]

    #     year = date[0:4]																				#On récupère l'année, le mois et le jour 
    #     month = date[5:7]
    #     day = date[8:10]

    #     if month[0] == 0 :
    #         monthLetter = month + ' ' + lMonth[int(month[1])-1]
    #     else :
    #         monthLetter = month + ' ' + lMonth[int(month)-1]


    #     if not path.exists(self.getPathPhoto(year)) : 														#Création des dossiers année, mois si nécessaire
    #         mkdir(self.getPathPhoto(year))

    #     if not path.exists(self.getPathPhoto(year + '/' + monthLetter)) :
    #         mkdir(self.getPathPhoto(year + '/' + monthLetter))	

    #     mkdir(self.getPathEvnmt(year, monthLetter, month, day, evnmt))										#Création du dossier de l'évènement

    #     for i in range(len(lDir)) :																		#Création des autres dossier	
    #         mkdir(self.getPathDirPhoto(year, monthLetter, month, day, evnmt, lDir[i]))


    #     for pathPhoto in fPathJ :																		#Copie des photos dans le DDE
    #         copy(pathPhoto, self.getPathDirPhoto(year, monthLetter, month, day, evnmt, '/OG/JPEG'))

    #     for pathPhoto in fPathR :
    #         copy(pathPhoto, self.getPathDirPhoto(year, monthLetter, month, day, evnmt, '/OG/RAW'))

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
    #             for pathPhoto in path :
    #                 remove(pathPhoto)
    #             self.labelEtat.setText('Suppression ' + directory + ' ok')
    #             self.timer.start(1000)
    #     self.labelEtat.setText("Suppression ok\nArvi Pa SIUUUUUUU")
    #     self.timer.start(3000)


    # def getPathPhoto(self,path) :     
    #     return '/Volumes/Andúril/Prod/Photo/' + path 


    # def getPathEvnmt(self, year, monthLetter, month, day, evnmt) :     
    #     return self.getPathPhoto(year + '/' + monthLetter + '/' + day + ':' + month + ' ' + evnmt)


    # def getPathDirPhoto(self, year, monthLetter, month, day, evnmt, path) :   
    #     return self.getPathEvnmt(year, monthLetter, month, day, evnmt) + path
    

    # def finTimer(self):
    #     self.labelEtat.setText("")

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

        for pathPhoto in fPathSD :															#Itérations sur tous les chemins
            
            if pathPhoto[-1] == 'G' : 														#Condition de tri d'un JPEG
                copy(pathPhoto, '/Users/leopold/Library/Mobile Documents/com~apple~CloudDocs/Photo/Jpeg/' + pathPhoto[-12:]) 	#Enregistrement dans le bon dossier
            
            else : 
                copy(pathPhoto, '/Users/leopold/Library/Mobile Documents/com~apple~CloudDocs/Photo/Raw/' + pathPhoto[-12:])
        self.labelEtat.setText("séparation ok")
        self.timer.start(3000)


    def coherence(self) :
        self.labelEtat.setText("mise en cohérence en cours ...")

        fPathJ = list(glob('/Users/leopold/Library/Mobile Documents/com~apple~CloudDocs/Photo/Jpeg/*'))
        fPathR = list(glob('/Users/leopold/Library/Mobile Documents/com~apple~CloudDocs/Photo/Raw/*'))

        for pathPhotoR in fPathR :															#Itération sur chaque éléments des deux listes (correspondant à chaque photo)
            garder = False 																	#Condition de garder une photo

            for pathPhotoJ in fPathJ :
                if pathPhotoJ[-8:-4] == pathPhotoR[-8:-4] : 								#Condition pour le tri de la photo avec les 2 numéros des photos  
                    garder = True 															#La condition passe à true si les numéros de photos correspondent

            if garder == False :
                remove(pathPhotoR) 															#Efface la photo si condition est fausse

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


        if not path.exists(self.getPathPhoto(year)) : 														#Création des dossiers année, mois si nécessaire
            mkdir(self.getPathPhoto(year))

        if not path.exists(self.getPathPhoto(year + '/' + monthLetter)) :
            mkdir(self.getPathPhoto(year + '/' + monthLetter))	

        mkdir(self.getPathEvnmt(year, monthLetter, month, day, evnmt))										#Création du dossier de l'évènement

        for i in range(len(lDir)) :																		#Création des autres dossier	
            mkdir(self.getPathDirPhoto(year, monthLetter, month, day, evnmt, lDir[i]))


        for pathPhoto in fPathJ :																		#Copie des photos dans le DDE
            copy(pathPhoto, self.getPathDirPhoto(year, monthLetter, month, day, evnmt, '/OG/JPEG'))

        for pathPhoto in fPathR :
            copy(pathPhoto, self.getPathDirPhoto(year, monthLetter, month, day, evnmt, '/OG/RAW'))

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
                for pathPhoto in path :
                    remove(pathPhoto)
                self.labelEtat.setText('Suppression ' + directory + ' ok')
                self.timer.start(1000)
        self.labelEtat.setText("Suppression ok\nArvi Pa SIUUUUUUU")
        self.timer.start(3000)


    def getPathPhoto(self,path) :     
        return '/Volumes/Andúril/Prod/Photo/' + path 


    def getPathEvnmt(self, year, monthLetter, month, day, evnmt) :     
        return self.getPathPhoto(year + '/' + monthLetter + '/' + day + ':' + month + ' ' + evnmt)


    def getPathDirPhoto(self, year, monthLetter, month, day, evnmt, path) :   
        return self.getPathEvnmt(year, monthLetter, month, day, evnmt) + path
    

    def finTimer(self):
        self.labelEtat.setText("")
'''