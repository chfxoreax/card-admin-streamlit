# Card Admin Panel (Streamlit)

A modern admin panel for managing card verification keys, credits, and monitoring live cards, built with Streamlit and Supabase.

## Features

- Modern, responsive UI built with Streamlit
- Real-time data visualization with Plotly
- Secure authentication and authorization
- Key management (create, edit, delete)
- Credit management (add/deduct)
- User management
- Live cards monitoring
- Beautiful charts and statistics

## Screenshots

![Dashboard](https://via.placeholder.com/800x450?text=Dashboard+Screenshot)
![Keys Management](https://via.placeholder.com/800x450?text=Keys+Management+Screenshot)
![Live Cards](https://via.placeholder.com/800x450?text=Live+Cards+Screenshot)

## Setup Instructions

### Supabase Setup

1. Create a new project in Supabase (https://supabase.com)
2. Get your Supabase URL and anon key from the project settings
3. Run the `init_db.sql` script in the Supabase SQL editor to create the necessary tables
4. Enable Row Level Security (RLS) and configure appropriate policies

### Local Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file from the template:
   ```bash
   cp .env.example .env
   ```

5. Edit the `.env` file with your Supabase credentials

6. Initialize the database:
   ```bash
   python init_db.py
   ```

7. Run the Streamlit app:
   ```bash
   streamlit run app.py
   ```

8. Access the app at http://localhost:8501

## Default Login

- Username: admin
- Password: admin

**Important**: Change the default password after first login!

## Development

- The main application is in `app.py`
- Database schema is defined in `init_db.sql`
- Database initialization script is in `init_db.py`

## Deployment

### Deploy to Streamlit Cloud

1. Push your code to GitHub
2. Go to [Streamlit Cloud](https://streamlit.io/cloud)
3. Connect your GitHub repository
4. Set the main file path to `app.py`
5. Add your Supabase credentials as secrets

### Deploy to a VPS

1. Set up a server with Python installed
2. Clone the repository
3. Follow the local setup instructions
4. Use a process manager like Supervisor to keep the app running
5. Set up Nginx as a reverse proxy

## Security Considerations

- Use HTTPS in production
- Change the default admin password
- Use strong passwords and rotate secrets regularly
- Implement rate limiting
- Configure appropriate RLS policies in Supabase
- Monitor for suspicious activities 