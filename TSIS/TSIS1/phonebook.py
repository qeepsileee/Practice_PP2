import csv
import json
import os
import sys

from connect import connect

PAGE_SIZE = 5  # rows per page for paginated navigation



def _conn_cur():
    """Return (conn, cur) or raise RuntimeError."""
    conn = connect()
    if conn is None:
        raise RuntimeError("Cannot connect to database.")
    return conn, conn.cursor()


def _close(conn, cur):
    cur.close()
    conn.close()


def _fmt_row(row):
    """Pretty-print a contact row returned by search_contacts / list queries."""
    id_, name, email, birthday, grp = row
    return (
        f"  ID={id_:<4} | {name:<20} | "
        f"Email: {email or '—':<25} | "
        f"Birthday: {birthday or '—'} | "
        f"Group: {grp or '—'}"
    )


# ──────────────────────────────────────────────
# 3.2 Advanced Search & Filter
# ──────────────────────────────────────────────

def filter_by_group():
    conn, cur = _conn_cur()
    try:
        cur.execute("SELECT id, name FROM groups ORDER BY name")
        groups = cur.fetchall()
        if not groups:
            print("No groups found.")
            return

        print("\nAvailable groups:")
        for g in groups:
            print(f"  {g[0]}. {g[1]}")

        choice = input("Enter group name (or part): ").strip()

        cur.execute(
            """
            SELECT c.id, c.name, c.email, c.birthday, gr.name
            FROM contacts c
            LEFT JOIN groups gr ON gr.id = c.group_id
            WHERE gr.name ILIKE %s
            ORDER BY c.name
            """,
            (f"%{choice}%",),
        )
        rows = cur.fetchall()
        _print_contacts(rows)
    finally:
        _close(conn, cur)


def search_by_email():
    conn, cur = _conn_cur()
    try:
        query = input("Email search term: ").strip()
        cur.execute(
            """
            SELECT c.id, c.name, c.email, c.birthday, g.name
            FROM contacts c
            LEFT JOIN groups g ON g.id = c.group_id
            WHERE c.email ILIKE %s
            ORDER BY c.name
            """,
            (f"%{query}%",),
        )
        rows = cur.fetchall()
        _print_contacts(rows)
    finally:
        _close(conn, cur)


def sort_contacts():
    print("\nSort by: 1) Name  2) Birthday  3) Date Added")
    choice = input("Choice: ").strip()
    order_map = {"1": "c.name", "2": "c.birthday", "3": "c.created_at"}
    order = order_map.get(choice, "c.name")

    conn, cur = _conn_cur()
    try:
        cur.execute(
            f"""
            SELECT c.id, c.name, c.email, c.birthday, g.name
            FROM contacts c
            LEFT JOIN groups g ON g.id = c.group_id
            ORDER BY {order} NULLS LAST
            """
        )
        rows = cur.fetchall()
        _print_contacts(rows)
    finally:
        _close(conn, cur)


def paginated_navigation():
    """Console loop using the Practice 8 get_contacts_paginated DB function."""
    offset = 0
    while True:
        conn, cur = _conn_cur()
        try:
            # Use the existing Practice 8 paginated function
            cur.execute(
                "SELECT id, name, phone FROM get_contacts_paginated(%s, %s)",
                (PAGE_SIZE, offset),
            )
            rows = cur.fetchall()
        finally:
            _close(conn, cur)

        if not rows and offset == 0:
            print("No contacts found.")
            return

        page_num = offset // PAGE_SIZE + 1
        print(f"\n── Page {page_num} ──────────────────────")
        if not rows:
            print("  (no more contacts)")
        else:
            for r in rows:
                print(f"  ID={r[0]:<4} | {r[1]:<20} | Phone: {r[2]}")

        print("Commands: [n]ext  [p]rev  [q]uit")
        cmd = input(">> ").strip().lower()

        if cmd == "n":
            if len(rows) < PAGE_SIZE:
                print("Already on last page.")
            else:
                offset += PAGE_SIZE
        elif cmd == "p":
            if offset == 0:
                print("Already on first page.")
            else:
                offset = max(0, offset - PAGE_SIZE)
        elif cmd == "q":
            break
        else:
            print("Unknown command.")


def _print_contacts(rows):
    if not rows:
        print("  No contacts found.")
    else:
        print(f"\n  {'ID':<6}{'Name':<22}{'Email':<27}{'Birthday':<12}{'Group'}")
        print("  " + "─" * 75)
        for r in rows:
            print(_fmt_row(r))


# ──────────────────────────────────────────────
# 3.3 Import / Export
# ──────────────────────────────────────────────

