import os
import sqlite3


def migrate():
    """Migrates the local SQLite database to include missing columns.

    Adds:
    - tours.max_distance (FLOAT, default 100.0)
    - tour_places.is_hotel (BOOLEAN, default 0)
    """
    # SQLite file path inside instance/
    base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    db_path = os.path.join(base_dir, "instance", "travel.db")

    if not os.path.exists(db_path):
        print(f"[-] Database not found at {db_path}. No migration needed.")
        return

    print(f"[*] Found database at {db_path}. Running migrations...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check columns of tours
        cursor.execute("PRAGMA table_info(tours)")
        tours_columns = [col[1] for col in cursor.fetchall()]

        if "max_distance" not in tours_columns:
            print("[+] Adding column 'max_distance' to table 'tours'...")
            cursor.execute("ALTER TABLE tours ADD COLUMN max_distance FLOAT NOT NULL DEFAULT 100.0")
        else:
            print("[~] Column 'max_distance' already exists in table 'tours'.")

        # Check columns of tour_places
        cursor.execute("PRAGMA table_info(tour_places)")
        tour_places_columns = [col[1] for col in cursor.fetchall()]

        if "is_hotel" not in tour_places_columns:
            print("[+] Adding column 'is_hotel' to table 'tour_places'...")
            cursor.execute("ALTER TABLE tour_places ADD COLUMN is_hotel BOOLEAN NOT NULL DEFAULT 0")
        else:
            print("[~] Column 'is_hotel' already exists in table 'tour_places'.")

        conn.commit()
        print("[+] Migration completed successfully!")
    except Exception as e:
        conn.rollback()
        print(f"[-] Migration failed: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    migrate()
