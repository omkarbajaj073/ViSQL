import sys
from functools import cached_property

from PyQt6.QtCore import QRect, Qt
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import *

import logging

from components import CreateDb
from insert import InsertData
from tables import *

logging.basicConfig(level=logging.DEBUG)

class Home(QWidget):
  def __init__(self):
    super().__init__()
    self.layout = QVBoxLayout()

    header = QLabel()
    header.setText("VISQL")
    self.layout.addWidget(header)

    # self.layout.addWidget(create)

    self.setLayout(self.layout)


class MainWindow(QMainWindow):
    def __init__(self, widgets, **kwargs):
        super().__init__()
        self.setWindowTitle("ViSQL")

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
        self.view.setFixedSize(500, 300)
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
        self.query.triggered.connect(self.set_query_page)
        self.query.setEnabled(0)
        query_menu.addAction(self.query)

        self.create_t = QAction(query_menu)
        self.create_t.setText("Create Table")
        self.create_t.triggered.connect(self.create_table)
        self.create_t.setEnabled(0)
        query_menu.addAction(self.create_t)

        self.insert = QAction(query_menu)
        self.insert.setText("Insert Rows")
        self.insert.triggered.connect(self.insert_rows)
        self.insert.setEnabled(0)
        query_menu.addAction(self.insert)


    def show_create(self):
        dialog = CreateDb()
        dialog.exec()
        
    def set_query_page(self):
        # ! Very bad solution - find a way to pop the current widget off the stack before adding the next
        widget_to_add = ManageTables(self.database)
        self.view.stacked_widget.addWidget(widget_to_add)
        cnt = self.view.stacked_widget.count()
        self.view.stacked_widget.setCurrentIndex(cnt - 1)

    def create_table(self):
        widget_to_add = CreateTable(self.database)
        self.view.stacked_widget.addWidget(widget_to_add)
        cnt = self.view.stacked_widget.count()
        self.view.stacked_widget.setCurrentIndex(cnt - 1)

    def insert_rows(self):
        widget_to_add = InsertData(self.database)
        self.view.stacked_widget.addWidget(widget_to_add)
        cnt = self.view.stacked_widget.count()
        self.view.stacked_widget.setCurrentIndex(cnt - 1)


    def use_db(self, db):
        self.database = db
        self.view.setWindowTitle(f'VISQL: {db.upper()}')
        self.query.setEnabled(1)
        self.create_t.setEnabled(1)
        self.insert.setEnabled(1)

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
    w = MainWindow([widget1, QWidget()], host='localhost', user='root', password='sql123')
    m = Menu(w)
    w.show()
    app.exec()


if __name__ == "__main__":
    main()