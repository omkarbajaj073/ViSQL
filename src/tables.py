from PyQt6.QtWidgets import *
from components import *

import logging
from utils import *
from constants import *

from styles import queryStyles

logging.basicConfig(level=logging.DEBUG)


class ManageTables(QWidget):

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
    check4 = QRadioButton('Delete')
    check4.toggled.connect(lambda:self.select_action(check4))
    check5 = QRadioButton('Natural Join')
    check5.toggled.connect(lambda:self.select_action(check5))

    db_action_layout.addWidget(check1)
    db_action_layout.addWidget(check2)
    db_action_layout.addWidget(check3)
    db_action_layout.addWidget(check4)
    db_action_layout.addWidget(check5)

    # * Select action layout
    self.select_layout = SelectQueries(self.con)
    self.update_layout = UpdateQueries(self.con)
    self.group_layout = GroupBy(self.con)
    self.delete_layout = DeleteData(self.con)
    self.join_layout = NaturalJoin(self.con)

    self.select_layout.hide()
    self.update_layout.hide()
    self.group_layout.hide()
    self.delete_layout.hide()
    self.join_layout.hide()


    layout.addLayout(db_action_layout)
    layout.addWidget(self.select_layout)
    layout.addWidget(self.update_layout)
    layout.addWidget(self.group_layout)
    layout.addWidget(self.delete_layout)
    layout.addWidget(self.join_layout)

    self.setLayout(layout)
    self.setMinimumSize(750, 500)
    self.setStyleSheet(queryStyles) # > FLAG @Ananth. Using stylesheets.


  def select_action(self, b):
    if b.text() == "Select":
      if b.isChecked():
        self.select_layout.show()
      else:
        self.select_layout.hide()
        
    elif b.text() == "Update":
      if b.isChecked():
        self.update_layout.show()
      else:
        self.update_layout.hide()
        
    elif b.text() == "Aggregate Functions":
      if b.isChecked():
        self.group_layout.show()
      else:
        self.group_layout.hide()
        
    elif b.text() == "Delete":
      if b.isChecked():
        self.delete_layout.show()
      else:
        self.delete_layout.hide()
        
    elif b.text() == "Natural Join":
      if b.isChecked():
        self.join_layout.show()
      else:
        self.join_layout.hide()
        
        
  def close(self):
    self.con.close()
    logging.info("Connection closed")
    super().close()


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
    self.setStyleSheet(queryStyles)


  def add_attribute(self):
    dialog = CreateAttribute(self)
    dialog.exec()


  def create_table(self):
    # ! Add a few checks
    name = self.name.text()
    logging.debug(f'{name=}')
    create_table(self.cur, self.name.text(), self.attributes)
    dialog = MessageDialog("Table created!")
    dialog.exec()
    
    
  def close(self):
    self.con.close()
    super().close()


class DeleteTable(QWidget):
  def __init__(self, db):
    super().__init__()
    self.con = connector.connect(host=host, password=password, user=user, database=db) # ! Update parameters eventually
    self.cur = self.con.cursor()
    layout = QVBoxLayout()

    layout_table = QHBoxLayout()
    table_title = QLabel("Table: ")
    self.table_dropdown = QComboBox()
    self.table_dropdown.addItems(get_tables(self.cur))
    self.table_dropdown.activated.connect(self.table_activated)

    layout_table.addWidget(table_title)
    layout_table.addWidget(self.table_dropdown)

    self.delete_table_btn = QPushButton("Delete Table")
    self.delete_table_btn.setDisabled(True)
    self.delete_table_btn.clicked.connect(self.delete_table)
    

    layout.addLayout(layout_table)
    layout.addWidget(self.delete_table_btn)

    self.setLayout(layout)
    self.setStyleSheet(queryStyles)

    
  def table_activated(self):
    self.delete_table_btn.setDisabled(False)


  def delete_table(self):
    table = self.table_dropdown.currentText()
    delete_table(self.cur, table)
    logging.info(f'{table} table DELETED')
    
    
  def close(self):
    self.con.close()
    super().close()


class DescribeTable(QWidget):
  def __init__(self, db):
    super().__init__()
    self.con = connector.connect(host=host, password=password, user=user, database=db) # ! Update parameters eventually
    self.cur = self.con.cursor()
    self.layout = QVBoxLayout()

    layout_table = QHBoxLayout()
    table_title = QLabel("Table: ")
    self.table_dropdown = QComboBox()
    self.table_dropdown.addItems(get_tables(self.cur))
    self.table_dropdown.activated.connect(self.table_activated)

    layout_table.addWidget(table_title)
    layout_table.addWidget(self.table_dropdown)

    self.desc_table_btn = QPushButton("Describe Table")
    self.desc_table_btn.setDisabled(True)
    self.desc_table_btn.clicked.connect(self.desc_table)    

    self.layout.addLayout(layout_table)
    self.layout.addWidget(self.desc_table_btn)

    self.setLayout(self.layout)
    self.setMinimumSize(750, 500)
    self.setStyleSheet(queryStyles)
    
  def table_activated(self):
    self.desc_table_btn.setDisabled(False)
    
  def desc_table(self):
    table_name = self.table_dropdown.currentText()
    
    try:
      self.table.hide()
    except:
      pass

    self.cur.execute(f"desc {table_name}")
    self.results = self.cur.fetchall()

    headers = list(map(lambda i : i[0], self.cur.description))

    try:
      x, y = len(self.results), len(self.results[0])
      self.table = QTableWidget(x, y)
      self.table.setHorizontalHeaderLabels(headers)

      for i in range(x):
        for j in range(y):
          item = self.results[i][j]
          if type(item) is bytes:
            cell = QTableWidgetItem(str(item, 'utf-8'))
          else:
            cell = QTableWidgetItem(str(item))
          self.table.setItem(i, j, cell)

      self.layout.addWidget(self.table)
      
    except Exception as e:
      dialog = MessageDialog(str(e))
      dialog.exec()
      
    logging.debug(f"{self.results=}")


    