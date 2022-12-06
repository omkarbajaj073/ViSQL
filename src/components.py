from PyQt6.QtWidgets import *

import mysql.connector as connector

from utils import *
from styles import *


class CreateAttribute(QDialog):
  '''Dialog to create attribute while creating a new table'''
  def __init__(self, parent):
    super().__init__()
    layout = QVBoxLayout()

    num_fields = 5

    layouts = [QHBoxLayout() for i in range(num_fields)]
    labels = ['Name of Attribute', 'Data Type', 'Not Null', 'Primary Key', 'Default Value'] 

    # Adding titles to all sublayouts
    for i in range(num_fields):
      layouts[i].addWidget(QLabel(labels[i]))

    # Layout for attribute name
    self.name = QLineEdit()
    layouts[0].addWidget(self.name)

    # Layout for data type
    self.type = QComboBox()
    types = ['Integer', 'Varchar(30)', 'Varchar(500)', 'Date'] # TODO
    self.type.addItems(types)
    layouts[1].addWidget(self.type)
    
    # Layout for not null condition
    self.not_null = QCheckBox("Yes")
    layouts[2].addWidget(self.not_null)
    
    # Layout for primary key condition
    self.primary_key = QCheckBox("Yes")
    layouts[3].addWidget(self.primary_key)
    
    # Layout for default value
    self.default = QLineEdit()
    layouts[4].addWidget(self.default)

    # Add attribute
    self.set_att = QPushButton("Confirm")
    self.set_att.clicked.connect(self.set_attribute)

    # Add all attributes to main layout
    for sublayout in layouts:
      layout.addLayout(sublayout)
    
    layout.addWidget(self.set_att)

    self.setLayout(layout)
    self.parent = parent


  def set_attribute(self):
    
    # Formatting display for main window for new attribute
    params = [self.name.text(), self.type.currentText(), self.not_null.isChecked(), self.primary_key.isChecked(), self.default.text()]
    self.parent.attributes.append(format_attribute(*params))

    params[2] = 'Yes' if params[2] else 'No'
    params[3] = 'Yes' if params[3] else 'No'
    params[4] = params[4] if params[4] else 'None'


    # Update main window to display the new attribute
    currentRowCount = self.parent.table.rowCount()
    self.parent.table.insertRow(currentRowCount)   
    for i, param in enumerate(params):
      self.parent.table.setItem(currentRowCount, i, QTableWidgetItem(param))

    self.close()  


class CreateDb(QDialog):
  '''Dialog to create a new database'''
  def __init__(self):
    super().__init__()

    mainlayout = QVBoxLayout()
    sublayout = QHBoxLayout()

    self.label = QLabel("Enter DB name: ")
    self.edit = QLineEdit()
    self.push = QPushButton("Create")
    self.push.clicked.connect(self.create_db) # run the database creation query

    # Error field in case the name of the database is invalid
    self.error = QLabel()

    sublayout.addWidget(self.label)
    sublayout.addWidget(self.edit)
    sublayout.addWidget(self.push)

    mainlayout.addLayout(sublayout)
    mainlayout.addWidget(self.error)

    self.setLayout(mainlayout)

  def create_db(self):
    name = self.edit.text() # Get database name

    # Check if name is a valid attribute name (follows the same rules as python identifiers)
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
  '''Dialog with table to display results of all queries'''
  def __init__(self, cursor, table, attributes=None, conditions=None, order_by=None, join=False, other_table=None, group_by=False, func=None, attribute=None, group_by_attr=None):
    super().__init__()
    self.showMaximized()
    
    layout = QVBoxLayout()
    if not join and not group_by:
      # Normal select query
      self.results = get_data(cursor, table, attributes, conditions, order_by)
    elif join:
      # Natural join query
      self.results = natural_join(cursor, table, other_table)
    elif group_by:
      # Group by aggregate function query
      self.results = group_by_data(cursor, table, func, attribute, conditions, group_by_attr)
    
    # Get attribute names for table headers
    des = cursor.description
    attributes = list(map(lambda x: x[0], des))
    
    try:
      # Populate table with results
      x, y = len(self.results), len(self.results[0])
      self.table = QTableWidget(x, y)
      self.table.setHorizontalHeaderLabels(attributes)

      for i in range(x):
        for j in range(y):
          cell = QTableWidgetItem(str(self.results[i][j]))
          self.table.setItem(i, j, cell)

      layout.addWidget(self.table)
      self.setLayout(layout)
    except:
      dialog = MessageDialog("No data in the table")
      dialog.exec()
      self.close()


