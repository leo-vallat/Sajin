from PyQt5 import QtWidgets
from PyQt5.QtCore import QTimer
import sys
from src.logic.homepage import HomePage  
from src.logic.sortingPage import SortingPage

class MainApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.gen_update_timer = QTimer()
        self.gen_update_timer.start(3000)
        self.stacked_widget = QtWidgets.QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.homepage = HomePage(self.stacked_widget, self.gen_update_timer)
        self.sorting_page = SortingPage(self.stacked_widget, self.gen_update_timer)

        self.stacked_widget.addWidget(self.homepage)  
        self.stacked_widget.addWidget(self.sorting_page)  
        
        self.stacked_widget.setCurrentIndex(0)  # Affiche la page d'accueil par défaut

    def go_to_homePage(self):
        '''Natigate to homePage'''
        self.homepage.reset_ui()
        self.stacked_widget.setCurrentIndex(0)

    def go_to_sortingPage(self):
        '''Navigate to sortingPage'''
        self.stacked_widget.setCurrentIndex(1)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainApp()
    main_window.show()
    sys.exit(app.exec_())