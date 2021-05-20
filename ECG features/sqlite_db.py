from pathlib import Path
import sqlite3
import pandas as pd
import os

def save_to_sqldb(path, name, df):
    """
    Function saves pd.DataFrame into sqlite db file
    
    path (str): path to the directory where file will be stored
    name (str): name of the file and table in the database
    df: pd.DataFrame
    
    """
    
    db_file = os.path.join(path, name + '.db')
    Path(db_file).touch() #create empty database file
    conn = sqlite3.connect(db_file) #connect to database
    df.to_sql(name, conn, if_exists='append', index = False) # write the data to a sqlite table
    print('Database sucessfully saved!')
    
def read_sqlite_db(path, name):
    db_file = os.path.join(path, name + '.db')
    conn = sqlite3.connect(db_file)
    df = pd.read_sql_query("SELECT * FROM " + name, conn)
    return df