from PyQt6.QtWidgets import *
from components import *

import logging
from utils import *
from constants import *

logging.basicConfig(level=logging.DEBUG)


class ManageTables(QWidget):

  # ! Need to rerender when different database selected
  def __init__(self, db):
    super().__init__()

    self.con = connector.connect(host=host, password=password, user=user, database=db) # ! Update parameters eventually
    logging.info("connected" if self.con.is_connected() else "not connected but no error")

    layout = QVBoxLayout()

    db_action_layout = QHBoxLayout()
    check1 = QRadioButton('Select')
    check1.toggled.connect(lambda:self.select_action(check1))
    check2 = QRadioButton('Update')
    check2.toggled.connect(lambda:self.select_action(check2))
    check3 = QRadioButton('Aggregate Functions')
    check3.toggled.connect(lambda:self.select_action(check3))
    

    db_action_layout.addWidget(check1)
    db_action_layout.addWidget(check2)
    # * Select action layout
    self.select_layout = SelectQueries(self.con)
    self.update_layout = UpdateQueries(self.con)
    self.group_layout = GroupBy(self.con)

    self.select_layout.hide()
    self.update_layout.hide()
    self.group_layout.hide()

    layout.addLayout(db_action_layout)
    layout.addWidget(self.select_layout)
    layout.addWidget(self.update_layout)

    self.setLayout(layout)


  def select_action(self, b):
    if b.text() == "Select":
      if b.isChecked():
        self.select_layout.show()
      else:
        self.select_layout.hide()
        
    if b.text() == "Update":
      if b.isChecked():
        self.update_layout.show()
      else:
        self.update_layout.hide()
        
    if b.text() == "Aggregate Functions":
      if b.isChecked():
        self.group_layout.show()
      else:
        self.group_layout.hide()

        


class CreateTable(QWidget):
  def __init__(self, db):
    super().__init__()
    self.con = connector.connect(host=host, password=password, user=user, database=db) # ! Update parameters eventually
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



