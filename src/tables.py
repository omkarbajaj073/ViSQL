from PyQt6.QtWidgets import *
import sys

from components import *

import logging
from styles import stylesCreateTable
from utils import *

logging.basicConfig(level=logging.DEBUG)


class ManageTables(QWidget):

  # ! Need to rerender when different database selected
  def __init__(self, db):
    super().__init__()

    # db = self.
    self.con = connector.connect(host='localhost', password='sql123', user='root', database=db) # ! Update parameters eventually
    logging.info("connected" if self.con.is_connected() else "not connected but no error")

    layout = QVBoxLayout()
    # layout.addWidget()

    db_action_layout = QHBoxLayout()
    check1 = QRadioButton('Select')
    check1.toggled.connect(lambda:self.select_action(check1))
    check2 = QRadioButton('Update')
    check2.toggled.connect(lambda:self.select_action(check2))

    db_action_layout.addWidget(check1)
    db_action_layout.addWidget(check2)
    # * Select action layout
    self.select_layout = SelectQueries(self.con)

    self.select_layout.hide()




    layout.addLayout(db_action_layout)
    layout.addWidget(self.select_layout)

    self.setLayout(layout)


  def select_action(self, b):
	
      if b.text() == "Select":
         if b.isChecked() == True:
            print(b.text() + " is selected")
            self.select_layout.show()
         else:
            print(b.text() + " is deselected")
            self.select_layout.hide()

				
      if b.text() == "Update":
         if b.isChecked() == True:
            logging.info(b.text() + " is selected")
         else:
            logging.info(b.text() + " is deselected")


class CreateAttribute(QDialog):
  def __init__(self):
    super().__init__()
    layout = QVBoxLayout()
    layout.addWidget("Sanity Check")
    self.setLayout(layout)


class CreateTables(QWidget):
  def __init__(self):
    super().__init__()
    layout = QVBoxLayout()

    layout_title = QHBoxLayout()
    layout_title.addWidget(QLabel("Table Name: "))
    self.name = QLineEdit()
    layout_title.addWidget(self.name)

    

    layout.addLayout(layout_title)
    self.setLayout(layout)

  	
'''
1. Table Name
2. Form to add attributes - 
  a. Name - textInput
  b. Data type - dropdown
  c. not null - checkbox
  d. primary key - checkbox
  e. foreign key - checkbox + 2 dropdowns / nested dropdown
  f. default
  g. check
  h. unique - checkbox
'''


