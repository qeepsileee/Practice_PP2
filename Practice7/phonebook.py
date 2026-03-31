from connect import connect
import csv
import os


def insert_contact(name, phone):
    conn = connect()
    if conn is None:
        return

    cur = conn.cursor()

    cur.execute(
        "INSERT INTO contacts (name, phone) VALUES (%s, %s)",
        (name, phone)
    )

    conn.commit()
    cur.close()
    conn.close()


def get_contacts():
    conn = connect()
    if conn is None:
        return

    cur = conn.cursor()
    cur.execute("SELECT * FROM contacts")
    rows = cur.fetchall()

    if not rows:
        print("No contacts found.")
    else:
        for row in rows:
            print(f"ID: {row[0]}, Name: {row[1]}, Phone: {row[2]}")

    cur.close()
    conn.close()


def update_contact(name, new_phone):
    conn = connect()
    if conn is None:
        return

    cur = conn.cursor()

    cur.execute(
        "UPDATE contacts SET phone=%s WHERE name=%s",
        (new_phone, name)
    )

    conn.commit()
    print("Contact updated.")

    cur.close()
    conn.close()


def delete_contact(name):
    conn = connect()
    if conn is None:
        return

    cur = conn.cursor()

    cur.execute(
        "DELETE FROM contacts WHERE name=%s",
        (name,)
    )

    conn.commit()
    print("Contact deleted.")

    cur.close()
    conn.close()


def insert_from_csv():
    conn = connect()
    if conn is None:
        return

    cur = conn.cursor()

    try:
        # путь к текущей папке
        base_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_dir, "contacts.csv")

        print("Looking for:", file_path)

        if not os.path.exists(file_path):
            print(" File contacts.csv not found!")
            return

        with open(file_path, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                cur.execute(
                    "INSERT INTO contacts (name, phone) VALUES (%s, %s)",
                    (row["name"], row["phone"])
                )

        conn.commit()
        print("CSV data imported successfully.")

    except Exception as e:
        print("CSV Error:", e)

    cur.close()
    conn.close()


def search_by_name(name):
    conn = connect()
    if conn is None:
        return

    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM contacts WHERE name ILIKE %s",
        ('%' + name + '%',)
    )

    rows = cur.fetchall()

    if not rows:
        print("No matches found.")
    else:
        for row in rows:
            print(f"ID: {row[0]}, Name: {row[1]}, Phone: {row[2]}")

    cur.close()
    conn.close()


def menu():
    while True:
        print("\n===== PHONEBOOK MENU =====")
        print("1. Add Contact")
        print("2. Show Contacts")
        print("3. Update Contact")
        print("4. Delete Contact")
        print("5. Import from CSV")
        print("6. Search by Name")
        print("7. Exit")

        choice = input("Choose: ")

        if choice == "1":
            name = input("Name: ")
            phone = input("Phone: ")
            insert_contact(name, phone)

        elif choice == "2":
            get_contacts()

        elif choice == "3":
            name = input("Name: ")
            phone = input("New phone: ")
            update_contact(name, phone)

        elif choice == "4":
            name = input("Name: ")
            delete_contact(name)

        elif choice == "5":
            insert_from_csv()

        elif choice == "6":
            name = input("Search name: ")
            search_by_name(name)

        elif choice == "7":
            print("Goodbye!")
            break

        else:
            print("Invalid choice!")


if __name__ == "__main__":
    menu()