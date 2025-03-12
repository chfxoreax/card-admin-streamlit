import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import json
import requests
from supabase import create_client, Client
import time
import hashlib
import random
import string

# Load environment variables
load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("Missing Supabase configuration. Please check your .env file.")
    st.stop()

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Page configuration
st.set_page_config(
    page_title="Card Admin Panel",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
        color: #1E88E5;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
        color: #424242;
    }
    .card {
        background-color: #f9f9f9;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .metric-card {
        background-color: white;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        text-align: center;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #1E88E5;
    }
    .metric-label {
        font-size: 1rem;
        color: #616161;
    }
    .stButton button {
        background-color: #1E88E5;
        color: white;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    .stButton button:hover {
        background-color: #1565C0;
    }
    .warning {
        color: #FF5722;
        font-weight: bold;
    }
    .success {
        color: #4CAF50;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Authentication functions
def generate_random_key(length=16):
    """Generate a random key for new access keys"""
    chars = string.ascii_uppercase + string.digits
    # Generate 16 random characters
    random_chars = ''.join(random.choice(chars) for _ in range(16))
    # Format as XXXX-XXXX-XXXX-XXXX
    return f"{random_chars[0:4]}-{random_chars[4:8]}-{random_chars[8:12]}-{random_chars[12:16]}"

def hash_password(password):
    """Simple password hashing"""
    return hashlib.sha256(password.encode()).hexdigest()

def check_password(password, hashed_password):
    """Check if password matches hashed password"""
    return hash_password(password) == hashed_password

def login():
    """Handle user login"""
    st.markdown('<div class="main-header">Card Admin Panel</div>', unsafe_allow_html=True)
    
    # Debug section
    st.write("### Debug Info")
    st.write("If you're having trouble logging in, check the information below:")
    
    # Show admin password hash for verification
    admin_hash = hash_password("admin")
    st.code(f"Expected admin password hash: {admin_hash}")
    
    # Check if users table exists and has data
    try:
        response = supabase.table("users").select("*").execute()
        st.write(f"Found {len(response.data)} users in database")
        
        # Show user data (excluding sensitive info)
        if response.data:
            user_data = []
            for user in response.data:
                # Check which password field exists
                password_field = None
                password_length = 0
                for field in ["password", "password_hash", "hashed_password"]:
                    if field in user and user[field]:
                        password_field = field
                        password_length = len(user[field]) if user[field] else 0
                        break
                
                user_data.append({
                    "id": user.get("id"),
                    "username": user.get("username"),
                    "is_admin": user.get("is_admin"),
                    "password_field": password_field,
                    "password_length": password_length
                })
            st.write("Users in database:", user_data)
            
            # Add a button to fix admin password
            if st.button("Fix Admin Password"):
                try:
                    # Find admin user
                    admin_user = None
                    for user in response.data:
                        if user.get("username") == "admin":
                            admin_user = user
                            break
                    
                    if admin_user:
                        # Update admin password
                        admin_id = admin_user.get("id")
                        admin_hash = hash_password("admin")
                        
                        # Try different field names
                        for field in ["password", "password_hash"]:
                            try:
                                update_data = {field: admin_hash}
                                supabase.table("users").update(update_data).eq("id", admin_id).execute()
                                st.success(f"Admin password updated successfully using field '{field}'.")
                                st.rerun()
                                break
                            except Exception as e:
                                st.error(f"Error updating {field}: {str(e)}")
                    else:
                        st.error("Admin user not found.")
                except Exception as e:
                    st.error(f"Error fixing admin password: {str(e)}")
    except Exception as e:
        st.error(f"Error checking users table: {str(e)}")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        
        if submit:
            if not username or not password:
                st.error("Please enter both username and password")
                return False
                
            # Check credentials against Supabase
            response = supabase.table("users").select("*").eq("username", username).execute()
            
            if not response.data:
                st.error("Invalid username or password")
                return False
                
            user = response.data[0]
            
            # Debug password check
            entered_hash = hash_password(password)
            
            # Try different password field names
            stored_hash = None
            password_field_used = None
            for field in ["password", "password_hash", "hashed_password"]:
                if field in user and user[field]:
                    stored_hash = user[field]
                    password_field_used = field
                    break
            
            if not stored_hash:
                stored_hash = ""
                password_field_used = "none found"
            
            st.write("Debug password check:")
            st.write(f"Entered password hash: {entered_hash}")
            st.write(f"Stored password hash (from {password_field_used}): {stored_hash}")
            st.write(f"Match: {entered_hash == stored_hash}")
            
            # Check password
            if entered_hash == stored_hash:
                st.session_state["authenticated"] = True
                st.session_state["user"] = user
                st.session_state["is_admin"] = user.get("is_admin", False)
                return True
            else:
                st.error("Invalid username or password")
                return False
    
    # Add a button to create admin user if none exists
    if st.button("Initialize Admin User"):
        try:
            # Check if admin user exists
            response = supabase.table("users").select("*").eq("username", "admin").execute()
            
            if not response.data:
                # Create admin user
                admin_user = {
                    "username": "admin",
                    "password": hash_password("admin"),  # Try with 'password' field
                    "is_admin": True,
                    "created_at": datetime.now().isoformat()
                }
                
                supabase.table("users").insert(admin_user).execute()
                st.success("Admin user created successfully. You can now login with username 'admin' and password 'admin'.")
            else:
                st.info("Admin user already exists.")
        except Exception as e:
            st.error(f"Error creating admin user: {str(e)}")
    
    return False

# Initialize session state
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if "current_page" not in st.session_state:
    st.session_state["current_page"] = "dashboard"

# Main app
if not st.session_state["authenticated"]:
    login()
else:
    # Sidebar navigation
    with st.sidebar:
        st.image("https://via.placeholder.com/150x80?text=Card+Admin", width=150)
        st.markdown(f"Welcome, **{st.session_state['user'].get('username', 'User')}**")
        
        st.markdown("### Navigation")
        
        if st.button("Dashboard", key="nav_dashboard"):
            st.session_state["current_page"] = "dashboard"
            
        if st.button("Keys Management", key="nav_keys"):
            st.session_state["current_page"] = "keys"
            
        if st.button("Live Cards", key="nav_live_cards"):
            st.session_state["current_page"] = "live_cards"
            
        if st.session_state.get("is_admin", False):
            if st.button("User Management", key="nav_users"):
                st.session_state["current_page"] = "users"
        
        if st.button("Logout", key="nav_logout"):
            st.session_state["authenticated"] = False
            st.session_state["user"] = None
            st.session_state["is_admin"] = False
            st.rerun()
    
    # Content based on selected page
    if st.session_state["current_page"] == "dashboard":
        st.markdown('<div class="main-header">Dashboard</div>', unsafe_allow_html=True)
        
        # Get dashboard stats
        try:
            # Get total keys
            keys_response = supabase.table("access_keys").select("*").execute()
            total_keys = len(keys_response.data)
            
            # Get active keys
            active_keys = sum(1 for key in keys_response.data if key.get("is_active", False))
            
            # Get total live cards
            live_cards_response = supabase.table("live_cards").select("*").execute()
            total_live_cards = len(live_cards_response.data)
            
            # Get total users
            users_response = supabase.table("users").select("*").execute()
            total_users = len(users_response.data)
            
            # Get total credits and used credits
            total_credits = sum(key.get("credits", 0) for key in keys_response.data)
            total_used_credits = sum(key.get("used_credits", 0) for key in keys_response.data)
            
            # Display metrics in a grid
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{total_keys}</div>
                    <div class="metric-label">Total Keys</div>
                </div>
                """, unsafe_allow_html=True)
                
            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{active_keys}</div>
                    <div class="metric-label">Active Keys</div>
                </div>
                """, unsafe_allow_html=True)
                
            with col3:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{total_live_cards}</div>
                    <div class="metric-label">Live Cards</div>
                </div>
                """, unsafe_allow_html=True)
                
            col4, col5, col6 = st.columns(3)
            
            with col4:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{total_users}</div>
                    <div class="metric-label">Users</div>
                </div>
                """, unsafe_allow_html=True)
                
            with col5:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{total_credits}</div>
                    <div class="metric-label">Total Credits</div>
                </div>
                """, unsafe_allow_html=True)
                
            with col6:
                usage_percentage = (total_used_credits / total_credits * 100) if total_credits > 0 else 0
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{usage_percentage:.1f}%</div>
                    <div class="metric-label">Credit Usage</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Charts section
            st.markdown('<div class="sub-header">Analytics</div>', unsafe_allow_html=True)
            
            chart_col1, chart_col2 = st.columns(2)
            
            with chart_col1:
                # Create sample data for demonstration
                # In a real app, you'd get this from your database
                dates = [(datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]
                dates.reverse()
                
                verifications = [random.randint(50, 200) for _ in range(7)]
                
                # Create DataFrame
                df_verifications = pd.DataFrame({
                    "Date": dates,
                    "Verifications": verifications
                })
                
                # Create chart
                fig = px.line(
                    df_verifications, 
                    x="Date", 
                    y="Verifications",
                    title="Card Verifications (Last 7 Days)",
                    markers=True
                )
                
                fig.update_layout(
                    height=400,
                    margin=dict(l=20, r=20, t=40, b=20),
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            with chart_col2:
                # Create sample data for demonstration
                card_types = ["VISA", "MASTERCARD", "AMEX", "DISCOVER", "OTHER"]
                card_counts = [random.randint(20, 100) for _ in range(5)]
                
                # Create DataFrame
                df_cards = pd.DataFrame({
                    "Card Type": card_types,
                    "Count": card_counts
                })
                
                # Create chart
                fig = px.pie(
                    df_cards,
                    values="Count",
                    names="Card Type",
                    title="Card Distribution by Type",
                    hole=0.4
                )
                
                fig.update_layout(
                    height=400,
                    margin=dict(l=20, r=20, t=40, b=20),
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            # Recent activity
            st.markdown('<div class="sub-header">Recent Activity</div>', unsafe_allow_html=True)
            
            # Get recent logs
            logs_response = supabase.table("usage_logs").select("*").order("timestamp", desc=True).limit(10).execute()
            
            if logs_response.data:
                logs_df = pd.DataFrame(logs_response.data)
                logs_df["timestamp"] = pd.to_datetime(logs_df["timestamp"])
                logs_df["timestamp"] = logs_df["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")
                
                st.dataframe(
                    logs_df[["timestamp", "action", "details"]],
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("No recent activity found")
                
        except Exception as e:
            st.error(f"Error loading dashboard data: {str(e)}")
    
    elif st.session_state["current_page"] == "keys":
        st.markdown('<div class="main-header">Keys Management</div>', unsafe_allow_html=True)
        
        # Add refresh button
        if st.button("🔄 Refresh Data", key="refresh_keys"):
            st.rerun()
        
        # Create tabs for different key operations
        tab1, tab2, tab3, tab4 = st.tabs(["All Keys", "Create Key", "Manage Credits", "Delete Key"])
        
        with tab1:
            st.markdown('<div class="sub-header">All Keys</div>', unsafe_allow_html=True)
            
            # Get all keys
            try:
                keys_response = supabase.table("access_keys").select("*").execute()
                
                if keys_response.data:
                    keys_df = pd.DataFrame(keys_response.data)
                    keys_df["created_at"] = pd.to_datetime(keys_df["created_at"])
                    keys_df["created_at"] = keys_df["created_at"].dt.strftime("%Y-%m-%d %H:%M:%S")
                    
                    # Add status column
                    keys_df["status"] = keys_df["is_active"].apply(lambda x: "Active" if x else "Inactive")
                    
                    # Display keys table
                    st.dataframe(
                        keys_df[["id", "key_value", "credits", "used_credits", "status", "created_at"]],
                        use_container_width=True,
                        hide_index=True
                    )
                else:
                    st.info("No keys found")
            except Exception as e:
                st.error(f"Error loading keys: {str(e)}")
        
        with tab2:
            st.markdown('<div class="sub-header">Create New Key</div>', unsafe_allow_html=True)
            
            with st.form("create_key_form"):
                # Key type selection
                key_type = st.radio("Key Type", ["Generate Random Key", "Enter Custom Key"])
                
                # Generate a random key in format XXXX-XXXX-XXXX-XXXX
                suggested_key = generate_random_key()
                
                # Key value input
                if key_type == "Generate Random Key":
                    key_value = st.text_input("Key Value", value=suggested_key, disabled=True)
                    st.info("A random key has been generated in the format XXXX-XXXX-XXXX-XXXX")
                else:
                    key_value = st.text_input("Key Value", placeholder="e.g., ABCD-1234-EFGH-5678")
                    st.info("Enter a custom key. Recommended format: XXXX-XXXX-XXXX-XXXX")
                
                # Credits input
                credits = st.number_input("Credits", min_value=0, value=100)
                
                # Expiry date (optional)
                include_expiry = st.checkbox("Set Expiry Date")
                expiry_date = None
                if include_expiry:
                    expiry_date = st.date_input("Expiry Date", value=datetime.now() + timedelta(days=30))
                
                submit = st.form_submit_button("Create Key")
                
                if submit:
                    if not key_value:
                        st.error("Please enter a key value")
                    else:
                        try:
                            # Check if key already exists
                            existing_key = supabase.table("access_keys").select("*").eq("key_value", key_value).execute()
                            
                            if existing_key.data:
                                st.error("Key already exists")
                            else:
                                # Create key
                                new_key = {
                                    "key_value": key_value,
                                    "credits": credits,
                                    "used_credits": 0,
                                    "is_active": True,
                                    "created_by": st.session_state["user"].get("id"),
                                    "created_at": datetime.now().isoformat(),
                                    "webhook_enabled": False
                                }
                                
                                # Add expiry date if set
                                if include_expiry and expiry_date:
                                    new_key["expires_at"] = datetime.combine(expiry_date, datetime.min.time()).isoformat()
                                
                                response = supabase.table("access_keys").insert(new_key).execute()
                                
                                # Log the action
                                log_entry = {
                                    "key_id": response.data[0]["id"],
                                    "action": "create_key",
                                    "details": f"Created key with {credits} credits",
                                    "timestamp": datetime.now().isoformat()
                                }
                                supabase.table("usage_logs").insert(log_entry).execute()
                                
                                st.success("Key created successfully")
                                
                                # Show the created key for easy copying
                                st.code(key_value)
                        except Exception as e:
                            st.error(f"Error creating key: {str(e)}")
        
        with tab3:
            st.markdown('<div class="sub-header">Manage Credits</div>', unsafe_allow_html=True)
            
            # Get all keys for selection
            try:
                keys_response = supabase.table("access_keys").select("*").execute()
                
                if keys_response.data:
                    # Create a dictionary of key_id: key_value for selection
                    key_options = {str(key["id"]): f"{key['key_value']} ({key['credits']} credits)" for key in keys_response.data}
                    
                    with st.form("manage_credits_form"):
                        selected_key_id = st.selectbox("Select Key", options=list(key_options.keys()), format_func=lambda x: key_options[x])
                        operation = st.radio("Operation", ["ADD", "DEDUCT"])
                        amount = st.number_input("Amount", min_value=1, value=10)
                        
                        submit = st.form_submit_button("Update Credits")
                        
                        if submit:
                            try:
                                # Get current key
                                key_id = int(selected_key_id)
                                key_response = supabase.table("access_keys").select("*").eq("id", key_id).execute()
                                
                                if not key_response.data:
                                    st.error("Key not found")
                                else:
                                    key = key_response.data[0]
                                    
                                    # Update credits
                                    if operation == "ADD":
                                        new_credits = key["credits"] + amount
                                        supabase.table("access_keys").update({"credits": new_credits}).eq("id", key_id).execute()
                                        action = "add_credits"
                                        details = f"Added {amount} credits"
                                    else:  # DEDUCT
                                        if key["credits"] < amount:
                                            st.error("Insufficient credits")
                                            st.stop()
                                            
                                        new_credits = key["credits"] - amount
                                        new_used_credits = key["used_credits"] + amount
                                        supabase.table("access_keys").update({
                                            "credits": new_credits,
                                            "used_credits": new_used_credits
                                        }).eq("id", key_id).execute()
                                        action = "deduct_credits"
                                        details = f"Deducted {amount} credits"
                                    
                                    # Log the action
                                    log_entry = {
                                        "key_id": key_id,
                                        "action": action,
                                        "details": details,
                                        "timestamp": datetime.now().isoformat()
                                    }
                                    supabase.table("usage_logs").insert(log_entry).execute()
                                    
                                    st.success(f"Credits {operation.lower()}ed successfully")
                            except Exception as e:
                                st.error(f"Error updating credits: {str(e)}")
                else:
                    st.info("No keys found")
            except Exception as e:
                st.error(f"Error loading keys: {str(e)}")
        
        with tab4:
            st.markdown('<div class="sub-header">Delete Key</div>', unsafe_allow_html=True)
            
            # Get all keys for selection
            try:
                keys_response = supabase.table("access_keys").select("*").execute()
                
                if keys_response.data:
                    # Create a dictionary of key_id: key_value for selection
                    key_options = {str(key["id"]): f"{key['key_value']} ({key['credits']} credits)" for key in keys_response.data}
                    
                    with st.form("delete_key_form"):
                        selected_key_id = st.selectbox("Select Key to Delete", options=list(key_options.keys()), format_func=lambda x: key_options[x])
                        
                        # Confirmation checkbox
                        confirm_delete = st.checkbox("I understand this action cannot be undone")
                        
                        submit = st.form_submit_button("Delete Key")
                        
                        if submit:
                            if not confirm_delete:
                                st.error("Please confirm the deletion")
                            else:
                                try:
                                    # Get current key
                                    key_id = int(selected_key_id)
                                    key_response = supabase.table("access_keys").select("*").eq("id", key_id).execute()
                                    
                                    if not key_response.data:
                                        st.error("Key not found")
                                    else:
                                        key = key_response.data[0]
                                        key_value = key["key_value"]
                                        
                                        # Delete key
                                        supabase.table("access_keys").delete().eq("id", key_id).execute()
                                        
                                        # Log the action
                                        log_entry = {
                                            "key_id": key_id,
                                            "action": "delete_key",
                                            "details": f"Deleted key {key_value}",
                                            "timestamp": datetime.now().isoformat()
                                        }
                                        supabase.table("usage_logs").insert(log_entry).execute()
                                        
                                        st.success(f"Key {key_value} deleted successfully")
                                except Exception as e:
                                    st.error(f"Error deleting key: {str(e)}")
                else:
                    st.info("No keys found")
            except Exception as e:
                st.error(f"Error loading keys: {str(e)}")
    
    elif st.session_state["current_page"] == "live_cards":
        st.markdown('<div class="main-header">Live Cards</div>', unsafe_allow_html=True)
        
        # Add refresh button
        if st.button("Refresh Data"):
            st.rerun()
        
        # Get live cards
        try:
            live_cards_response = supabase.table("live_cards").select("*").order("created_at", desc=True).execute()
            
            if live_cards_response.data:
                live_cards_df = pd.DataFrame(live_cards_response.data)
                
                # Format dates
                if "created_at" in live_cards_df.columns:
                    live_cards_df["created_at"] = pd.to_datetime(live_cards_df["created_at"])
                    live_cards_df["created_at"] = live_cards_df["created_at"].dt.strftime("%Y-%m-%d %H:%M:%S")
                
                # Display live cards table
                st.dataframe(
                    live_cards_df,
                    use_container_width=True,
                    hide_index=True
                )
                
                # Add export functionality
                if st.button("Export to CSV"):
                    csv = live_cards_df.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name=f"live_cards_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
            else:
                st.info("No live cards found")
        except Exception as e:
            st.error(f"Error loading live cards: {str(e)}")
    
    elif st.session_state["current_page"] == "users" and st.session_state.get("is_admin", False):
        st.markdown('<div class="main-header">User Management</div>', unsafe_allow_html=True)
        
        # Create tabs for different user operations
        tab1, tab2 = st.tabs(["All Users", "Create User"])
        
        with tab1:
            st.markdown('<div class="sub-header">All Users</div>', unsafe_allow_html=True)
            
            # Get all users
            try:
                users_response = supabase.table("users").select("*").execute()
                
                if users_response.data:
                    users_df = pd.DataFrame(users_response.data)
                    
                    # Format dates
                    if "created_at" in users_df.columns:
                        users_df["created_at"] = pd.to_datetime(users_df["created_at"])
                        users_df["created_at"] = users_df["created_at"].dt.strftime("%Y-%m-%d %H:%M:%S")
                    
                    if "last_login" in users_df.columns:
                        users_df["last_login"] = pd.to_datetime(users_df["last_login"])
                        users_df["last_login"] = users_df["last_login"].dt.strftime("%Y-%m-%d %H:%M:%S")
                    
                    # Add role column
                    users_df["role"] = users_df["is_admin"].apply(lambda x: "Admin" if x else "User")
                    
                    # Display users table (exclude password hash)
                    columns_to_display = [col for col in users_df.columns if col != "password_hash" and col != "password"]
                    st.dataframe(
                        users_df[columns_to_display],
                        use_container_width=True,
                        hide_index=True
                    )
                else:
                    st.info("No users found")
            except Exception as e:
                st.error(f"Error loading users: {str(e)}")
        
        with tab2:
            st.markdown('<div class="sub-header">Create New User</div>', unsafe_allow_html=True)
            
            with st.form("create_user_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                is_admin = st.checkbox("Admin User")
                
                submit = st.form_submit_button("Create User")
                
                if submit:
                    if not username or not password:
                        st.error("Please enter both username and password")
                    else:
                        try:
                            # Check if username already exists
                            existing_user = supabase.table("users").select("*").eq("username", username).execute()
                            
                            if existing_user.data:
                                st.error("Username already exists")
                            else:
                                # Create user
                                new_user = {
                                    "username": username,
                                    "password_hash": hash_password(password),
                                    "is_admin": is_admin,
                                    "created_at": datetime.now().isoformat()
                                }
                                
                                supabase.table("users").insert(new_user).execute()
                                st.success("User created successfully")
                        except Exception as e:
                            st.error(f"Error creating user: {str(e)}") 