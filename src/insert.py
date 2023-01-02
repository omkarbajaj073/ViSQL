from PyQt6.QtWidgets import *

from styles import queryStyles
from constants import kwargs
from components import *

from utils import *

class DataItem(QDialog):
  '''Dialog to insert data for a row of the table'''
  def __init__(self, parent, table):
    super().__init__()
    self.parent = parent
    
    layout = QVBoxLayout()
    
    # Get the selected table's attributes for data entry
    labels = get_table_attributes(self.parent.cur, table)
    num_fields = len(labels)

    # Create an input box for each atttribute's data
    self.lineEdits = [QLineEdit() for i in range(num_fields)]
    layouts = [QHBoxLayout() for i in range(num_fields)]

    # Add attribute and data input to sublayouts
    for i in range(num_fields):
      layouts[i].addWidget(QLabel(labels[i]))
      layouts[i].addWidget(self.lineEdits[i])

    # Button to add data row
    self.set_att = QPushButton("Confirm")
    self.set_att.clicked.connect(self.set_attribute)

    # Add all sublayouts to main layout
    for sublayout in layouts:
      layout.addLayout(sublayout)
    
    layout.addWidget(self.set_att)

    self.setLayout(layout)


  def set_attribute(self):
    # Retrieve all data entered in input fields    
    params = [line.text() for line in self.lineEdits]
    # Pass row data to parent component
    self.parent.data.append(params)

    # Update parent component to display the new data row
    currentRowCount = self.parent.table.rowCount()
    self.parent.table.insertRow(currentRowCount)   

    for i, param in enumerate(params):
      self.parent.table.setItem(currentRowCount, i, QTableWidgetItem(param))

    self.close()  


class InsertData(QWidget):
  '''Insert data into an existing table'''
  def __init__(self, db):
    super().__init__()
    self.con = connector.connect(**kwargs, database=db) 
    self.cur = self.con.cursor()
    layout = QVBoxLayout()
    
    self.table_name = None
    # Sublayout to select table
    layout_title = QHBoxLayout()
    layout_title.addWidget(QLabel("Table Name: "))

    # Get all tables in current database
    self.name = QComboBox()
    self.name.activated.connect(self.set_table)
    self.name.addItems(get_tables(self.cur))
    
    layout_title.addWidget(self.name)

    # Open dialog to enter a row's data
    add_att = QPushButton("Add Data Item")
    add_att.clicked.connect(self.add_item)

    # Create an empty table to display data rows
    self.table = QTableWidget(0, 0)

    create_table_btn = QPushButton("Insert Data")
    create_table_btn.clicked.connect(self.insert_data)
    
    layout.addLayout(layout_title)
    layout.addWidget(add_att)
    layout.addWidget(self.table)
    layout.addWidget(create_table_btn)

    self.data = []
    self.setLayout(layout)
    self.setStyleSheet(queryStyles)


  def add_item(self):
    # Open dialog to enter a row's data
    dialog = DataItem(self, self.table_name)
    dialog.exec()
    

  def set_table(self):
    self.table_name = self.name.currentText()
    header = get_table_attributes(self.cur, self.table_name)
    # Set diplay table dimensions and attributes as header
    self.table.setRowCount(0)
    self.table.setColumnCount(len(header))
    self.table.setHorizontalHeaderLabels(header)


  def insert_data(self):
    # Retrieve the currently selected table
    name = self.name.currentText()
    # Format insert data for query
    data = format_insert_data(self.data)
    insert_data(self.con, name, data)
    
    
  def close(self):
    self.con.close()
    super().close()

