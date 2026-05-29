import os
import sqlite3


def migrate():
    """Migrates the local SQLite database to include missing columns and correct primary keys.

    Adds:
    - tours.max_distance (FLOAT, default 100.0)
    - Migrates tour_places primary key from (tour_id, place_id) to (tour_id, position)
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
        # 1. Check/Add max_distance in tours table
        cursor.execute("PRAGMA table_info(tours)")
        tours_columns = [col[1] for col in cursor.fetchall()]

        if "max_distance" not in tours_columns:
            print("[+] Adding column 'max_distance' to table 'tours'...")
            cursor.execute("ALTER TABLE tours ADD COLUMN max_distance FLOAT NOT NULL DEFAULT 100.0")
        else:
            print("[~] Column 'max_distance' already exists in table 'tours'.")

        # 1.5. Check/Add city in places table
        cursor.execute("PRAGMA table_info(places)")
        places_columns = [col[1] for col in cursor.fetchall()]

        if "city" not in places_columns:
            print("[+] Adding column 'city' to table 'places'...")
            cursor.execute("ALTER TABLE places ADD COLUMN city VARCHAR(100)")
        else:
            print("[~] Column 'city' already exists in table 'places'.")

        # 2. Check primary key of tour_places table
        # Query the creation SQL to check primary key constraint
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='tour_places'")
        sql_row = cursor.fetchone()
        if sql_row:
            create_sql = sql_row[0]
            # If the primary key is (tour_id, place_id), we need to migrate it to (tour_id, position)
            if "PRIMARY KEY (tour_id, place_id)" in create_sql or "PRIMARY KEY(tour_id, place_id)" in create_sql:
                print("[+] Migrating 'tour_places' table to use (tour_id, position) as PRIMARY KEY...")

                # Check columns of tour_places to make sure is_hotel and locked exist in the source
                cursor.execute("PRAGMA table_info(tour_places)")
                tp_cols = [col[1] for col in cursor.fetchall()]
                has_is_hotel = "is_hotel" in tp_cols
                has_locked = "locked" in tp_cols

                # Rename old table
                cursor.execute("ALTER TABLE tour_places RENAME TO tour_places_old")

                # Create new table with correct PRIMARY KEY and columns
                cursor.execute("""
                    CREATE TABLE tour_places (
                        tour_id INTEGER NOT NULL,
                        place_id INTEGER NOT NULL,
                        position INTEGER NOT NULL,
                        locked BOOLEAN NOT NULL DEFAULT 0,
                        is_hotel BOOLEAN NOT NULL DEFAULT 0,
                        PRIMARY KEY (tour_id, position),
                        FOREIGN KEY(tour_id) REFERENCES tours (id) ON DELETE CASCADE,
                        FOREIGN KEY(place_id) REFERENCES places (id) ON DELETE CASCADE
                    )
                """)

                # Copy data from old to new
                select_locked = "locked" if has_locked else "0"
                select_is_hotel = "is_hotel" if has_is_hotel else "0"
                cursor.execute(f"""
                    INSERT INTO tour_places (tour_id, place_id, position, locked, is_hotel)
                    SELECT tour_id, place_id, position, {select_locked}, {select_is_hotel} FROM tour_places_old
                """)

                # Drop old table
                cursor.execute("DROP TABLE tour_places_old")
                print("[+] 'tour_places' table migrated successfully!")
            else:
                print("[~] 'tour_places' table already has the correct PRIMARY KEY structure.")
        else:
            print("[-] 'tour_places' table does not exist.")

        conn.commit()
        print("[+] Migration completed successfully!")
    except Exception as e:
        conn.rollback()
        print(f"[-] Migration failed: {e}")
        raise e
    finally:
        conn.close()


if __name__ == "__main__":
    migrate()