class Condition(QDialog):
  def __init__(self, parent, attributes):
    super().__init__()
    self.parent = parent
    
    self.conditions = ['Relational', 'List', 'Regex', 'Is Null', "Is Not Null"]
    
    # Choose the type of condition to add
    self.select_condition = QComboBox()
    self.select_condition.addItems(self.conditions)
    # Toggle between different types of conditions
    self.select_condition.activated.connect(self.condition_selected)

    # Attributes of table for current query
    atts = attributes
    self.layout = QVBoxLayout()

    # Attribute dropdowns
    self.combo_boxes = [QComboBox() for _ in range(5)]
    for box in self.combo_boxes:
      box.addItems(atts)

    self.widgets = [QWidget() for _ in range(5)]
    layouts = [QHBoxLayout() for _ in range(5)]
    
    # Layout for comparisons
    self.comparators = QComboBox()
    compare = ['=', '!=', '<', '>', '<=', '>=']
    self.comparators.addItems(compare)
    self.compare_value = QLineEdit()
    
    layouts[0].addWidget(self.combo_boxes[0])
    layouts[0].addWidget(self.comparators)
    layouts[0].addWidget(self.compare_value)
    
    
    # Layouts for is null, is not null
    layouts[3].addWidget(self.combo_boxes[3])
    layouts[4].addWidget(self.combo_boxes[4])
    
    # Layout for in
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
    
    
    # Layout for regex
    layouts[2].addWidget(self.combo_boxes[2])
    self.regex = QLineEdit()
    layouts[2].addWidget(QLabel("Regex: "))
    layouts[2].addWidget(self.regex)
    
    # Add all sublayouts to subwidgets
    for i in range(5):
      self.widgets[i].setLayout(layouts[i])
      self.widgets[i].hide()

    self.cur_layout = None

    self.btn = QPushButton("Add condition")
    self.btn.clicked.connect(self.add_condition)

    self.layout.addWidget(QLabel("Select condition type:"))
    self.layout.addWidget(self.select_condition)
    
    # Add all subwidets to main layout
    for widget in self.widgets:
      self.layout.addWidget(widget)

    self.layout.addWidget(self.btn)
    self.setLayout(self.layout)

  def condition_selected(self):
    # Toggle between layouts for various types of conditions
    if self.cur_layout is not None:
      self.widgets[self.cur_layout].hide()
    self.cur_layout = self.select_condition.currentIndex()

    self.widgets[self.cur_layout].show()

  def add_condition(self):
    attr = self.combo_boxes[self.cur_layout].currentText()
    condition = None
    
    # Format condition for query
    if self.cur_layout == 0:
      condition = f'{attr} {self.comparators.currentText()} {self.compare_value.text()}'
    elif self.cur_layout == 1:
      condition = f'{attr} in ({self.values.text()})'
    elif self.cur_layout == 2:
      condition = f'{attr} like {self.regex.text()}'
    elif self.cur_layout == 3:
      condition = f'{attr} is null'
    elif self.cur_layout == 4:
      condition = f'{attr} is not null'
    
    # Update parent component
    self.parent.conditions.append(condition)
    cur = self.parent.display_conditions.text()
    new = f'{cur}, {condition}' if cur else condition
    self.parent.display_conditions.setText(new)

    self.close()
  
  def add_value(self):
    # Utility function for in operator
    value = self.cur_value.text()
    if value in self.selected_values:
      return

    self.selected_values.append(value)
    cur = self.values.text()
    new = f'{cur}, {value}' if cur != 'No values added.' else value
    self.values.setText(new)
    self.cur_value.setText("")
  
  def clear_values(self):
    # Utility function for in operator
    self.selected_values.clear()
    self.values.setText('No values added.') 
    