def export_to_json():
    conn, cur = _conn_cur()
    try:
        cur.execute(
            """
            SELECT c.id, c.name, c.email,
                   c.birthday::TEXT, g.name AS grp,
                   COALESCE(
                       json_agg(
                           json_build_object('phone', ph.phone, 'type', ph.type)
                       ) FILTER (WHERE ph.id IS NOT NULL),
                       '[]'
                   ) AS phones
            FROM contacts c
            LEFT JOIN groups g  ON g.id  = c.group_id
            LEFT JOIN phones ph ON ph.contact_id = c.id
            GROUP BY c.id, c.name, c.email, c.birthday, g.name
            ORDER BY c.name
            """
        )
        rows = cur.fetchall()
        contacts = []
        for r in rows:
            contacts.append(
                {
                    "id": r[0],
                    "name": r[1],
                    "email": r[2],
                    "birthday": r[3],
                    "group": r[4],
                    "phones": r[5],
                }
            )

        base = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(base, "contacts_export.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(contacts, f, indent=2, ensure_ascii=False)

        print(f"Exported {len(contacts)} contacts → {path}")
    finally:
        _close(conn, cur)


def import_from_json():
    base = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base, "contacts_export.json")

    if not os.path.exists(path):
        path = input("Path to JSON file: ").strip()
    if not os.path.exists(path):
        print("File not found.")
        return

    with open(path, "r", encoding="utf-8") as f:
        contacts = json.load(f)

    conn, cur = _conn_cur()
    try:
        inserted = skipped = overwritten = 0

        for c in contacts:
            name = c.get("name", "").strip()
            if not name:
                continue

            # Check duplicate
            cur.execute("SELECT id FROM contacts WHERE name = %s", (name,))
            existing = cur.fetchone()

            if existing:
                print(f'Duplicate: "{name}". [s]kip / [o]verwrite?', end=" ")
                ans = input().strip().lower()
                if ans != "o":
                    skipped += 1
                    continue
                # Overwrite
                cur.execute(
                    """
                    UPDATE contacts
                    SET email = %s, birthday = %s,
                        group_id = (SELECT id FROM groups WHERE name = %s)
                    WHERE name = %s
                    """,
                    (c.get("email"), c.get("birthday"), c.get("group"), name),
                )
                conn.commit()
                overwritten += 1
                contact_id = existing[0]
                # Replace phones
                cur.execute("DELETE FROM phones WHERE contact_id = %s", (contact_id,))
            else:
                # Ensure group
                grp = c.get("group")
                if grp:
                    cur.execute(
                        "INSERT INTO groups (name) VALUES (%s) ON CONFLICT DO NOTHING",
                        (grp,),
                    )
                cur.execute(
                    """
                    INSERT INTO contacts (name, email, birthday, group_id)
                    VALUES (%s, %s, %s,
                            (SELECT id FROM groups WHERE name = %s))
                    RETURNING id
                    """,
                    (name, c.get("email"), c.get("birthday"), grp),
                )
                contact_id = cur.fetchone()[0]
                inserted += 1

            # Insert phones
            for ph in c.get("phones", []):
                if ph.get("phone"):
                    cur.execute(
                        "INSERT INTO phones (contact_id, phone, type) VALUES (%s, %s, %s)",
                        (contact_id, ph["phone"], ph.get("type", "mobile")),
                    )

            conn.commit()

        print(
            f"Import complete: {inserted} inserted, "
            f"{overwritten} overwritten, {skipped} skipped."
        )
    finally:
        _close(conn, cur)


def import_from_csv_extended():
    """
    Extended CSV import (Practice 7 base + new fields).
    Expected columns: name, phone, phone_type, email, birthday, group
    """
    base = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base, "contacts.csv")

    if not os.path.exists(path):
        print(f"contacts.csv not found at {path}")
        return

    conn, cur = _conn_cur()
    try:
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            inserted = 0
            for row in reader:
                name  = row.get("name", "").strip()
                phone = row.get("phone", "").strip()
                ptype = row.get("phone_type", "mobile").strip() or "mobile"
                email = row.get("email", "").strip() or None
                bday  = row.get("birthday", "").strip() or None
                grp   = row.get("group", "").strip() or None

                if not name:
                    continue

                # Ensure group
                if grp:
                    cur.execute(
                        "INSERT INTO groups (name) VALUES (%s) ON CONFLICT DO NOTHING",
                        (grp,),
                    )

                # Upsert contact (re-use Practice 8 procedure for validation)
                cur.execute("CALL upsert_contact(%s, %s)", (name, phone))

                # Update extended fields
                cur.execute(
                    """
                    UPDATE contacts
                    SET email    = COALESCE(%s, email),
                        birthday = COALESCE(%s::DATE, birthday),
                        group_id = COALESCE(
                            (SELECT id FROM groups WHERE name = %s),
                            group_id
                        )
                    WHERE name = %s
                    """,
                    (email, bday, grp, name),
                )

                # Add phone to phones table
                if phone:
                    cur.execute(
                        """
                        SELECT id FROM contacts WHERE name = %s
                        """,
                        (name,),
                    )
                    cid = cur.fetchone()
                    if cid:
                        cur.execute(
                            """
                            INSERT INTO phones (contact_id, phone, type)
                            VALUES (%s, %s, %s)
                            ON CONFLICT DO NOTHING
                            """,
                            (cid[0], phone, ptype),
                        )

                inserted += 1

        conn.commit()
        print(f"CSV import complete: {inserted} rows processed.")
    except Exception as e:
        conn.rollback()
        print(f"CSV import error: {e}")
    finally:
        _close(conn, cur)


