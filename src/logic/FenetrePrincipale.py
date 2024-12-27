import sys
import typing
import AutresFenetres
from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel, QDialog, QGridLayout, QToolBar, QAction, QMenuBar
from PyQt5.QtGui import QIcon, QFont, QPalette, QColor, QLinearGradient


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
        self.autre_fenetre = AutresFenetres.Tri(self)
        self.autre_fenetre.setGeometry(self.geometry().x(), self.geometry().y(), self.geometry().width(), self.geometry().height())
        self.autre_fenetre.show()

    def ouvertureRenommage(self):
        self.hide()
        self.autre_fenetre = AutresFenetres.Renommage(self)
        self.autre_fenetre.setGeometry(self.geometry().x(), self.geometry().y(), self.geometry().width(), self.geometry().height())
        self.autre_fenetre.show()



if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = FenetrePrincipale()
    window.show()

    sys.exit(app.exec_())



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