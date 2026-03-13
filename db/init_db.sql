CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS keys_table (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    hashed_api_key TEXT UNIQUE NOT NULL,
    key_fingerprint TEXT UNIQUE,
    disabled BOOLEAN DEFAULT FALSE,
    total_requests INT DEFAULT 0,
    max_requests INT DEFAULT 5
);