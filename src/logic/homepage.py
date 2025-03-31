from src.ui.homepage import Ui_Homepage
from src.utils.utils import Utils
from PyQt5.QtWidgets import QMainWindow


class HomePage(QMainWindow):
    """Page d'accueil"""
    def __init__(self, stacked_widget, gen_update_timer):
        super().__init__()
        self.utils = Utils()
        #UI Initialization
        self.ui = Ui_Homepage()
        self.ui.setupUi(self)
        self.ui.triBtn.clicked.connect(lambda: stacked_widget.setCurrentIndex(1))
        self.update_ui()
        #Timer Initialization
        self.gen_update_timer = gen_update_timer
        self.gen_update_timer.timeout.connect(lambda: self.update_ui())
        print("homepage initialized")

    def update_ui(self):
        ''' Update every ui element at the timer timeout '''
        self.utils.update_status_labels(self.ui)
        self.update_storage_data()
    
    def update_storage_data(self):
        ''' Update the values of card(1,2,3)InfoLabel '''
        storage_data = self.utils.get_storage_data()
        
        self.ui.card1InfoLabel.setText(storage_data[0])
        self.ui.card2InfoLabel.setText(storage_data[1])
        self.ui.card3InfoLabel.setText(storage_data[2])


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