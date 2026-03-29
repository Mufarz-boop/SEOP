import pymysql
from flask import g, current_app

def get_db():
    if 'db' not in g:
        g.db = pymysql.connect(
            host=current_app.config['MYSQL_HOST'],
            user=current_app.config['MYSQL_USER'],
            password=current_app.config['MYSQL_PASSWORD'],
            database=current_app.config['MYSQL_DB'],
            port=current_app.config['MYSQL_PORT'],
            cursorclass=pymysql.cursors.DictCursor
        )
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db(app):
    app.teardown_appcontext(close_db)

def execute_query(query, params=None, fetch_one=False, commit=False):
    db = get_db()
    cursor = db.cursor()
    
    try:
        cursor.execute(query, params or ())
        
        if commit:
            db.commit()
            return cursor.lastrowid
        
        if fetch_one:
            return cursor.fetchone()
        return cursor.fetchall()
    except Exception as e:
        if commit:
            db.rollback()
        raise e
    finally:
        cursor.close()
