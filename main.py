import os
import hashlib
import sqlite3


def initialize_db():
    conn = sqlite3.connect("vault.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS credentials (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        website TEXT NOT NULL,
        username TEXT NOT NULL,
        password TEXT NOT NULL
    )
    """)

    conn.commit()
    conn.close()

initialize_db()

FILE_NAME = "master.txt"

# Function to hash password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# Check if master.txt exists
if not os.path.exists(FILE_NAME):
    print("=== First Time Setup ===")
    
    # Set master password
    master_password = input("Set your master password: ")
    hashed_password = hash_password(master_password)

    # Create file and store hash
    with open(FILE_NAME, "w") as file:
        file.write(hashed_password)

    print("Master password set successfully! ✅")

else:
    print("=== Login ===")
    
    # Ask user to enter password
    entered_password = input("Enter master password: ")
    entered_hash = hash_password(entered_password)

    # Read stored hash
    with open(FILE_NAME, "r") as file:
        stored_hash = file.read()

    # Compare hashes
    if entered_hash == stored_hash:
        print("Access Granted ✅")
    else:
        print("Wrong Password ❌")
        exit()



def add_credentials():
    conn = sqlite3.connect("vault.db")
    cursor = conn.cursor()

    website = input("Enter website: ")
    username = input("Enter username: ")
    password = input("Enter password: ")

    cursor.execute("""
    INSERT INTO credentials (website, username, password)
    VALUES (?, ?, ?)
    """, (website, username, password))

    conn.commit()
    conn.close()

    print("Credentials added successfully! ✅")


def show_credentials():
    conn = sqlite3.connect("vault.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM credentials")
    records = cursor.fetchall()

    print("\nStored Credentials:")
    print("-" * 40)

    for row in records:
        print(f"ID: {row[0]}")
        print(f"Website: {row[1]}")
        print(f"Username: {row[2]}")
        print(f"Password: {row[3]}")
        print("-" * 40)

    conn.close()

def edit_credentials():
    conn = sqlite3.connect("vault.db")
    cursor = conn.cursor()

    # Show existing records first
    cursor.execute("SELECT * FROM credentials")
    records = cursor.fetchall()

    if not records:
        print("No credentials found ❌")
        conn.close()
        return

    print("\n=== Existing Credentials ===")
    for row in records:
        print(f"ID: {row[0]} | Website: {row[1]} | Username: {row[2]}")

    # Ask user for ID
    record_id = input("\nEnter ID to edit: ")

    # Check if ID exists
    cursor.execute("SELECT * FROM credentials WHERE id=?", (record_id,))
    result = cursor.fetchone()

    if not result:
        print("Invalid ID ❌")
        conn.close()
        return

    # Take new values
    new_website = input("Enter new website: ")
    new_username = input("Enter new username: ")
    new_password = input("Enter new password: ")

    # Update record
    cursor.execute("""
    UPDATE credentials
    SET website=?, username=?, password=?
    WHERE id=?
    """, (new_website, new_username, new_password, record_id))

    conn.commit()
    conn.close()

    print("Credentials updated successfully ✅")

def delete_credentials():
    conn = sqlite3.connect("vault.db")
    cursor = conn.cursor()

    # Show existing records
    cursor.execute("SELECT * FROM credentials")
    records = cursor.fetchall()

    if not records:
        print("No credentials found ❌")
        conn.close()
        return

    print("\n=== Stored Credentials ===")
    for row in records:
        print(f"ID: {row[0]} | Website: {row[1]} | Username: {row[2]}")

    # Ask for ID
    record_id = input("\nEnter ID to delete: ")

    # Check if ID exists
    cursor.execute("SELECT * FROM credentials WHERE id=?", (record_id,))
    result = cursor.fetchone()

    if not result:
        print("Invalid ID ❌")
        conn.close()
        return

    # Confirmation step (important 🔥)
    confirm = input("Are you sure you want to delete this? (y/n): ")

    if confirm.lower() == "y":
        cursor.execute("DELETE FROM credentials WHERE id=?", (record_id,))
        conn.commit()
        print("Credential deleted successfully ✅")
    else:
        print("Deletion cancelled")

    conn.close()

def menu():
    while True:
        print("\n=== Password Manager ===")
        print("1. Add Credentials")
        print("2. Show Credentials")
        print("3. Edit Credentials")
        print("4. Delete Credentials")
        print("5. Exit")

        choice = input("Enter choice: ")

        if choice == "1":
            add_credentials()

        elif choice == "2":
            show_credentials()

        elif choice == "3":
            edit_credentials()

        elif choice == "4":
            delete_credentials()

        elif choice == "5":
            print("Exiting...")
            break

        else:
            print("Invalid choice ❌")
    
menu()