# ──────────────────────────────────────────────
# 3.4 New Stored Procedure callers
# ──────────────────────────────────────────────

def add_phone_to_contact():
    name  = input("Contact name: ").strip()
    phone = input("Phone number: ").strip()
    print("Type: 1) mobile  2) home  3) work")
    t_map = {"1": "mobile", "2": "home", "3": "work"}
    ptype = t_map.get(input("Choice [1]: ").strip(), "mobile")

    conn, cur = _conn_cur()
    try:
        cur.execute("CALL add_phone(%s, %s, %s)", (name, phone, ptype))
        conn.commit()
        print(f"Phone added.")
    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
    finally:
        _close(conn, cur)


def move_contact_to_group():
    name  = input("Contact name: ").strip()
    group = input("Group name (will be created if new): ").strip()

    conn, cur = _conn_cur()
    try:
        cur.execute("CALL move_to_group(%s, %s)", (name, group))
        conn.commit()
        print(f'"{name}" moved to group "{group}".')
    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
    finally:
        _close(conn, cur)


def full_search():
    """Uses search_contacts function — searches name, email, all phones."""
    query = input("Search (name / email / phone): ").strip()
    conn, cur = _conn_cur()
    try:
        cur.execute("SELECT * FROM search_contacts(%s)", (query,))
        rows = cur.fetchall()
        _print_contacts(rows)
    finally:
        _close(conn, cur)


def show_phones_for_contact():
    name = input("Contact name: ").strip()
    conn, cur = _conn_cur()
    try:
        cur.execute(
            """
            SELECT ph.id, ph.phone, ph.type
            FROM phones ph
            JOIN contacts c ON c.id = ph.contact_id
            WHERE c.name ILIKE %s
            ORDER BY ph.type
            """,
            (f"%{name}%",),
        )
        rows = cur.fetchall()
        if not rows:
            print("No phone numbers found.")
        else:
            for r in rows:
                print(f"  Phone ID={r[0]} | {r[1]} ({r[2]})")
    finally:
        _close(conn, cur)


# ──────────────────────────────────────────────
# Menu
# ──────────────────────────────────────────────

MENU = """
╔══════════════════════════════════════════╗
║        PHONEBOOK — TSIS 1               ║
╠══════════════════════════════════════════╣
║  SEARCH & FILTER                        ║
║   1. Full search (name/email/phone)     ║
║   2. Filter by group                   ║
║   3. Search by email                   ║
║   4. Sort all contacts                  ║
║   5. Browse (paginated)                 ║
╠══════════════════════════════════════════╣
║  PHONES                                 ║
║   6. Add phone to contact               ║
║   7. Show phones for contact            ║
╠══════════════════════════════════════════╣
║  GROUPS                                 ║
║   8. Move contact to group              ║
╠══════════════════════════════════════════╣
║  IMPORT / EXPORT                        ║
║   9. Export all contacts → JSON         ║
║  10. Import contacts ← JSON             ║
║  11. Import from CSV (extended)         ║
╠══════════════════════════════════════════╣
║   0. Exit                               ║
╚══════════════════════════════════════════╝
"""

ACTIONS = {
    "1": full_search,
    "2": filter_by_group,
    "3": search_by_email,
    "4": sort_contacts,
    "5": paginated_navigation,
    "6": add_phone_to_contact,
    "7": show_phones_for_contact,
    "8": move_contact_to_group,
    "9": export_to_json,
    "10": import_from_json,
    "11": import_from_csv_extended,
}


def menu():
    while True:
        print(MENU)
        choice = input("Choose: ").strip()
        if choice == "0":
            print("Goodbye!")
            sys.exit(0)
        action = ACTIONS.get(choice)
        if action:
            try:
                action()
            except RuntimeError as e:
                print(f"[Error] {e}")
            except KeyboardInterrupt:
                print()
        else:
            print("Invalid choice. Try again.")


if __name__ == "__main__":
    menu()
