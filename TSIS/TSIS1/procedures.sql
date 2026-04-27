CREATE OR REPLACE PROCEDURE add_phone(
    p_contact_name VARCHAR,
    p_phone        VARCHAR,
    p_type         VARCHAR DEFAULT 'mobile'
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_id INTEGER;
BEGIN
    -- Validate phone type
    IF p_type NOT IN ('home', 'work', 'mobile') THEN
        RAISE EXCEPTION 'Invalid phone type: %. Must be home, work, or mobile.', p_type;
    END IF;

    -- Validate phone digits only
    IF p_phone !~ '^[0-9+\-\s()]+$' THEN
        RAISE EXCEPTION 'Invalid phone number format: %', p_phone;
    END IF;

    SELECT id INTO v_id FROM contacts WHERE name = p_contact_name;

    IF v_id IS NULL THEN
        RAISE EXCEPTION 'Contact "%" not found.', p_contact_name;
    END IF;

    INSERT INTO phones (contact_id, phone, type)
    VALUES (v_id, p_phone, p_type);

    RAISE NOTICE 'Phone % (%) added to contact "%".', p_phone, p_type, p_contact_name;
END;
$$;


CREATE OR REPLACE PROCEDURE move_to_group(
    p_contact_name VARCHAR,
    p_group_name   VARCHAR
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_group_id   INTEGER;
    v_contact_id INTEGER;
BEGIN
    -- Ensure group exists, create if not
    INSERT INTO groups (name)
    VALUES (p_group_name)
    ON CONFLICT (name) DO NOTHING;

    SELECT id INTO v_group_id FROM groups WHERE name = p_group_name;
    SELECT id INTO v_contact_id FROM contacts WHERE name = p_contact_name;

    IF v_contact_id IS NULL THEN
        RAISE EXCEPTION 'Contact "%" not found.', p_contact_name;
    END IF;

    UPDATE contacts SET group_id = v_group_id WHERE id = v_contact_id;

    RAISE NOTICE 'Contact "%" moved to group "%".', p_contact_name, p_group_name;
END;
$$;



CREATE OR REPLACE FUNCTION search_contacts(p_query TEXT)
RETURNS TABLE(
    id       INT,
    name     TEXT,
    email    TEXT,
    birthday DATE,
    grp      TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT DISTINCT
        c.id,
        c.name::TEXT,
        c.email::TEXT,
        c.birthday,
        g.name::TEXT AS grp
    FROM contacts c
    LEFT JOIN groups g  ON g.id  = c.group_id
    LEFT JOIN phones ph ON ph.contact_id = c.id
    WHERE
        c.name  ILIKE '%' || p_query || '%'
     OR c.email ILIKE '%' || p_query || '%'
     OR ph.phone ILIKE '%' || p_query || '%'
    ORDER BY c.name;
END;
$$;
