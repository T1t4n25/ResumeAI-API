from Auth_DataBase.auth_database import AuthDatabase
if __name__ == "__main__":
    auth_db = AuthDatabase()
    
    # Test the connection
    try:
        # Check if API key exists
        is_valid = auth_db.check_api_key("5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8")
        print(f"API key valid: {is_valid}")
        
        # Get user by API key
        user = auth_db.get_user_by_api_key("5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8")
        if user:
            print(f"User found: {user.username}")
        else:
            print("No user found for this API key")
            
    except Exception as e:
        print(f"Database error: {e}")