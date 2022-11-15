from PyQt6.QtWidgets import *

import sys

from components import *

import logging
from styles import stylesCreateTable
from utils import *
logging.basicConfig(level=logging.DEBUG)


class DataItem(QDialog):
  def __init__(self, parent, table):
    super().__init__()
    self.parent = parent
    layout = QVBoxLayout()
    # TODO: foreign key, check, unique
    labels = get_table_attributes(self.parent.cur, table)
    num_fields = len(labels)
    self.lineEdits = [QLineEdit() for i in range(num_fields)]
    layouts = [QHBoxLayout() for i in range(num_fields)]

    for i in range(num_fields):
      layouts[i].addWidget(QLabel(labels[i]))
      layouts[i].addWidget(self.lineEdits[i])

    self.set_att = QPushButton("Confirm")
    self.set_att.clicked.connect(self.set_attribute)

    for sublayout in layouts:
      layout.addLayout(sublayout)
    
    layout.addWidget(self.set_att)

    self.setLayout(layout)


  def set_attribute(self):
    # ! Add checks to make sure things work
    
    params = [line.text() for line in self.lineEdits]
    # TODO: Format before sending
    self.parent.data.append(params)

    currentRowCount = self.parent.table.rowCount()
    logging.debug(f'{currentRowCount=}')
    self.parent.table.insertRow(currentRowCount)   

    for i, param in enumerate(params):
      logging.debug("param: " + param)
      self.parent.table.setItem(currentRowCount, i, QTableWidgetItem(param))

    logging.debug(f'{self.parent.data=}')
    self.close()  


class InsertData(QWidget):
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

    self.data = []
    self.setLayout(layout)


  def add_attribute(self):
    dialog = CreateAttribute(self)
    dialog.exec()


  def create_table(self):
    # ! Add a few checks
    name = self.name.text()
    logging.debug(f'{name=}')
    # create_table(self.cur, self.name.text(), self.attributes)
    # TODO: Query
    dialog = SuccessDialog("Data Inserted!")
    dialog.exec()
    
    
  def close(self):
    self.con.close()
    super().close()

