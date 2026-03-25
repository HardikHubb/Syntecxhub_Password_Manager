import os
import hashlib
import sqlite3
import random
import string
import shutil
import base64
from cryptography.fernet import Fernet

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

def generate_key(master_password):
    key = hashlib.sha256(master_password.encode()).digest()
    return base64.urlsafe_b64encode(key)


FILE_NAME = "master.txt"

# Function to hash password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def encrypt_password(password, key):
    f = Fernet(key)
    return f.encrypt(password.encode()).decode()

def decrypt_password(encrypted_password, key):
    f = Fernet(key)
    return f.decrypt(encrypted_password.encode()).decode()

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
        key = generate_key(entered_password)
    else:
        print("Wrong Password ❌")
        exit()




def generate_password():
    length = 32
    characters = string.ascii_letters + string.digits + string.punctuation

    password = ''.join(random.choice(characters) for _ in range(length))

    print("\nGenerated Password:")
    print(password)

    use = input("Do you want to use this password? (y/n): ")

    if use.lower() == "y":
        return password
    else:
        return None
    
  

def add_credentials(key):
    conn = sqlite3.connect("vault.db")
    cursor = conn.cursor()

    website = input("Enter website: ")
    username = input("Enter username: ")

    choice = input("Generate strong password? (y/n): ")

    if choice.lower() == "y":
        password = generate_password()

        if password is None:
            password = input("Enter password manually: ")
    else:
        password = input("Enter password: ")

       # 🔥 Encrypt before storing
    encrypted_password = encrypt_password(password, key)

    cursor.execute("""
    INSERT INTO credentials (website, username, password)
    VALUES (?, ?, ?)
    """, (website, username, encrypted_password))

    conn.commit()
    conn.close()

    print("Credentials added successfully ✅")


def show_credentials(key):
    conn = sqlite3.connect("vault.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM credentials")
    records = cursor.fetchall()

     for row in records:
        decrypted_password = decrypt_password(row[3], key)

    print("\nStored Credentials:")
    print("-" * 40)

    for row in records:
        print(f"ID: {row[0]}")
        print(f"Website: {row[1]}")
        print(f"Username: {row[2]}")
        print(f"Password: {decrypted_password}")
        print("-" * 40)

    conn.close()

def edit_credentials(key):
    conn = sqlite3.connect("vault.db")
    cursor = conn.cursor()

    # Show existing records
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

    cursor.execute("SELECT * FROM credentials WHERE id=?", (record_id,))
    result = cursor.fetchone()

    if not result:
        print("Invalid ID ❌")
        conn.close()
        return

    # 🔓 Decrypt old password for reference
    old_password = decrypt_password(result[3], key)

    print("\nLeave blank to keep existing value")

    # Take new values (with fallback)
    new_website = input(f"Enter new website [{result[1]}]: ")
    if new_website == "":
        new_website = result[1]

    new_username = input(f"Enter new username [{result[2]}]: ")
    if new_username == "":
        new_username = result[2]

    new_password = input("Enter new password (leave blank to keep old): ")
    if new_password == "":
        new_password = old_password

    # 🔐 Encrypt new password before storing
    encrypted_password = encrypt_password(new_password, key)

    # Update record
    cursor.execute("""
    UPDATE credentials
    SET website=?, username=?, password=?
    WHERE id=?
    """, (new_website, new_username, encrypted_password, record_id))

    conn.commit()
    conn.close()

    print("Credentials updated successfully 🔐✅")

def delete_credentials(key):
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



def backup_database(key):
    try:
        shutil.copy("vault.db", "vault_backup.db")
        print("Backup created successfully ✅")
    except Exception as e:
        print("Backup failed ❌", e)


def erase_database(key):
    confirm = input("⚠️ Are you sure you want to delete ALL credentials? (y/n): ")

    if confirm.lower() == "y":
        conn = sqlite3.connect("vault.db")
        cursor = conn.cursor()

        cursor.execute("DELETE FROM credentials")

        conn.commit()
        conn.close()

        print("All credentials erased ❗")
    else:
        print("Operation cancelled")



def menu(key):
    while True:
        print("\n=== Password Manager ===")
        print("1. Add Credentials")
        print("2. Show Credentials")
        print("3. Edit Credentials")
        print("4. Delete Credentials")
        print("5. Backup Database")
        print("6. Erase the Database")
        print("7. Exit")

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
            backup_database()

        elif choice == "6":
            erase_database()

        elif choice == "7":
            print("Exiting...")
            break

        else:
            print("Invalid choice ❌")
    
menu()