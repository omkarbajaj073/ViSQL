from PyQt6.QtWidgets import *

# from utils import create_database
# from styles import styles
import mysql.connector
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

  # def closeEvent(self, event):
  #   print('Dialog closed')

  def create_db(self):
    name = self.edit.text()
    # TODO: Check that the name is valid
    # TODO: Specific error for database already exists
    if name.isidentifier():
      try:
        create_database(name)
        self.edit.hide()
        self.push.hide()
        self.error.hide()
        self.label.setText("Database created. Close this dialogue and proceed.")
      except mysql.connector.errors.DatabaseError:
        self.error.setText("A database with that name already exists.")
    else:
      self.error.setText("Invalid database name!")



# class SelectDb(QWidget):
#   def __init__(self):
#     next = QPushButton("Use Database")
#     dropdown = QComboBox()
#     dropdown.addItems(get_databases())

#     mainlayout = QVBoxLayout()



  
