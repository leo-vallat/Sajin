from PyQt5 import QtWidgets
import sys
from src.ui.Homepage import Ui_Homepage  # Import de la page d'accueil (générée par Qt Designer)
from src.ui.SortingPage import Ui_SortingPage  # Import de la page de tri (générée par Qt Designer)

class MainApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        # Création du QStackedWidget
        self.stacked_widget = QtWidgets.QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # Initialisation des pages
        self.home_page = QtWidgets.QMainWindow()
        self.sorting_page = QtWidgets.QMainWindow()

        # Interface de la page d'accueil
        self.ui_home = Ui_Homepage()
        self.ui_home.setupUi(self.home_page)

        # Interface de la page de tri
        self.ui_sorting = Ui_SortingPage()
        self.ui_sorting.setupUi(self.sorting_page)

        # Ajout des pages au QStackedWidget
        self.stacked_widget.addWidget(self.home_page)  # Index 0
        self.stacked_widget.addWidget(self.sorting_page)  # Index 1

        # Connexion des boutons pour la navigation
        self.ui_home.triBtn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))  # Aller à Tri
        self.ui_sorting.accueilBtn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))  # Aller à Accueil

        # Afficher la première page par défaut
        self.stacked_widget.setCurrentIndex(0)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainApp()
    main_window.show()
    sys.exit(app.exec_())