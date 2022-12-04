import sys
from functools import cached_property

from PyQt6.QtCore import QRect, Qt
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import *

import logging

from components import CreateDb
from insert import InsertData
from help import Help
from tables import *
from constants import *
from styles import styles


logging.basicConfig(level=logging.DEBUG)

class Home(QWidget):
  def __init__(self):
    super().__init__()
    self.layout = QVBoxLayout()

    header = QLabel()
    header.setText("VISQL")
    self.layout.addWidget(header)

    self.setLayout(self.layout)


class MainWindow(QMainWindow):
    def __init__(self, widgets, **kwargs):
        super().__init__()
        self.setWindowTitle("ViSQL")
        self.setFixedSize(800, 600)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        lay = QVBoxLayout(central_widget)
        lay.addWidget(self.stacked_widget, alignment=Qt.AlignmentFlag.AlignCenter)

        for page in widgets:
            self.stacked_widget.addWidget(page)

    @cached_property
    def stacked_widget(self):
        return QStackedWidget()


class Menu:
    def __init__(self, MainWindow):
        super().__init__()
        self.view = MainWindow
        self.database = None
        self.view.setWindowTitle(f"VISQL: (NO DATABASE SELECTED)")

        self.menuBar = QMenuBar()

        self.menuBar.setGeometry(QRect(0, 0, 277, 22))
        self.view.setMenuBar(self.menuBar)
        self.open = QMenu(self.menuBar)
        self.open.setTitle("Database Functions")
        self.menuBar.addAction(self.open.menuAction())
        

        # * Select databases menu
        self.select = QMenu(self.menuBar)
        self.select.setTitle("Select Database")
        self.select.aboutToShow.connect(self.display_dbs)
        self.open.addMenu(self.select)

        self.create = QAction(self.menuBar)
        self.create.setText("Create Database")
        self.create.triggered.connect(self.show_create)
        self.open.addAction(self.create)
        
        query_menu = self.menuBar.addMenu("Manage Tables")

        self.query = QAction(query_menu)
        self.query.setText("Queries")
        self.query.triggered.connect(lambda: self.set_main_widget(ManageTables(self.database)))
        self.query.setEnabled(0)
        query_menu.addAction(self.query)

        self.create_t = QAction(query_menu)
        self.create_t.setText("Create Table")
        self.create_t.triggered.connect(lambda: self.set_main_widget(CreateTable(self.database)))
        self.create_t.setEnabled(0)
        query_menu.addAction(self.create_t)

        self.insert = QAction(query_menu)
        self.insert.setText("Insert Rows")
        self.insert.triggered.connect(lambda: self.set_main_widget(InsertData(self.database)))
        self.insert.setEnabled(0)
        query_menu.addAction(self.insert)

        self.delete_t = QAction(query_menu)
        self.delete_t.setText("Delete Table")
        self.delete_t.triggered.connect(lambda: self.set_main_widget(DeleteTable(self.database)))
        self.delete_t.setEnabled(0)
        query_menu.addAction(self.delete_t)

        self.desc_t = QAction(query_menu)
        self.desc_t.setText("Describe Table")
        self.desc_t.triggered.connect(lambda: self.set_main_widget(DescribeTable(self.database)))
        self.desc_t.setEnabled(0)
        query_menu.addAction(self.desc_t)
        
        help_action = QAction(self.menuBar)
        help_action.setText("Help")
        help_action.triggered.connect(self.show_help)
        self.menuBar.addAction(help_action)
        


    def show_create(self):
        dialog = CreateDb()
        dialog.exec()
        
    def show_help(self):
        dialog = Help()
        dialog.exec()
        
    def set_main_widget(self, widget_to_add):
        self.view.stacked_widget.addWidget(widget_to_add)
        cnt = self.view.stacked_widget.count()
        self.view.stacked_widget.setCurrentIndex(cnt - 1)
       
    def use_db(self, db):
        self.database = db
        self.view.setWindowTitle(f'VISQL: {db.upper()}')
        save_to_file(f"INFO: CURRENT DATABASE: {db}")
        self.query.setEnabled(1)
        self.create_t.setEnabled(1)
        self.insert.setEnabled(1)
        self.delete_t.setEnabled(1)
        self.desc_t.setEnabled(1)


    def display_dbs(self):
        databases = get_databases()
        self.select.clear()
        for db in databases:
            action = QAction(self.select)
            action.setText(db)
            action.triggered.connect(lambda args, db=db: self.use_db(db))
            self.select.addAction(action)


def main():
    app = QApplication(sys.argv)
    widget1 = Home()
    w = MainWindow([widget1, QWidget()], host=host, user=user, password=password)
    m = Menu(w)
    w.setStyleSheet(styles)
    w.show()
    app.exec()


if __name__ == "__main__":
    main()