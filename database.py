'''import sqlite3
import pandas as pd

# Database connection setup
def get_db_connection(database="Main.db"):
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
        session_id INTEGER
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

def register_new_user(session_data, user):
    """
    Registers a new user by inserting their data into the USER_DATABASE and creating user-specific tables.
    """
    from app import create_session
    
    # Ensure user_id is present and valid (accessing it as an attribute of the User object)
    user_id = user.id  # Use dot notation to access the 'id' attribute of the user object
    if not user_id:
        print("Error: User ID is missing.")
        return None
    
    session_id = session_data.get("session_id")  # Accessing session_id from the session data
    if not session_id:
        print("Error: No session ID found.")
        return None

    db = get_db_connection()
    cursor = db.cursor()
    
    insert_user_query = "INSERT INTO USER_DATABASE (user_id, session_id) VALUES (?, ?)"
    
    try:
        # Start a transaction
        db.begin()

        # Insert user into USER_DATABASE
        cursor.execute(insert_user_query, (user_id, session_id))
        
        # Create user-specific tables (optional, depending on your app)
        create_user_specific_tables(cursor, user_id, session_id)
        
        # Commit the transaction
        db.commit()
        
        print(f"New user registered with user_id: {user_id} and session_id: {session_id}")
        return user_id

    except Exception as e:
        # If an error occurs, rollback the transaction
        db.rollback()
        print(f"Error registering new user: {e}")
        return None
    finally:
        cursor.close()
        db.close()


def create_user_specific_tables(cursor, user_id, session_id):
    """
    Creates user-specific conversation and health data tables.
    """
    # Ensure user_id is an integer
    if not isinstance(user_id, int):
        print("Error: user_id must be an integer.")
        return

    # Ensure valid table name by sanitizing user_id
    table_name_conversations = f"Table_{user_id}_conversations"
    table_name_health_data = f"Table_{user_id}_health_data"

    # Avoid SQL injection risks with dynamic table names
    if not table_name_conversations.isidentifier() or not table_name_health_data.isidentifier():
        print(f"Error: Invalid table name with user_id {user_id}.")
        return

    conversation_table_query = f"""
    CREATE TABLE IF NOT EXISTS {table_name_conversations} (
        session_id TEXT PRIMARY KEY,
        conversation_summary TEXT
    )
    """
    health_data_table_query = f"""
    CREATE TABLE IF NOT EXISTS {table_name_health_data} (
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
        INSERT INTO {table_name_conversations} (session_id, conversation_summary)
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
'''