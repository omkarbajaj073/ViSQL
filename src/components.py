from PyQt6.QtWidgets import *
# import PyQt6.QtCore as QtCore

import mysql.connector as connector

from utils import *




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


class Constraint(QDialog):
  def __init__(self, parent, table):
    super().__init__()
    self.parent = parent
    self.constraints = ['Logical', 'List', 'Regex', 'Is Null', "Is Not Null"]
    
    self.select_constraint = QComboBox()
    self.select_constraint.addItems(self.constraints)
    self.select_constraint.activated.connect(self.constraint_selected)

    atts = get_table_attributes(self.parent.cur, table)
    self.layout = QVBoxLayout()


    inds = {
      "comp": 0,
      "in": 1,
      "like": 2,
      "null": 3,
      "not_null": 4
    }

    self.combo_boxes = [QComboBox() for i in range(5)]
    for box in self.combo_boxes:
      box.addItems(atts)

    self.widgets = [QWidget() for i in range(5)]
    
    for widget in self.widgets:
      widget.hide()
    
    layouts = [QHBoxLayout() for _ in range(5)]

    # * Layouts for is null, is not null
    layouts[3].addWidget(self.combo_boxes[3])
    layouts[4].addWidget(self.combo_boxes[4])
    
    # * layout for in

    layouts[1] = QVBoxLayout()

    sublayout = QHBoxLayout()
    sublayout.addWidget(QLabel("Enter Value: "))
    self.cur_value = QLineEdit()
    self.add_value_btn = QPushButton("Add Value")
    self.add_value_btn.clicked.connect(self.add_value)
    sublayout.addWidget(self.cur_value)
    sublayout.addWidget(self.add_value_btn)
    
    self.selected_values = []
    self.values = QLabel()
    self.clear_values_btn = QPushButton("Clear All Values")
    self.clear_values_btn.clicked.connect(self.clear_values)
    
    self.combo_boxes[2].activated.connect(self.clear_values)
    layouts[1].addWidget(self.combo_boxes[2])
    layouts[1].addLayout(sublayout)
    layouts[1].addWidget(self.values)
    layouts[1].addWidget(self.clear_values_btn)


    for i in range(5):
      self.widgets[i].setLayout(layouts[i])

    self.cur_layout = None

    self.btn = QPushButton("Add constraint")
    self.btn.clicked.connect(self.add_constraint)

    self.layout.addWidget(QLabel("Select constraint type:"))
    self.layout.addWidget(self.select_constraint)
    for widget in self.widgets:
      self.layout.addWidget(widget)

    self.layout.addWidget(self.btn)

    self.setLayout(self.layout)

  def constraint_selected(self):
    if self.cur_layout is not None:
      self.widgets[self.cur_layout].hide()
    self.cur_layout = self.select_constraint.currentIndex()

    self.widgets[self.cur_layout].show()

  def add_constraint(self):
    if self.cur_layout == 0:
      pass
    if self.cur_layout == 1:
      pass
    if self.cur_layout == 2:
      pass
    if self.cur_layout == 3:
      pass
    if self.cur_layout == 4:
      pass
    logging.info("This piece of code is reached - add constriant")

  
  def add_value(self):
    value = self.cur_value.text()
    if value in self.selected_values:
      return

    self.selected_values.append(value)
    self.values.setText("Values: " + ', '.join(self.selected_values))
    self.cur_value.setText("")
  
  def clear_values(self):
    self.selected_values.clear()
    self.values.setText('No values added.')

    
    

class SelectQueries(QWidget):
  def __init__(self, con):
    super().__init__()
    self.cur = con.cursor()

    layout = QVBoxLayout()
    layout_table = QHBoxLayout()
    table_title = QLabel("Table: ")
    self.table_dropdown = QComboBox()
    self.table_dropdown.addItems(get_tables(self.cur))
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
    
    self.att_clear = QPushButton("Clear")
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


    # * Where functionality
    self.constraints = []
    
    btn_constraint = QPushButton("Add Constraint")
    btn_constraint.clicked.connect(self.add_constraint)
    
    self.display_constraints = QWidget()
    self.reset_constraints = QPushButton("Remove all constraints")
    self.reset_constraints.clicked.connect(lambda: logging.info("Constraints clicked"))

    layout_order = QHBoxLayout()
    layout_order.addWidget(QLabel("Sorted by: "))
    self.order_dropdown = QComboBox()
    self.order_dropdown.setDisabled(True)

    layout_order.addWidget(self.order_dropdown)

    # TODO: Disable button when no text in table
    btn_query = QPushButton("Run Query")
    btn_query.clicked.connect(lambda: self.run_query())

    layout.addLayout(layout_table)
    layout.addLayout(layout_att)
    layout.addWidget(self.att_selected)
    layout.addWidget(btn_constraint)
    layout.addWidget(self.display_constraints)
    layout.addWidget(self.reset_constraints)
    layout.addLayout(layout_order)
    layout.addWidget(btn_query)
    self.setLayout(layout)


  def table_activated(self):

    self.selected_attributes.clear()
    self.att_dropdown.setDisabled(False)
    self.att_dropdown.clear()

    table = self.table_dropdown.currentText()
    self.all_attributes = list(get_table_attributes(self.cur, table))
    self.att_dropdown.addItems(self.all_attributes)

    self.order_dropdown.setDisabled(False)
    self.order_dropdown.clear()

    table = self.table_dropdown.currentText()
    self.all_attributes = list(get_table_attributes(self.cur, table))
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

  def add_constraint(self):
    dialog = Constraint(self, self.table_dropdown.currentText())
    dialog.exec()
    
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
    


    
