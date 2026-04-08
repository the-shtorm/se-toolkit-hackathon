-- Smart Notification Manager - Database Initialization Script (V1)
-- This script runs automatically when the PostgreSQL container first starts

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Priority enum type
CREATE TYPE notification_priority AS ENUM ('low', 'medium', 'high', 'critical');

-- Notification status enum type
CREATE TYPE notification_status AS ENUM ('pending', 'sent', 'delivered', 'read', 'failed');

-- Delivery status enum type
CREATE TYPE delivery_status AS ENUM ('pending', 'delivered', 'read', 'failed');

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Notifications table
CREATE TABLE IF NOT EXISTS notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    priority notification_priority DEFAULT 'medium',
    status notification_status DEFAULT 'pending',
    created_by UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    sent_at TIMESTAMP WITH TIME ZONE,
    read_at TIMESTAMP WITH TIME ZONE
);

-- Notification recipients table
CREATE TABLE IF NOT EXISTS notification_recipients (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    notification_id UUID NOT NULL REFERENCES notifications(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    delivery_status delivery_status DEFAULT 'pending',
    delivered_at TIMESTAMP WITH TIME ZONE,
    UNIQUE(notification_id, user_id)
);

-- Note: Most indexes are now created automatically by SQLAlchemy via index=True on columns.
-- This script is kept for reference. When using Alembic migrations, 
-- tables and indexes are managed via migrations, not this script.
-- The indexes below are created by SQLAlchemy models:
--   ix_users_id, ix_users_email, ix_users_username
--   ix_notifications_id, ix_notifications_created_by, ix_notifications_group_id
--   ix_notification_recipients_id, ix_notification_recipients_notification_id, ix_notification_recipients_user_id
--   ix_notification_groups_id, ix_group_members_id, ix_events_id
--
-- Create additional custom indexes for query performance (if not already via SQLAlchemy):
-- (All needed indexes are already in the SQLAlchemy models)

-- Update timestamp trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply update trigger to users table
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Insert a default admin user for testing (password: admin123)
-- Note: In production, use proper password hashing
INSERT INTO users (id, email, username, password_hash) VALUES
    (uuid_generate_v4(), 'admin@example.com', 'admin', 'hashed_password_placeholder')
ON CONFLICT (username) DO NOTHING;
