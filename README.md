# MySQL Query Wizard

## Instructions
1. Install dependencies - `pip install -r requirements.txt`
2. Clone this repository - `git clone https://github.com/omkarbajaj073/ViSQL.git`
3. For the *main* branch, define the variables `host`, `user` and `password` with the mysql server credentials. For the *kwargs_ver*, define a dictionary `kwargs` with the above as keys, and a port number if necessary. (See `constants.py` for examples)
4. Run the main script - `python main.py`
5. All queries run during a given session are stored in `%USERPROFILE%/Desktop/ViSQL_log.txt`

## Limitations 
1. No join supported except natural join (select queries)
2. Check constraint not supported (create table queries)
3. Foreign keys not supported (create table queries)
4. Cannot change user/host of MySQL server from within the application. Admin must update `constants.py` for this.
5. Alter queries not supported
(There may be others too ... )
