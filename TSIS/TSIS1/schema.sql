CREATE TABLE IF NOT EXISTS groups (
    id   SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL
);

-- Seed default groups
INSERT INTO groups (name) VALUES
    ('Family'), ('Work'), ('Friend'), ('Other')
ON CONFLICT (name) DO NOTHING;

-- 2. Extend contacts with email, birthday, group FK
ALTER TABLE contacts
    ADD COLUMN IF NOT EXISTS email    VARCHAR(100),
    ADD COLUMN IF NOT EXISTS birthday DATE,
    ADD COLUMN IF NOT EXISTS group_id INTEGER REFERENCES groups(id),
    ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ DEFAULT NOW();

-- Unique constraint on name (needed for ON CONFLICT in upsert)
ALTER TABLE contacts
    ADD CONSTRAINT contacts_name_unique UNIQUE (name);

-- 3. Separate phones table (1-to-many)
CREATE TABLE IF NOT EXISTS phones (
    id         SERIAL PRIMARY KEY,
    contact_id INTEGER REFERENCES contacts(id) ON DELETE CASCADE,
    phone      VARCHAR(20)  NOT NULL,
    type       VARCHAR(10)  CHECK (type IN ('home', 'work', 'mobile')) DEFAULT 'mobile'
);
