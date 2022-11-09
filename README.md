# MySQL Query Wizard

### Requirements: 
1. PyQT6 - UI components
2. Pysql Connector (or something)
3. An email client


### Structure of project - 
1. UI defined in main.py
2. Email client used in email.py - connection created on demand. [Within this, add the boilerplate of connecting to the database myself]
3. utils - all functions to be called by the ui components

### Menus - 
- One for each type of language (DDL, DML, DQL, DCL, TCL)
- Choose the constraints of each field, and button to add fields, during table creation 
- Everything will be dropdown based, except the field values
- Email client - automatically adds boiler plate (button for this)