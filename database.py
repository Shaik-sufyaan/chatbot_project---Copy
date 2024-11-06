import pymysql
from app import create_session

# Database connection setup
mydb = pymysql.connect(
    host="localhost",
    user="root",
    password="Shaik1517@",
    database="maindb"
)
mycursor = mydb.cursor()

# Function to create the USER_DATABASE table for storing all new users with only user number
def create_user_database_table():
    create_table_query = """
    CREATE TABLE IF NOT EXISTS USER_DATABASE (
        user_number INT AUTO_INCREMENT PRIMARY KEY
    )
    """
    try:
        mycursor.execute(create_table_query)
        mydb.commit()
        print("USER_DATABASE table created successfully.")
    except Exception as e:
        print(f"Error creating USER_DATABASE table: {e}")

# Function to register a new user and create user-specific tables
def register_new_user(session_id, user):
    # Register the user and create the session
    session_data = create_session(user)  # Make sure `create_session` is returning session data
    new_user_number = session_data["USER_ID"]  # Use the session data for user identification
    
    # Insert a new user entry into USER_DATABASE (adjust this query to match your actual user data fields)
    insert_user_query = "INSERT INTO USER_DATABASE (user_number) VALUES (%s)"
    try:
        # Assuming user_number is the only field in the USER_DATABASE table
        mycursor.execute(insert_user_query, (new_user_number,))
        mydb.commit()
        
        # Get the newly created user number
        user_number = mycursor.lastrowid
        print(f"New user registered with user_number: {user_number}")
        
        # Create the user-specific tables with session_id
        create_user_specific_tables(user_number, session_id)
        
        return user_number
    except Exception as e:
        print(f"Error registering new user: {e}")
        return None


# Function to create two tables for a specific user
def create_user_specific_tables(user_number, session_id):
    # Table 1 for conversation tracking (e.g., Table_4_1 for user_number 4)
    conversation_table_query = f"""
    CREATE TABLE IF NOT EXISTS `Table_{user_number}_1` (
        session_id VARCHAR(255) NOT NULL,
        conversation_summary TEXT
    )
    """
    
    # Insert the session_id into the conversation tracking table
    insert_session_query = f"""
    INSERT INTO `Table_{user_number}_1` (session_id, conversation_summary) 
    VALUES ('{session_id}', '')
    """
    
    # Table 2 for health data (e.g., Table_4_2 for user_number 4)
    health_data_table_query = f"""
    CREATE TABLE IF NOT EXISTS `Table_{user_number}_2` (
        Health_parameters TEXT,
        Social_parameters TEXT,
        Environmental_Parameters TEXT
    )
    """
    
    try:
        mycursor.execute(conversation_table_query)
        mycursor.execute(health_data_table_query)
        mycursor.execute(insert_session_query)  # Insert session_id for initial entry
        mydb.commit()
        print(f"Tables for user {user_number} created successfully.")
    except Exception as e:
        print(f"Error creating tables for user {user_number}: {e}")

# Run the functions
create_user_database_table()  # Create main USER_DATABASE table

# Register a new user and create specific tables using the session_id from SESSION_ID dictionary
# Assuming SESSION_ID['current_session'] holds the relevant session_id
session_data = create_session(user)  # user needs to be defined or passed here
new_user_number = register_new_user(session_data['Session_ID'])