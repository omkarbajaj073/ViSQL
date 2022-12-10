import sys
from functools import cached_property

from PyQt6.QtCore import QRect, Qt
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import *

from components import CreateDb
from insert import InsertData
from help import Help
from tables import *
from constants import *
from styles import homeStyles


class Home(QWidget):
  '''Page displayed on opening application'''
  def __init__(self):
    super().__init__()
    self.layout = QVBoxLayout()
    
    # ViSQL Banner
    header = QLabel()
    header.setText("VISQL")
    self.layout.addWidget(header)

    self.setLayout(self.layout)


class MainWindow(QMainWindow):
    '''Main window through which application runs'''
    def __init__(self, widgets, **kwargs):
        super().__init__()
        self.setWindowTitle("ViSQL")
        self.setFixedSize(800, 600)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create a stack of widgets that can be viewed one at a time
        lay = QVBoxLayout(central_widget)
        lay.addWidget(self.stacked_widget, alignment=Qt.AlignmentFlag.AlignCenter)

        # Push initial pages to stack
        for page in widgets:
            self.stacked_widget.addWidget(page)

    @cached_property
    def stacked_widget(self):
        return QStackedWidget()


class Menu:
    '''Menu options page'''
    def __init__(self, MainWindow):
        super().__init__()
        self.view = MainWindow
        self.database = None
        self.view.setWindowTitle(f"VISQL: (NO DATABASE SELECTED)")

        # Toolbar/Menu ribbon
        self.menuBar = QMenuBar()
        self.menuBar.setGeometry(QRect(0, 0, 277, 22))
        self.view.setMenuBar(self.menuBar)

        # Dropdown for accessing database
        self.open = QMenu(self.menuBar)
        self.open.setTitle("Database Functions")
        
        self.menuBar.addAction(self.open.menuAction())
        
        # Nested dropdown for selecting databases
        self.select = QMenu(self.menuBar)
        self.select.setTitle("Select Database")
        self.select.aboutToShow.connect(self.display_dbs) # Updates dropdown items when clicked
        self.open.addMenu(self.select)

        # Create new database dropdown option
        self.create = QAction(self.menuBar)
        self.create.setText("Create Database")
        self.create.triggered.connect(self.show_create)
        self.open.addAction(self.create)
        
        # Menu for all table operations
        query_menu = self.menuBar.addMenu("Manage Tables")

        # Querying table option
        self.query = QAction(query_menu)
        self.query.setText("Queries")
        self.query.triggered.connect(lambda: self.set_main_widget(ManageTables(self.database)))
        self.query.setEnabled(0) # Disable button until databse selected
        query_menu.addAction(self.query)
        
        # Create table option
        self.create_t = QAction(query_menu)
        self.create_t.setText("Create Table")
        self.create_t.triggered.connect(lambda: self.set_main_widget(CreateTable(self.database)))
        self.create_t.setEnabled(0)
        query_menu.addAction(self.create_t)

        # Insert rows option
        self.insert = QAction(query_menu)
        self.insert.setText("Insert Rows")
        self.insert.triggered.connect(lambda: self.set_main_widget(InsertData(self.database)))
        self.insert.setEnabled(0)
        query_menu.addAction(self.insert)

        # Delete table option
        self.delete_t = QAction(query_menu)
        self.delete_t.setText("Delete Table")
        self.delete_t.triggered.connect(lambda: self.set_main_widget(DeleteTable(self.database)))
        self.delete_t.setEnabled(0)
        query_menu.addAction(self.delete_t)

        # Display table attributes option
        self.desc_t = QAction(query_menu)
        self.desc_t.setText("Describe Table")
        self.desc_t.triggered.connect(lambda: self.set_main_widget(DescribeTable(self.database)))
        self.desc_t.setEnabled(0)
        query_menu.addAction(self.desc_t)
        
        # Help page menubar button
        help_action = QAction(self.menuBar)
        help_action.setText("Help")
        help_action.triggered.connect(self.show_help)
        self.menuBar.addAction(help_action)        

    def show_create(self):
        # Dialog to create a new database
        dialog = CreateDb()
        dialog.exec()
        
    def show_help(self):
        # Dialog to display the help page
        dialog = Help()
        dialog.exec()
        
    def set_main_widget(self, widget_to_add):
        # Add table operation widget to page stack
        self.view.stacked_widget.addWidget(widget_to_add)
        cnt = self.view.stacked_widget.count()
        # Selecting page from stack to display
        self.view.stacked_widget.setCurrentIndex(cnt - 1)
 
    def use_db(self, db):
        # Updating window title to reflect databse in use
        self.database = db
        self.view.setWindowTitle(f'VISQL: {db.upper()}')
        save_to_file(f"INFO: CURRENT DATABASE: {db}") # Logging database change

        # Enable all menu actions after databse is selected
        self.query.setEnabled(1)
        self.create_t.setEnabled(1)
        self.insert.setEnabled(1)
        self.delete_t.setEnabled(1)
        self.desc_t.setEnabled(1)

    def display_dbs(self):
        databases = get_databases()
        self.select.clear() # Clear the database nested dropdown's contents
        # Add available databases to dropdown
        for db in databases:
            action = QAction(self.select)
            action.setText(db)
            action.triggered.connect(lambda args, db=db: self.use_db(db)) # Switches database on click
            self.select.addAction(action)


def main():
    # Intialising the application
    app = QApplication(sys.argv)
    widget1 = Home()
    w = MainWindow([widget1, QWidget()], host=host, user=user, password=password)
    m = Menu(w)
    w.setStyleSheet(homeStyles)
    w.show()
    app.exec()


if __name__ == "__main__":
    main()