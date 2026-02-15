"""
Migration script to add share_access_level column to notes table
Run this script to update the database schema
"""
import sqlite3
import os

def run_migration():
    # Determine database path
    # Try different common locations
    possible_paths = [
        os.path.join(os.path.dirname(__file__), 'teamledger.db'),
        os.path.join(os.path.dirname(__file__), 'data', 'teamledger.db'),
        os.path.join(os.path.dirname(__file__), 'app', 'teamledger.db'),
    ]
    
    db_path = None
    for path in possible_paths:
        if os.path.exists(path):
            db_path = path
            break
            
    if not db_path:
        print("Could not find database file.")
        return
    
    print(f"Using database at: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if column already exists
        cursor.execute("PRAGMA table_info(notes)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'share_access_level' in columns:
            print("✓ share_access_level column already exists")
        else:
            print("Adding share_access_level column to notes table...")
            cursor.execute("""
                ALTER TABLE notes 
                ADD COLUMN share_access_level TEXT DEFAULT 'view'
            """)
            
            conn.commit()
            print("✓ Migration completed successfully: Added share_access_level column")
        
        conn.close()
        
    except Exception as e:
        print(f"✗ Migration failed: {e}")
        raise

if __name__ == "__main__":
    run_migration()
