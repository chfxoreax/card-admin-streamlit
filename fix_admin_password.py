#!/usr/bin/env python3
import os
import hashlib
from dotenv import load_dotenv
from supabase import create_client, Client
import json

# Load environment variables
load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Error: Missing Supabase configuration. Please check your .env file.")
    exit(1)

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def hash_password(password):
    """Simple password hashing using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def fix_admin_password():
    """Fix the admin user's password hash"""
    print("Fixing admin user password...")
    
    # Get the admin user to check column names
    response = supabase.table("users").select("*").eq("username", "admin").execute()
    
    if not response.data:
        print("Admin user not found.")
        return
    
    # Print the user data to see column names
    print("User data structure:")
    user_data = response.data[0]
    for key in user_data:
        print(f"  - {key}: {type(user_data[key])}")
    
    # Check if password column exists
    password_column = None
    for column in ["password_hash", "password", "hashed_password", "passwordhash"]:
        if column in user_data:
            password_column = column
            print(f"Found password column: {password_column}")
            break
    
    if not password_column:
        print("Could not find password column. Available columns:")
        print(list(user_data.keys()))
        return
    
    # Update the admin user's password
    admin_id = user_data["id"]
    admin_hash = hash_password("admin")
    
    print(f"Updating admin user (ID: {admin_id}) password...")
    print(f"New hash: {admin_hash}")
    
    try:
        # Try to update the password
        update_data = {password_column: admin_hash}
        supabase.table("users").update(update_data).eq("id", admin_id).execute()
        print(f"Admin password updated successfully using column '{password_column}'.")
        
        # Verify the update
        response = supabase.table("users").select("*").eq("id", admin_id).execute()
        if response.data and response.data[0].get(password_column) == admin_hash:
            print("Verification successful. Admin password is now set correctly.")
        else:
            print("Warning: Verification failed. The password may not have been updated correctly.")
    except Exception as e:
        print(f"Error updating password: {e}")
        
        # Try alternative approach - create a new admin user
        print("Trying to create a new admin user...")
        try:
            # Delete existing admin user
            supabase.table("users").delete().eq("username", "admin").execute()
            
            # Create new admin user
            new_admin = {
                "username": "admin",
                password_column: admin_hash,
                "is_admin": True
            }
            supabase.table("users").insert(new_admin).execute()
            print("New admin user created successfully.")
        except Exception as e2:
            print(f"Error creating new admin user: {e2}")

if __name__ == "__main__":
    fix_admin_password() 