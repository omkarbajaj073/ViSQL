from PyQt6.QtWidgets import *

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
       

class Table(QDialog):
  def __init__(self, cursor, table, attributes=None, constraints=None, order_by=None, join=False, other_table=None, group_by=False, func=None, attribute=None, group_by_attr=None):
    super().__init__()

    self.showMaximized()

    layout = QVBoxLayout()
    if not join and not group_by:
      self.results = get_data(cursor, table, attributes, constraints, order_by)

    elif join:
      assert(other_table is not None)
      self.results = natural_join(cursor, table, other_table)
      des = cursor.description
      # get_attributes
      attributes = list(map(lambda x: x[0], des))
      
    elif group_by:
      self.results = group_by_data(cursor, table, func, attribute, constraints, group_by_attr)
      des = cursor.description
      # get_attributes
      attributes = list(map(lambda x: x[0], des))
    
    
    try:
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
    except:
      dialog = ErrorDialog("No data in the table")
      dialog.exec()
      self.close()


class Constraint(QDialog):
  def __init__(self, parent, attributes):
    super().__init__()
    self.parent = parent
    self.constraints = ['Relational', 'List', 'Regex', 'Is Null', "Is Not Null"]
    
    self.select_constraint = QComboBox()
    self.select_constraint.addItems(self.constraints)
    self.select_constraint.activated.connect(self.constraint_selected)

    atts = attributes
    self.layout = QVBoxLayout()

    self.combo_boxes = [QComboBox() for _ in range(5)]
    for box in self.combo_boxes:
      box.addItems(atts)

    self.widgets = [QWidget() for _ in range(5)]
    
    layouts = [QHBoxLayout() for _ in range(5)]
    
    # * Layout for comparisons
    self.comparators = QComboBox()
    compare = ['=', '!=', '<', '>', '<=', '>=']
    self.comparators.addItems(compare)
    self.compare_value = QLineEdit()
    
    layouts[0].addWidget(self.combo_boxes[0])
    layouts[0].addWidget(self.comparators)
    layouts[0].addWidget(self.compare_value)
    
    
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
    
    self.combo_boxes[1].activated.connect(self.clear_values)
    layouts[1].addWidget(self.combo_boxes[1])
    layouts[1].addLayout(sublayout)
    layouts[1].addWidget(self.values)
    layouts[1].addWidget(self.clear_values_btn)
    
    
    # * layout for regex
    layouts[2].addWidget(self.combo_boxes[2])
    self.regex = QLineEdit()
    layouts[2].addWidget(QLabel("Regex: "))
    layouts[2].addWidget(self.regex)
    

    for i in range(5):
      self.widgets[i].setLayout(layouts[i])
      self.widgets[i].hide()

    self.cur_layout = None

    self.btn = QPushButton("Add condition")
    self.btn.clicked.connect(self.add_constraint)

    self.layout.addWidget(QLabel("Select condition type:"))
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
    attr = self.combo_boxes[self.cur_layout].currentText()
    constraint = None
    if self.cur_layout == 0:
      constraint = f'{attr} {self.comparators.currentText()} {self.compare_value.text()}'
    elif self.cur_layout == 1:
      constraint = f'{attr} in ({self.values.text()})'
    elif self.cur_layout == 2:
      constraint = f'{attr} like {self.regex.text()}'
    elif self.cur_layout == 3:
      constraint = f'{attr} is null'
    elif self.cur_layout == 4:
      constraint = f'{attr} is not null'
      
    self.parent.constraints.append(constraint)
    cur = self.parent.display_constraints.text()
    new = f'{cur}, {constraint}' if cur else constraint
    self.parent.display_constraints.setText(new)
    logging.info("This piece of code is reached - add constriant")
    # TODO: Update the parent component
    self.close()

  
  def add_value(self):
    value = self.cur_value.text()
    if value in self.selected_values:
      return

    self.selected_values.append(value)
    cur = self.values.text()
    new = f'{cur}, {value}' if cur != 'No values added.' else value
    self.values.setText(new)
    self.cur_value.setText("")
  
  def clear_values(self):
    self.selected_values.clear()
    self.values.setText('No values added.') 
    

