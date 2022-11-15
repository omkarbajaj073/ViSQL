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

    self.con = connector.connect(host='localhost', password='sql123', user='root', database=db) # ! Update parameters eventually
    logging.info("connected" if self.con.is_connected() else "not connected but no error")

    layout = QVBoxLayout()

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
  def __init__(self, parent):
    super().__init__()
    layout = QVBoxLayout()
    # TODO: foreign key, check, unique
    num_fields = 5
    layouts = [QHBoxLayout() for i in range(num_fields)]
    labels = ['Name of Attribute', 'Data Type', 'Not Null', 'Primary Key', 'Default Value']

    for i in range(num_fields):
      layouts[i].addWidget(QLabel(labels[i]))

    self.name = QLineEdit()
    layouts[0].addWidget(self.name)

    self.type = QComboBox()
    types = ['Integer', 'Varchar(30)', 'Date'] # TODO
    self.type.addItems(types)
    layouts[1].addWidget(self.type)
    
    self.not_null = QCheckBox("Yes")
    layouts[2].addWidget(self.not_null)
    
    self.primary_key = QCheckBox("Yes")
    layouts[3].addWidget(self.primary_key)
    
    self.default = QLineEdit()
    layouts[4].addWidget(self.default)

    self.set_att = QPushButton("Confirm")
    self.set_att.clicked.connect(self.set_attribute)

    for sublayout in layouts:
      layout.addLayout(sublayout)
    
    layout.addWidget(self.set_att)

    self.setLayout(layout)
    self.parent = parent


  def set_attribute(self):
    # ! Add checks to make sure things work
    
    params = [self.name.text(), self.type.currentText(), self.not_null.isChecked(), self.primary_key.isChecked(), self.default.text()]
    self.parent.attributes.append(format_attribute(*params))

    params[2] = 'Yes' if params[2] else 'No'
    params[3] = 'Yes' if params[3] else 'No'
    params[4] = params[4] if params[4] else 'None'

    currentRowCount = self.parent.table.rowCount()
    logging.debug(f'{currentRowCount=}')
    self.parent.table.insertRow(currentRowCount)   

    for i, param in enumerate(params):
      logging.debug("param: " + param)
      self.parent.table.setItem(currentRowCount, i, QTableWidgetItem(param))

    logging.debug(f'{self.parent.attributes=}')
    self.close()  


class CreateTable(QWidget):
  def __init__(self, db):
    super().__init__()
    self.con = connector.connect(host='localhost', password='sql123', user='root', database=db) # ! Update parameters eventually
    self.cur = self.con.cursor()
    layout = QVBoxLayout()

    layout_title = QHBoxLayout()
    layout_title.addWidget(QLabel("Table Name: "))
    self.name = QLineEdit()
    layout_title.addWidget(self.name)

    add_att = QPushButton("Add Attribute")
    add_att.clicked.connect(self.add_attribute)

    self.attributes = []

    # TODO: Adjust the geometry of the table
    headers = ['Name', 'Data Type', 'Not Null?', 'Primary Key?', 'Default Value']
    self.table = QTableWidget(0, 5)
    self.table.setHorizontalHeaderLabels(headers)

    create_table_btn = QPushButton("Create Table")
    create_table_btn.clicked.connect(self.create_table)
    

    layout.addLayout(layout_title)
    layout.addWidget(add_att)
    layout.addWidget(self.table)
    layout.addWidget(create_table_btn)

    self.setLayout(layout)


  def add_attribute(self):
    dialog = CreateAttribute(self)
    dialog.exec()


  def create_table(self):
    # ! Add a few checks
    name = self.name.text()
    logging.debug(f'{name=}')
    create_table(self.cur, self.name.text(), self.attributes)
    dialog = SuccessDialog("Table created!")
    dialog.exec()
    
    
  def close(self):
    self.con.close()
    super().close()

  	
'''
2. Form to add attributes - 
  a. Name - textInput
  b. Data type - dropdown
  c. not null - checkbox
  d. primary key - checkbox
  e. foreign key - checkbox + 2 dropdowns / nested dropdown
  f. default
  g. check (if time permits)
  h. unique - checkbox
'''


