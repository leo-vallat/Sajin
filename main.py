from PyQt5 import QtWidgets
import sys
from src.logic.homepage import HomePage  
from src.logic.sortingPage import SortingPage

class MainApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        # Création du QStackedWidget
        self.stacked_widget = QtWidgets.QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.home_page = HomePage(self.stacked_widget)
        self.sorting_page = SortingPage(self.stacked_widget)

        # Ajout des pages au QStackedWidget
        self.stacked_widget.addWidget(self.home_page)  
        self.stacked_widget.addWidget(self.sorting_page)  
        
        self.stacked_widget.setCurrentIndex(0)  # Affiche la page d'accueil par défaut



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainApp()
    main_window.show()
    sys.exit(app.exec_())