class ConstraintsBox(QWidget):
  def __init__(self):
    super().__init__()
    self.constraints = []
    self.attributes = None
    
    btn_constraint = QPushButton("Add Condition")
    btn_constraint.clicked.connect(self.add_constraint)
    
    self.display_constraints = QLabel()
    self.reset_constraints = QPushButton("Remove all conditions")
    self.reset_constraints.clicked.connect(self.call_reset_constraints)
    
    layout = QVBoxLayout()
    layout.addWidget(btn_constraint)
    layout.addWidget(self.display_constraints)
    layout.addWidget(self.reset_constraints)
    self.setLayout(layout)

  def call_reset_constraints(self):
    self.display_constraints.setText("")
    self.constraints.clear()

  def add_constraint(self):
    if self.attributes is not None:
      dialog = Constraint(self, self.attributes)
      dialog.exec()
    else:
      dialog = ErrorDialog("Please select a table")
      dialog.exec()
  

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
    self.constraints_box = ConstraintsBox()
    layout_order = QHBoxLayout()
    layout_order.addWidget(QLabel("Sorted by: "))
    self.order_dropdown = QComboBox()
    self.order_dropdown.setDisabled(True)

    layout_order.addWidget(self.order_dropdown)

    # TODO: Disable button when no text in table
    self.btn_query = QPushButton("Run Query")
    self.btn_query.clicked.connect(lambda: self.run_query())
    self.btn_query.setDisabled(True)

    layout.addLayout(layout_table)
    layout.addLayout(layout_att)
    layout.addWidget(self.att_selected)
    layout.addWidget(self.constraints_box)
    layout.addLayout(layout_order)
    layout.addWidget(self.btn_query)

    self.setLayout(layout)

  def table_activated(self):

    self.btn_query.setDisabled(False)
    self.selected_attributes.clear()
    self.att_dropdown.setDisabled(False)
    self.att_dropdown.clear()

    table = self.table_dropdown.currentText()
    
    self.all_attributes = list(get_table_attributes(self.cur, table))
    
    self.constraints_box.attributes = self.all_attributes.copy()
    self.att_dropdown.addItems(self.all_attributes)

    self.order_dropdown.setDisabled(False)
    self.order_dropdown.clear()

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

  def run_query(self):
    table = self.table_dropdown.currentText()
    attributes = self.selected_attributes
    
    # * FLAG @Ananth - just use this to get the constraints. it returns a list of the formated constraints for the query (see utils for next comment)
    constraints = self.constraints_box.constraints
    order_by = self.order_dropdown.currentText()
    if order_by in ['', 'None']:
      order_by = None

    if attributes:
      show_table = Table(self.cur, table, attributes, constraints, order_by)
      show_table.exec()
    else:
      error_dialog = ErrorDialog("Please make sure the table and at least 1 attribute is selected.")
      error_dialog.exec()


class UpdateQueries(QWidget):
  def __init__(self, con):
    super().__init__()
    self.cur = con.cursor()

    layout = QVBoxLayout()
    layout_table = QHBoxLayout()
    table_title = QLabel("Table: ")
    self.table_dropdown = QComboBox()
    self.table_dropdown.addItems(get_tables(self.cur))
    self.table_dropdown.activated.connect(self.table_activated)

    layout_table.addWidget(table_title)
    layout_table.addWidget(self.table_dropdown)

    layout_att = QHBoxLayout()

    self.att_dropdown = QComboBox()
    self.att_dropdown.setDisabled(True)
    self.update_value = QLineEdit()

    layout_att.addWidget(QLabel("Set Attribute: "))
    layout_att.addWidget(self.att_dropdown)
    layout_att.addWidget(QLabel("To"))
    layout_att.addWidget(self.update_value)
    
    # * Where functionality

    self.constraints_box = ConstraintsBox()
    # TODO: Disable button when no text in table
    self.btn_query = QPushButton("Run Query")
    self.btn_query.clicked.connect(lambda: self.run_query())
    self.btn_query.setDisabled(True)

    layout.addLayout(layout_table)
    layout.addLayout(layout_att)
    layout.addWidget(self.constraints_box)
    layout.addWidget(self.btn_query)
    self.setLayout(layout)


  def table_activated(self):
    self.btn_query.setDisabled(False)
    self.att_dropdown.setDisabled(False)
    self.att_dropdown.clear()

    table = self.table_dropdown.currentText()
    self.all_attributes = list(get_table_attributes(self.cur, table))
    self.constraints_box.attributes = self.all_attributes.copy()
    self.att_dropdown.addItems(self.all_attributes)
    
  def run_query(self):
    table = self.table_dropdown.currentText()
    attribute = self.att_dropdown.currentText()
    value = self.update_value.text()
    constraints = self.constraints_box.constraints.copy()
    update_data(self.cur, table, attribute, value, constraints)
    
  def close(self):
    self.con.close()
    super().close()

    
