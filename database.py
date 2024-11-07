import pymysql

# Database connection setup
def get_db_connection(database="maindb"):
    return pymysql.connect(
        host="localhost",
        user="root",
        password="Shaik1517@",
        database=database
    )

def create_user_database_table():
    """
    Creates the main USER_DATABASE table in 'maindb' to store user-specific information.
    """
    create_table_query = """
    CREATE TABLE IF NOT EXISTS USER_DATABASE (
        user_id INT AUTO_INCREMENT PRIMARY KEY,
        session_id VARCHAR(255)
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
    from app import create_session  # Import here to avoid circular dependency
    """
    Registers a new user by adding them to USER_DATABASE and creates user-specific tables.
    """
    # Create the session and retrieve session data
    session_data = create_session(user)
    new_user_id = session_data["USER_ID"]

    db = get_db_connection()
    cursor = db.cursor()
    insert_user_query = "INSERT INTO USER_DATABASE (user_id, session_id) VALUES (%s, %s)"
    
    try:
        cursor.execute(insert_user_query, (new_user_id, session_id))
        db.commit()
        user_id = cursor.lastrowid
        print(f"New user registered with user_id: {user_id}")

        # Create user-specific tables for conversations and health data
        create_user_specific_tables(user_id, session_id)

        return user_id
    except Exception as e:
        print(f"Error registering new user: {e}")
        return None
    finally:
        cursor.close()
        db.close()

def create_user_specific_tables(user_id, session_id):
    """
    Creates user-specific conversation and health data tables and stores the initial session ID in the conversation table.
    """
    conversation_table_query = f"""
    CREATE TABLE IF NOT EXISTS `Table_{user_id}_conversations` (
        session_id VARCHAR(255) PRIMARY KEY,
        conversation_summary TEXT
    )
    """
    health_data_table_query = f"""
    CREATE TABLE IF NOT EXISTS `Table_{user_id}_health_data` (
        health_parameters TEXT,
        social_parameters TEXT,
        environmental_parameters TEXT
    )
    """
    
    db = get_db_connection()
    cursor = db.cursor()
    try:
        # Create the tables
        cursor.execute(conversation_table_query)
        cursor.execute(health_data_table_query)

        # Insert the initial session record in the conversation table
        insert_session_query = f"""
        INSERT INTO `Table_{user_id}_conversations` (session_id, conversation_summary)
        VALUES (%s, '')
        """
        cursor.execute(insert_session_query, (session_id,))
        db.commit()

        print(f"Tables for user {user_id} created successfully, and session_id saved in `Table_{user_id}_conversations`.")
    except Exception as e:
        print(f"Error creating tables for user {user_id}: {e}")
    finally:
        cursor.close()
        db.close()
