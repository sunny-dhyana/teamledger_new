"""
Migration script to add share_token column to notes table
Run this script to update the database schema
"""
import sqlite3
import os

def run_migration():
    # Determine database path
    db_path = os.path.join(os.path.dirname(__file__), 'teamledger.db', 'teamledger.db')
    
    # Check if database exists
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        # Try alternative path
        db_path = os.path.join(os.path.dirname(__file__), 'data', 'teamledger.db')
        if not os.path.exists(db_path):
            print(f"Database not found at {db_path} either")
            return
    
    print(f"Using database at: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if column already exists
        cursor.execute("PRAGMA table_info(notes)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'share_token' in columns:
            print("✓ share_token column already exists")
        else:
            print("Adding share_token column to notes table...")
            cursor.execute("""
                ALTER TABLE notes 
                ADD COLUMN share_token TEXT
            """)
            
            # Create unique index on share_token
            cursor.execute("""
                CREATE UNIQUE INDEX IF NOT EXISTS idx_notes_share_token 
                ON notes(share_token)
            """)
            
            conn.commit()
            print("✓ Migration completed successfully")
        
        conn.close()
        
    except Exception as e:
        print(f"✗ Migration failed: {e}")
        raise

if __name__ == "__main__":
    run_migration()