class GroupBy(QWidget):
  def __init__(self, con):
    super().__init__()
    self.cur = con.cursor()

    layout = QVBoxLayout()
    layout_table = QHBoxLayout()
    table_title = QLabel("Table: ")
    self.table_dropdown = QComboBox()
    self.table_dropdown.addItems(get_tables(self.cur))
    self.table_dropdown.activated.connect(self.table_activated)
    
    layout_table.addWidget(table_title)
    layout_table.addWidget(self.table_dropdown)


    layout_att = QHBoxLayout()
    att_title = QLabel("Function: ")

    self.agg_function = QComboBox()
    functions = ['max', 'min', 'avg', 'sum', 'count', 'count(*)']
    self.agg_function.addItems(functions)
    self.agg_function.setDisabled(True)
    
    self.att_dropdown = QComboBox()
    self.att_dropdown.setDisabled(True)

    layout_att.addWidget(att_title)
    layout_att.addWidget(self.agg_function)
    layout_att.addWidget(self.att_dropdown)


    # * Where functionality
    self.constraints_box = ConstraintsBox()
    
    layout_group = QHBoxLayout()
    layout_group.addWidget(QLabel("Grouped by: "))
    self.group_dropdown = QComboBox()
    self.group_dropdown.setDisabled(True)

    layout_group.addWidget(self.group_dropdown)

    # TODO: Disable button when no text in table
    self.btn_query = QPushButton("Run Query")
    self.btn_query.clicked.connect(lambda: self.run_query())
    self.btn_query.setDisabled(True)

    layout.addLayout(layout_table)
    layout.addLayout(layout_att)
    layout.addWidget(self.constraints_box)
    layout.addLayout(layout_group)
    layout.addWidget(self.btn_query)
    self.setLayout(layout)


  def table_activated(self):
    
    self.btn_query.setDisabled(False)
    self.agg_function.setDisabled(False)
    self.att_dropdown.setDisabled(False)
    self.att_dropdown.clear()

    table = self.table_dropdown.currentText()
    self.all_attributes = list(get_table_attributes(self.cur, table))
    self.constraints_box.attributes = self.all_attributes.copy()
    self.att_dropdown.addItems(self.all_attributes)

    self.group_dropdown.setDisabled(False)
    self.group_dropdown.clear()

    self.all_attributes = list(get_table_attributes(self.cur, table))
    self.group_dropdown.addItems(self.all_attributes)

    
  def run_query(self):
    table = self.table_dropdown.currentText()
    attribute = self.att_dropdown.currentText()
    func = self.agg_function.currentText()
    constraints = self.constraints_box.constraints
    group_by = self.group_dropdown.currentText()
    
    table = Table(self.cur, table, group_by=True, func=func, attribute=attribute, constraints=constraints, group_by_attr=group_by)
    table.exec()
    
   
    
class DeleteData(QWidget):
  def __init__(self, con):
    super().__init__()
    self.con = con
    self.cur = con.cursor()

    layout = QVBoxLayout()
    layout_table = QHBoxLayout()
    table_title = QLabel("Table: ")
    self.table_dropdown = QComboBox()
    self.table_dropdown.addItems(get_tables(self.cur))
    self.table_dropdown.activated.connect(self.table_activated)

    layout_table.addWidget(table_title)
    layout_table.addWidget(self.table_dropdown)
    
    self.constraints_box = ConstraintsBox()

    # TODO: Disable button when no text in table
    self.btn_delete = QPushButton("Delete Rows")
    self.btn_delete.clicked.connect(lambda: self.run_delete())
    self.btn_delete.setDisabled(True)

    layout.addLayout(layout_table)
    layout.addWidget(self.constraints_box)
    layout.addWidget(self.btn_delete)

    self.setLayout(layout)


  def table_activated(self):
    self.btn_delete.setDisabled(False)
    table = self.table_dropdown.currentText()
    self.constraints_box.attributes = list(get_table_attributes(self.cur, table))

  def run_delete(self):
    table = self.table_dropdown.currentText()
    constraints = self.constraints_box.constraints
    delete_rows(self.con, table, constraints)
    

class NaturalJoin(QWidget):
  def __init__(self, con):
    super().__init__()
    self.cur = con.cursor()

    layout = QVBoxLayout()
    sublayout = QHBoxLayout()
    
    tables = list(get_tables(self.cur))
    
    table_title_1 = QLabel("Table 1: ")
    self.table_dropdown_1 = QComboBox()
    self.table_dropdown_1.addItems(tables)

    table_title_2 = QLabel("Table 2: ")
    self.table_dropdown_2 = QComboBox()
    self.table_dropdown_2.addItems(tables)


    sublayout.addWidget(table_title_1)
    sublayout.addWidget(self.table_dropdown_1)
    sublayout.addWidget(table_title_2)
    sublayout.addWidget(self.table_dropdown_2)
    
    btn = QPushButton("Join")
    btn.clicked.connect(self.run_query)
    
    layout.addWidget(QLabel("Select tables to join."))
    layout.addLayout(sublayout)
    layout.addWidget(btn)
    
    self.setLayout(layout)

  def run_query(self):
    table_1 = self.table_dropdown_1.currentText()
    table_2 = self.table_dropdown_2.currentText()
    
    if table_1 == table_2 or table_1 == '' or table_2 == '':
      dialog = ErrorDialog("Please select different tables")
      dialog.exec()
      return
    
    show_table = Table(self.cur, table_1, other_table=table_2, join=True)
    show_table.exec()
    

    