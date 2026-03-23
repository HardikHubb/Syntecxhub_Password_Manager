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

def menu():
    while True:
        print("\n=== Password Manager ===")
        print("1. Add Credentials")
        print("2. Show Credentials")
        print("3. Exit")

        choice = input("Enter choice: ")

        if choice == "1":
            add_credentials()

        elif choice == "2":
            show_credentials()

        elif choice == "3":
            print("Exiting...")
            break

        else:
            print("Invalid choice ❌")
    
menu()