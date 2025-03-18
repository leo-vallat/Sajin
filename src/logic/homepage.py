import json
import os
import sys
from src.ui.homepage import Ui_Homepage
from src.utils.utils import Utils
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QToolBar, QAction

class HomePage(QMainWindow):
    """Page d'accueil"""
    def __init__(self, stacked_widget, gen_update_timer):
        super().__init__()
        self.utils = Utils()
        #UI Initialization
        self.ui = Ui_Homepage()
        self.ui.setupUi(self)
        self.ui.triBtn.clicked.connect(lambda: stacked_widget.setCurrentIndex(1))
        #Timer Initialization
        self.gen_update_timer = gen_update_timer
        self.gen_update_timer.timeout.connect(lambda: self.update_ui())
        #Storage Value Initialization
        # storage_data = self.get_storage_data()
        # self.ui.card1InfoLabel.setText(storage_data[0])
        # self.ui.card2InfoLabel.setText(storage_data[1])
        # self.ui.card3InfoLabel.setText(storage_data[2])
        print("homepage initialized")

    def update_ui(self):
        ''' Update every ui element at the timer timeout '''
        self.update_accueilBtn()
        self.update_storage_data()

    def update_accueilBtn(self):
        '''Update the text of the accueilBtn depending if a storage device is connected'''
        storage_state, active_storage_path = self.utils.get_storage()
        if storage_state:
            self.ui.accueilBtn.setText("  Accueil 💾")
            self.ui.accueilBtn.setToolTip(f"{active_storage_path[0]}")
        else:
            self.ui.accueilBtn.setText("  Accueil ❌")
            self.ui.accueilBtn.setToolTip("Aucun dispositif connecté")
    
    def update_storage_data(self):
        ''' Update the values of card(1,2,3)InfoLabel '''
        storage_data = self.get_storage_data()
        
        self.ui.card1InfoLabel.setText(storage_data[0])
        self.ui.card2InfoLabel.setText(storage_data[1])
        self.ui.card3InfoLabel.setText(storage_data[2])

    def get_storage_data(self):
        '''
        Get the number of photos stored at camera_storage paths
        
        !!! Working for Sony environnement only !!!
        '''
        nPic = 0
        nRAW = 0
        nJPEG = 0
        
        storage_state, active_storage_path = self.utils.get_storage()

        if storage_state:
            for path in active_storage_path:
                DCIM_path = os.path.join(path, 'DCIM')
                pic_folder = [d for d in os.listdir(DCIM_path) if os.path.isdir(os.path.join(DCIM_path, d))]
                for folder in pic_folder:
                    folder_path = os.path.join(DCIM_path, folder)
                    for file in os.listdir(folder_path):
                        if file.endswith(('.ARW', '.NEF', '.CR3')):
                            nRAW += 1
                            nPic += 1
                        elif file.endswith(('.jpg', '.JPG')):
                            nJPEG += 1
                            nPic += 1
            return [str(nPic), str(nRAW), str(nJPEG)]
        else:
            return ['--','--','--']

'''
class FenetrePrincipale(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout()

        centralWidget = QWidget()
        centralWidget.setLayout(layout)
        self.setCentralWidget(centralWidget)

        self.label = QLabel("Bienvenue")
        layout.addWidget(self.label)

        menuBar = self.menuBar()
        menuAide = menuBar.addMenu("Aide")
        menuAideAction = QAction("Aide", self)
        menuAide.addAction(menuAideAction)
        menuCredits = menuBar.addMenu("Credits")
        menuCreditsAction = QAction("Crédits", self)
        menuCredits.addAction(menuCreditsAction)

        barreOutils = QToolBar("Toolbar")
        self.addToolBar(Qt.RightToolBarArea, barreOutils)

        fenetreTri = QAction("Tri",self)
        barreOutils.addAction(fenetreTri)
        fenetreTri.triggered.connect(self.ouvertureTri)

        fenetreRenommage = QAction("Renommage", self)
        barreOutils.addAction(fenetreRenommage)
        fenetreRenommage.triggered.connect(self.ouvertureRenommage)

        # Initialisation de la fenêtre
        self.setWindowTitle("@leovallat.ph's app")
        self.resize(600, 400)
        self.centrerFenetre
        self.setStyleSheet("QToolBar { background-color: transparent; border: none; }")



    def centrerFenetre(self):
        screen_geometry = QApplication.desktop().screenGeometry()  # Récupérer la géométrie de l'écran
        window_geometry = self.frameGeometry()  # Récupérer la géométrie de la fenêtre

        # Calculer les coordonnées pour centrer la fenêtre
        x = (screen_geometry.width() - window_geometry.width()) // 2
        y = (screen_geometry.height() - window_geometry.height()) // 2

        self.move(x, y)  # Déplace la fenêtre aux bonnes coordonées


    def ouvertureTri(self):
        self.hide()
        self.autre_fenetre = sortingPage.Tri(self)
        self.autre_fenetre.setGeometry(self.geometry().x(), self.geometry().y(), self.geometry().width(), self.geometry().height())
        self.autre_fenetre.show()

    def ouvertureRenommage(self):
        self.hide()
        self.autre_fenetre = sortingPage.Renommage(self)
        self.autre_fenetre.setGeometry(self.geometry().x(), self.geometry().y(), self.geometry().width(), self.geometry().height())
        self.autre_fenetre.show()



if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = FenetrePrincipale()
    window.show()

    sys.exit(app.exec_())
'''


###################################################################################################
## BUG A CORRIGER
###################################################################################################
##
## 1) Gestion d'erreur si on met un / dans le nom de l'évènement : 
##  File "/Users/leopold 1/Desktop/Appli Photo/AutresFenetres.py", line 137, in rangement
##    mkdir(self.getPathEvnmt(year, monthLetter, month, day, evnmt))                                                                        #Création du dossier de l'évènement
##  FileNotFoundError: [Errno 2] No such file or directory: '/Volumes/Andúril Prod/Photo/2023/07 Juillet/09:07 Levé de soleil Saulire w/ Juju ...'
##
###################################################################################################