import psycopg2
from connect import connect

def get_contacts(pattern=None, limit=None, offset=None):
    conn = connect()
    cur = conn.cursor()
    if pattern:
        cur.execute("SELECT * FROM get_contacts_by_pattern(%s)", (pattern,))
    elif limit is not None and offset is not None:
        cur.execute("SELECT * FROM get_contacts_paginated(%s, %s)", (limit, offset))
    else:
        cur.execute("SELECT id, name, phone FROM contacts")
    results = cur.fetchall()
    cur.close()
    conn.close()
    return results

def add_contact(name, phone):
    conn = connect()
    cur = conn.cursor()
    cur.callproc('upsert_contact', (name, phone))
    conn.commit()
    cur.close()
    conn.close()

def add_many_contacts(names, phones):
    conn = connect()
    cur = conn.cursor()
    cur.callproc('upsert_many_contacts', (names, phones))
    conn.commit()
    cur.close()
    conn.close()

def remove_contact(key):
    conn = connect()
    cur = conn.cursor()
    cur.callproc('delete_contact', (key,))
    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    add_contact("Alice", "1234567890")
    add_many_contacts(["Bob", "Charlie"], ["0987654321", "not_a_number"])
    print(get_contacts(pattern="Ali"))
    print(get_contacts(limit=2, offset=0))
    remove_contact("Alice")