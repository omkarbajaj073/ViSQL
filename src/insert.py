from PyQt6.QtWidgets import *

import sys
from constants import *
from components import *

import logging
# from styles import stylesCreateTable
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
    self.con = connector.connect(host=host, password=password, user=user, database=db) 
    self.cur = self.con.cursor()
    layout = QVBoxLayout()
    
    self.table_name = None

    layout_title = QHBoxLayout()
    layout_title.addWidget(QLabel("Table Name: "))
    self.name = QComboBox()
    self.name.activated.connect(self.set_table)
    self.name.addItems(get_tables(self.cur))
    # use_table = QPushButton("Use Table")
    # use_table.clicked.connect(self.set_table)
    layout_title.addWidget(self.name)
    # layout_title.addWidget(use_table)

    add_att = QPushButton("Add Data Item")
    add_att.clicked.connect(self.add_item)

    # TODO: Adjust the geometry of the table

    self.table = QTableWidget(0, 0)

    create_table_btn = QPushButton("Insert Data")
    create_table_btn.clicked.connect(self.insert_data)
    

    layout.addLayout(layout_title)
    layout.addWidget(add_att)
    layout.addWidget(self.table)
    layout.addWidget(create_table_btn)

    self.data = []
    self.setLayout(layout)


  def add_item(self):
    dialog = DataItem(self, self.table_name)
    dialog.exec()
    
  def set_table(self):
    self.table_name = self.name.currentText()
    header = get_table_attributes(self.cur, self.table_name)
    self.table.setRowCount(0)
    self.table.setColumnCount(len(header))
    self.table.setHorizontalHeaderLabels(header)


  def insert_data(self):
    # ! Add a few checks
    name = self.name.currentText()
    logging.debug(f'{name=}')

    # TODO: Handle data types in add data item
    # TODO: Format and run query - match case sorta syntax to decide quotes.
    # TODO: ComboBox for enum datatype
    # * desc table returns a list. second element is a byte string with the datatype.
    # create_table(self.cur, self.name.text(), self.attributes)
    # TODO: Query

    data = format_insert_data(self.data)
    insert_data(self.con, name, data)
    
    
  def close(self):
    self.con.close()
    super().close()

