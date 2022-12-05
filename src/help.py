from PyQt6.QtWidgets import *
import os
from constants import *

path = os.path.join(os.environ['USERPROFILE'], 'Desktop', 'ViSQL_log.txt')

help_msg = f'''
ViSQL User Guide

1. Accessing a database
    + The title of the ViSQL window indicates whether a databse has been selected or not, and if so, which database has been selected.
    + If the message reads (NO DATABASE SELECTED), please proceed as indicated below.
        - In the Database Functions dropdown, click Select Database. A dropdown of available databses will appear.
    + To create a databse, click Create Database in the same dropdown.

2. History of all queries performed
    + A log of all queries performed can be found at {path}

3. Note on inputting data (conditions/select/update/aggregate/insert functions)
    + For varchar and datetime data types, the user must enter the values surrounded by quotes.
    + This applies to anywhere table data is being inputted or referenced.
    + Example: For conditions of relational type, a comparison of a varchar attribute must be done as shown:
        - <attribute> | <operator> | "string"
        - name = "monty python"

4. Use the menu options to direct you to the pages to create a new table, describe a table, insert data, query the table, delete tables and so on. Rest is as directed by the forms to run queries.

MySQL metadata
    + host: {host}
    + user: {user}

'''

class Help(QDialog):
  def __init__(self):
    super().__init__()
    layout = QVBoxLayout()
    layout.addWidget(QLabel(help_msg))
    self.setLayout(layout)
    