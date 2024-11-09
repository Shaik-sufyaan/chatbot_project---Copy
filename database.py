import sqlite3
import pandas as pd

# Database connection setup
def get_db_connection(database="users.db"):
    """
    Establishes a connection to the SQLite3 database.
    """
    return sqlite3.connect(database)

def create_user_database_table():
    """
    Creates the main USER_DATABASE table to store user-specific information.
    """
    create_table_query = """
    CREATE TABLE IF NOT EXISTS USER_DATABASE (
        user_id INTEGER PRIMARY KEY,
        session_id TEXT
    )
    """
    db = get_db_connection()
    cursor = db.cursor()
    try:
        cursor.execute(create_table_query)
        db.commit()
        print("USER_DATABASE table created successfully.")
    except Exception as e:
        print(f"Error creating USER_DATABASE table: {e}")
    finally:
        cursor.close()
        db.close()

def register_new_user(session_id, user):
    from app import create_session
    """
    Registers a new user by adding them to USER_DATABASE and creates user-specific tables.
    Arguments:
    - session_id: The session ID for the user.
    - user: The user object from the Flask SQLAlchemy model.
    """
    # Extract user ID from the SQLAlchemy user object
    user_id = user.id

    db = get_db_connection()
    cursor = db.cursor()
    insert_user_query = "INSERT INTO USER_DATABASE (user_id, session_id) VALUES (?, ?)"
    
    try:
        # Insert user into USER_DATABASE
        cursor.execute(insert_user_query, (user_id, session_id))
        db.commit()
        print(f"New user registered with user_id: {user_id}")

        # Create user-specific tables
        create_user_specific_tables(cursor, user_id, session_id)

        return user_id
    except Exception as e:
        print(f"Error registering new user: {e}")
        return None
    finally:
        cursor.close()
        db.close()

def create_user_specific_tables(cursor, user_id, session_id):
    """
    Creates user-specific conversation and health data tables.
    """
    conversation_table_query = f"""
    CREATE TABLE IF NOT EXISTS Table_{user_id}_conversations (
        session_id TEXT PRIMARY KEY,
        conversation_summary TEXT
    )
    """
    health_data_table_query = f"""
    CREATE TABLE IF NOT EXISTS Table_{user_id}_health_data (
        health_parameters TEXT,
        social_parameters TEXT,
        environmental_parameters TEXT
    )
    """
    try:
        cursor.execute(conversation_table_query)
        cursor.execute(health_data_table_query)

        # Insert initial session record
        insert_session_query = f"""
        INSERT INTO Table_{user_id}_conversations (session_id, conversation_summary)
        VALUES (?, '')
        """
        cursor.execute(insert_session_query, (session_id,))
        print(f"User-specific tables for user_id {user_id} created successfully.")
    except Exception as e:
        print(f"Error creating user-specific tables for user_id {user_id}: {e}")

def view_table_data(table_name):
    """
    Views the data of a specified table using Pandas.
    """
    db = get_db_connection()
    try:
        query = f"SELECT * FROM {table_name}"
        df = pd.read_sql_query(query, db)
        print(df)
    except Exception as e:
        print(f"Error fetching data from {table_name}: {e}")
    finally:
        db.close()
