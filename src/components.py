from PyQt6.QtWidgets import *
# import PyQt6.QtCore as QtCore

import mysql.connector as connector

from utils import *


class CreateDb(QDialog):
  def __init__(self):
    super().__init__()

    # ! Error label appears next to main layout
    mainlayout = QVBoxLayout()
    sublayout = QHBoxLayout()

    self.label = QLabel("Enter DB name: ")
    self.edit = QLineEdit()
    self.push = QPushButton("Create")
    self.push.clicked.connect(self.create_db)

    # TODO: Implement error field
    self.error = QLabel()

    sublayout.addWidget(self.label)
    sublayout.addWidget(self.edit)
    sublayout.addWidget(self.push)
    # sublayout.addWidget(self.error)

    mainlayout.addLayout(sublayout)
    mainlayout.addWidget(self.error)

    self.setLayout(mainlayout)

  def create_db(self):
    name = self.edit.text()

    if name.isidentifier():
      try:
        create_database(name)
        self.edit.hide()
        self.push.hide()
        self.error.hide()
        self.label.setText("Database created. Close this dialogue and proceed.")
      except connector.errors.DatabaseError:
        self.error.setText("A database with that name already exists.")
    else:
      self.error.setText("Invalid database name!")

class ErrorDialog(QDialog):
  def __init__(self, error):
    super().__init__()
    layout = QVBoxLayout()
    layout.addWidget(QLabel(error))
    self.setLayout(layout)
    
class SuccessDialog(QDialog):
  def __init__(self, txt):
    super().__init__()
    layout = QVBoxLayout()
    layout.addWidget(QLabel(txt))
    self.setLayout(layout)


class Table(QDialog):
  def __init__(self, cursor, table, attributes, order_by=None):
    super().__init__()

    layout = QVBoxLayout()

    self.results = get_data(cursor, table, attributes, order_by)
    x, y = len(self.results), len(self.results[0])
    self.table = QTableWidget(x, y)
    self.table.setHorizontalHeaderLabels(attributes)

    for i in range(x):
      for j in range(y):
        cell = QTableWidgetItem(str(self.results[i][j]))
        # TODO: Make cells read only
        # cell.setFlags(QtCore.Qt.ItemIsEnabled)
        self.table.setItem(i, j, cell)

    layout.addWidget(self.table)
    self.setLayout(layout)


class SelectQueries(QWidget):
  def __init__(self, con):
    super().__init__()

    layout = QVBoxLayout()

    self.cursor = con.cursor()
    
    layout_table = QHBoxLayout()
    table_title = QLabel("Table: ")
    self.table_dropdown = QComboBox()
    self.table_dropdown.addItems(get_tables(self.cursor))
    self.table_dropdown.activated.connect(self.table_activated)

    self.all_attributes = []
    self.selected_attributes = []

    layout_table.addWidget(table_title)
    layout_table.addWidget(self.table_dropdown)


    layout_att = QHBoxLayout()
    att_title = QLabel("Attributes: ")

    self.att_dropdown = QComboBox()
    self.att_dropdown.setDisabled(True)

    self.att_add = QPushButton("Add")
    self.att_add.clicked.connect(self.add_attribute)
    
    self.att_remove = QPushButton("Remove")
    self.att_remove.clicked.connect(lambda: self.remove_attribute())
    
    self.att_clear = QPushButton("Clear`")
    self.att_clear.clicked.connect(lambda: self.clear_attributes())

    # TODO: Solve the text overflow here
    self.att_addAll = QPushButton("Add all attributes")
    self.att_addAll.clicked.connect(lambda: self.add_all_attributes())
    
    self.att_selected = QLabel("No attribtues selected.")


    layout_att.addWidget(att_title)
    layout_att.addWidget(self.att_dropdown)
    layout_att.addWidget(self.att_add)
    layout_att.addWidget(self.att_remove)
    layout_att.addWidget(self.att_clear)
    layout_att.addWidget(self.att_addAll)


    layout_order = QHBoxLayout()
    layout_order.addWidget(QLabel("Sorted by: "))
    self.order_dropdown = QComboBox()
    self.order_dropdown.setDisabled(True)

    layout_order.addWidget(self.order_dropdown)


    # TODO: Disable button when no text in table
    btn = QPushButton("Run Query")
    btn.clicked.connect(lambda: self.run_query())

    layout.addLayout(layout_table)
    layout.addLayout(layout_att)
    layout.addWidget(self.att_selected)
    layout.addLayout(layout_order)
    layout.addWidget(btn)
    self.setLayout(layout)


  def table_activated(self):

    self.selected_attributes.clear()
    self.att_dropdown.setDisabled(False)
    self.att_dropdown.clear()

    table = self.table_dropdown.currentText()
    self.all_attributes = list(get_table_attributes(self.cursor, table))
    self.att_dropdown.addItems(self.all_attributes)

    self.order_dropdown.setDisabled(False)
    self.order_dropdown.clear()

    table = self.table_dropdown.currentText()
    self.all_attributes = list(get_table_attributes(self.cursor, table))
    self.order_dropdown.addItem("None")
    self.order_dropdown.addItems(self.all_attributes)

  def add_attribute(self):
    attribute = self.att_dropdown.currentText()
    if attribute in self.selected_attributes:
      return

    self.selected_attributes.append(attribute)
    self.att_selected.setText("Attributes: " + ', '.join(self.selected_attributes))

  def remove_attribute(self):
    attribute = self.att_dropdown.currentText()
    if attribute not in self.selected_attributes:
      return
    self.selected_attributes.remove(attribute)
    if self.selected_attributes:
      self.att_selected.setText("Attributes: " + ', '.join(self.selected_attributes))
    else:
      self.att_selected.setText("No attribtues selected.")
  
  def clear_attributes(self):
    self.selected_attributes.clear()
    self.att_selected.setText('No attributes selected.')

  def add_all_attributes(self):
    self.selected_attributes = self.all_attributes.copy()
    self.att_selected.setText('All attributes selected.')

  def run_query(self):
    table = self.table_dropdown.currentText()
    attributes = self.selected_attributes
    order_by = self.order_dropdown.currentText()
    if order_by in ['', 'None']:
      order_by = None

    if attributes:
      show_table = Table(self.cursor, table, attributes, order_by)
      show_table.exec()
    else:
      error_dialog = ErrorDialog("Please make sure the table and at least 1 attribute is selected.")
      error_dialog.exec()

  def close(self):
    self.con.close()
    super().close()
    


    
