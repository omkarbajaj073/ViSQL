1. When you switch between databases, need to remove the widget with the current database and replace it with the widget for the new database.

2. Things left to do: 

  - displays left - 
    - group by
    - describe table
    - constraints
    - help page

  - extract table name box (do we need to?)
  - Change titles of all opened dialogs

  - Styling (if time permits)
  - Clean code for queries with decorator (if time permits)

3. Inefficiencies - 
  - Constantly creating new pages instead of popping off the old widget
  - ManageTables - transitioning between layouts - new cursors are created. Do the old ones have to be closed or anything?  
  - importing * everywhere