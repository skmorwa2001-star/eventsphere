import sqlite3

DATABASE_PATH="eventsphere.db"

connection=sqlite3.connect(DATABASE_PATH)

try:
    cursor=connection.cursor()

    cursor.execute("PRAGMA table_info(registrations)")
    columns=[column[1] for column in cursor.fetchall()]

    if "ticket_code" not in columns:
        cursor.execute("ALTER TABLE registrations ADD COLUMN ticket_code VARCHAR(36)")
        connection.commit()
        print("ticket_code column add successfully")
    else:
        print("ticket_code column already exists")

    cursor.execute("PRAGMA table_info(registrations)")
    columns=[column[1] for column in cursor.fetchall()]

    if "checked_in" not in columns:
        cursor.execute("ALTER TABLE registrations "
                       "ADD COLUMN checked_in INTEGER NOT NULL DEFAULT 0")
        connection.commit()
        print("checked_in column added successfully")
    else:
        print("checked_in column already exists")    

except sqlite3.Error as error:
    connection.rollback()
    print(f"Database migration failed: {error}")

finally:
    connection.close()                