class ConditionsBox(QWidget):
  '''Component to add conditions to query'''
  def __init__(self):
    super().__init__()
    self.conditions = []
    self.attributes = None
    
    btn_condition = QPushButton("Add Condition")
    btn_condition.clicked.connect(self.add_condition)
    
    self.display_conditions = QLabel()
    self.reset_conditions = QPushButton("Remove all conditions")
    self.reset_conditions.clicked.connect(self.call_reset_conditions)
    
    layout = QVBoxLayout()
    layout.addWidget(btn_condition)
    layout.addWidget(self.display_conditions)
    layout.addWidget(self.reset_conditions)
    self.setLayout(layout)

  def call_reset_conditions(self):
    self.display_conditions.setText("")
    self.conditions.clear()

  def add_condition(self):
    if self.attributes is not None:
      dialog = Condition(self, self.attributes)
      dialog.exec()
    else:
      dialog = MessageDialog("Please select a table")
      dialog.exec()
  

class SelectQueries(QWidget):
  '''Create select query to get data from tables'''
  def __init__(self, con):
    super().__init__()
    self.cur = con.cursor()

    layout = QVBoxLayout()
    
    # Sublayout to select table
    layout_table = QHBoxLayout()
    table_title = QLabel("Table: ")
    self.table_dropdown = QComboBox()
    self.table_dropdown.addItems(get_tables(self.cur))
    # Allow selection of attributes only when table is selected
    self.table_dropdown.activated.connect(self.table_activated)

    self.all_attributes = []
    self.selected_attributes = []

    layout_table.addWidget(table_title)
    layout_table.addWidget(self.table_dropdown)

    # Sublayout to select attributes
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
    
    self.att_selected = QLabel("No attribtues selected.") # Display selected attributes

    layout_att.addWidget(att_title)
    layout_att.addWidget(self.att_dropdown)
    layout_att.addWidget(self.att_add)
    layout_att.addWidget(self.att_remove)
    layout_att.addWidget(self.att_clear)
    layout_att.addWidget(self.att_addAll)


    # Where clause functionality
    self.conditions_box = ConditionsBox()
    
    # Sublayout for order by clause
    layout_order = QHBoxLayout()
    layout_order.addWidget(QLabel("Sorted by: "))
    self.order_dropdown = QComboBox()
    self.order_dropdown.setDisabled(True)

    layout_order.addWidget(self.order_dropdown)

    # Run the final query
    self.btn_query = QPushButton("Run Query")
    self.btn_query.clicked.connect(self.run_query)
    self.btn_query.setDisabled(True)

    layout.addLayout(layout_table)
    layout.addLayout(layout_att)
    layout.addWidget(self.att_selected)
    layout.addWidget(self.conditions_box)
    layout.addLayout(layout_order)
    layout.addWidget(self.btn_query)

    self.setLayout(layout)

  def table_activated(self):
    # Allow selection of attributes only when table is selected
    self.btn_query.setDisabled(False)
    self.selected_attributes.clear()
    self.att_dropdown.setDisabled(False)
    self.att_dropdown.clear()

    table = self.table_dropdown.currentText()
    
    self.all_attributes = list(get_table_attributes(self.cur, table))
    
    self.conditions_box.attributes = self.all_attributes.copy()
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
    
    # Get data for query
    table = self.table_dropdown.currentText()
    attributes = self.selected_attributes
    conditions = self.conditions_box.conditions
    order_by = self.order_dropdown.currentText()
    if order_by in ['', 'None']:
      order_by = None

    if attributes:
      show_table = Table(self.cur, table, attributes, conditions, order_by)
      show_table.exec()
    else:
      error_dialog = MessageDialog("Please make sure the table and at least 1 attribute is selected.")
      error_dialog.exec()


