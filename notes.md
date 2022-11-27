1. When you switch between databases, need to remove the widget with the current database and replace it with the widget for the new database.

2. Things left to do: 

  - displays left - 
    - group by
    - describe table
    - natural join
    - constraints
    - extract table name box (do we need to?)
    - help page

  - Change titles of all opened dialogs

  Ant: 
  - Resizing - fields to match text length
    - Partially accomplished

  - Styling (if time permits)
  - Clean code for queries with decorator (if time permits)
  - Help page to explain basic things like regex and all. (if time permits. Static page)

3. Bugs - 
  - Constantly creating new pages instead of popping off the old widget
  - ManageTables - transitioning between layouts - new cursors are created. Do the old ones have to be closed or anything?
  - If MySQL return an empty table, Table widget throws an error

4. Ideas
  - Input data type whenever you have to update something or add things to a list