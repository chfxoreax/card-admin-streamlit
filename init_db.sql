-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE
);

-- Access keys table
CREATE TABLE IF NOT EXISTS access_keys (
    id SERIAL PRIMARY KEY,
    key_value TEXT UNIQUE NOT NULL,
    credits INTEGER DEFAULT 0,
    used_credits INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,
    webhook_enabled BOOLEAN DEFAULT FALSE,
    webhook_url TEXT,
    webhook_secret TEXT
);

-- Live cards table
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

-- Usage logs table
CREATE TABLE IF NOT EXISTS usage_logs (
    id SERIAL PRIMARY KEY,
    key_id INTEGER REFERENCES access_keys(id),
    action TEXT NOT NULL,
    details TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create initial admin user (password: admin)
-- The password_hash is the SHA-256 hash of 'admin'
INSERT INTO users (username, password_hash, is_admin, created_at)
VALUES ('admin', '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918', TRUE, NOW())
ON CONFLICT (username) DO NOTHING; 