class UpdateQueries(QWidget):
  '''Update query to update tables'''
  def __init__(self, con):
    super().__init__()
    self.cur = con.cursor()

    # Layout is very similar to select queries layout, with similar utility functions
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

    self.conditions_box = ConditionsBox()

    self.btn_query = QPushButton("Run Query")
    self.btn_query.clicked.connect(lambda: self.run_query())
    self.btn_query.setDisabled(True)

    layout.addLayout(layout_table)
    layout.addLayout(layout_att)
    layout.addWidget(self.conditions_box)
    layout.addWidget(self.btn_query)
    self.setLayout(layout)


  def table_activated(self):
    self.btn_query.setDisabled(False)
    self.att_dropdown.setDisabled(False)
    self.att_dropdown.clear()

    table = self.table_dropdown.currentText()
    self.all_attributes = list(get_table_attributes(self.cur, table))
    self.conditions_box.attributes = self.all_attributes.copy()
    self.att_dropdown.addItems(self.all_attributes)
    
  def run_query(self):
    table = self.table_dropdown.currentText()
    attribute = self.att_dropdown.currentText()
    value = self.update_value.text()
    conditions = self.conditions_box.conditions.copy()
    update_data(self.cur, table, attribute, value, conditions)
    
  def close(self):
    self.con.close()
    super().close()

    
class GroupBy(QWidget):
  '''Group by queries for aggregate functions'''
  def __init__(self, con):
    super().__init__()
    self.cur = con.cursor()

    # Layout is very similar to select queries layout, with similar utility functions
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


    # Where functionality
    self.conditions_box = ConditionsBox()
    
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
    layout.addWidget(self.conditions_box)
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
    self.conditions_box.attributes = self.all_attributes.copy()
    self.att_dropdown.addItems(self.all_attributes)

    self.group_dropdown.setDisabled(False)
    self.group_dropdown.clear()

    self.all_attributes = list(get_table_attributes(self.cur, table))
    self.group_dropdown.addItems(self.all_attributes)

    
  def run_query(self):
    table = self.table_dropdown.currentText()
    attribute = self.att_dropdown.currentText()
    func = self.agg_function.currentText()
    conditions = self.conditions_box.conditions
    group_by = self.group_dropdown.currentText()
    
    table = Table(self.cur, table, group_by=True, func=func, attribute=attribute, conditions=conditions, group_by_attr=group_by)
    table.exec()
    
    
class DeleteData(QWidget):
  '''Delete data from tables'''
  def __init__(self, con):
    super().__init__()
    self.con = con
    self.cur = con.cursor()

    # Layout is very similar to select queries layout, with similar utility functions
    layout = QVBoxLayout()
    layout_table = QHBoxLayout()
    table_title = QLabel("Table: ")
    self.table_dropdown = QComboBox()
    self.table_dropdown.addItems(get_tables(self.cur))
    self.table_dropdown.activated.connect(self.table_activated)

    layout_table.addWidget(table_title)
    layout_table.addWidget(self.table_dropdown)
    
    self.conditions_box = ConditionsBox()

    # TODO: Disable button when no text in table
    self.btn_delete = QPushButton("Delete Rows")
    self.btn_delete.clicked.connect(lambda: self.run_delete())
    self.btn_delete.setDisabled(True)

    layout.addLayout(layout_table)
    layout.addWidget(self.conditions_box)
    layout.addWidget(self.btn_delete)

    self.setLayout(layout)


  def table_activated(self):
    self.btn_delete.setDisabled(False)
    table = self.table_dropdown.currentText()
    self.conditions_box.attributes = list(get_table_attributes(self.cur, table))

  def run_delete(self):
    table = self.table_dropdown.currentText()
    conditions = self.conditions_box.conditions
    delete_rows(self.con, table, conditions)
    

class NaturalJoin(QWidget):
  '''Join 2 tables'''
  def __init__(self, con):
    super().__init__()
    self.cur = con.cursor()

    layout = QVBoxLayout()
    sublayout = QHBoxLayout()
    
    tables = list(get_tables(self.cur))
    
    # Sublayouts to select the 2 tables to join
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
      dialog = MessageDialog("Please select different tables")
      dialog.exec()
      return
    
    show_table = Table(self.cur, table_1, other_table=table_2, join=True)
    show_table.exec()
    

    