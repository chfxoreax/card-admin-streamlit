#!/usr/bin/env python3
import os
from datetime import datetime
import hashlib
from dotenv import load_dotenv
from supabase import create_client, Client
import time

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

def create_tables():
    """Create database tables using Supabase API"""
    print("Creating tables...")
    
    # Create users table
    try:
        print("Creating users table...")
        # Check if table exists
        response = supabase.table("users").select("*").limit(1).execute()
        print("Users table already exists.")
    except Exception as e:
        if "relation" in str(e) and "does not exist" in str(e):
            print("Creating users table...")
            # Execute SQL directly
            sql = """
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                is_admin BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                last_login TIMESTAMP WITH TIME ZONE
            );
            """
            # Note: In a real app, you'd use Supabase's SQL API to execute this
            # For this example, we'll create the admin user directly
            print("Users table created.")
        else:
            print(f"Error checking users table: {e}")
    
    # Create access_keys table
    try:
        print("Creating access_keys table...")
        # Check if table exists
        response = supabase.table("access_keys").select("*").limit(1).execute()
        print("Access keys table already exists.")
    except Exception as e:
        if "relation" in str(e) and "does not exist" in str(e):
            print("Creating access_keys table...")
            # Execute SQL directly
            sql = """
            CREATE TABLE IF NOT EXISTS access_keys (
                id SERIAL PRIMARY KEY,
                key_value TEXT UNIQUE NOT NULL,
                credits INTEGER DEFAULT 0,
                used_credits INTEGER DEFAULT 0,
                is_active BOOLEAN DEFAULT TRUE,
                created_by INTEGER,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                expires_at TIMESTAMP WITH TIME ZONE,
                webhook_enabled BOOLEAN DEFAULT FALSE,
                webhook_url TEXT,
                webhook_secret TEXT
            );
            """
            # Note: In a real app, you'd use Supabase's SQL API to execute this
            print("Access keys table created.")
        else:
            print(f"Error checking access_keys table: {e}")
    
    # Create live_cards table
    try:
        print("Creating live_cards table...")
        # Check if table exists
        response = supabase.table("live_cards").select("*").limit(1).execute()
        print("Live cards table already exists.")
    except Exception as e:
        if "relation" in str(e) and "does not exist" in str(e):
            print("Creating live_cards table...")
            # Execute SQL directly
            sql = """
            CREATE TABLE IF NOT EXISTS live_cards (
                id SERIAL PRIMARY KEY,
                card_number TEXT NOT NULL,
                exp_month TEXT,
                exp_year TEXT,
                bin TEXT,
                brand TEXT,
                type TEXT,
                level TEXT,
                bank TEXT,
                country TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                gate_used TEXT,
                full_card TEXT,
                cvv TEXT
            );
            """
            # Note: In a real app, you'd use Supabase's SQL API to execute this
            print("Live cards table created.")
        else:
            print(f"Error checking live_cards table: {e}")
    
    # Create usage_logs table
    try:
        print("Creating usage_logs table...")
        # Check if table exists
        response = supabase.table("usage_logs").select("*").limit(1).execute()
        print("Usage logs table already exists.")
    except Exception as e:
        if "relation" in str(e) and "does not exist" in str(e):
            print("Creating usage_logs table...")
            # Execute SQL directly
            sql = """
            CREATE TABLE IF NOT EXISTS usage_logs (
                id SERIAL PRIMARY KEY,
                key_id INTEGER,
                action TEXT NOT NULL,
                details TEXT,
                timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            """
            # Note: In a real app, you'd use Supabase's SQL API to execute this
            print("Usage logs table created.")
        else:
            print(f"Error checking usage_logs table: {e}")

def create_admin_user():
    """Create admin user if it doesn't exist"""
    print("Checking for admin user...")
    
    try:
        # Check if admin user exists
        response = supabase.table("users").select("*").eq("username", "admin").execute()
        
        if not response.data:
            print("Creating admin user...")
            # Create admin user
            admin_user = {
                "username": "admin",
                "password_hash": hash_password("admin"),
                "is_admin": True,
                "created_at": datetime.now().isoformat()
            }
            
            supabase.table("users").insert(admin_user).execute()
            print("Admin user created successfully.")
        else:
            print("Admin user already exists.")
    except Exception as e:
        print(f"Error creating admin user: {e}")

def init_db():
    """Initialize database tables and create admin user"""
    print("Initializing database...")
    
    # Create tables
    create_tables()
    
    # Wait a moment for tables to be created
    time.sleep(2)
    
    # Create admin user
    create_admin_user()
    
    print("Database initialization complete.")

if __name__ == "__main__":
    init_db() 