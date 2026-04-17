#!/usr/bin/env python3
"""
Database Migration Script for Alfheim Guide Bot
Safely updates existing database with new tables and columns
"""

import os
import sys
import sqlite3
from datetime import datetime
import shutil

# Database path
DB_PATH = "db/bot-db.db"
BACKUP_DIR = "db/backups"

def create_backup():
    """Create a backup of the existing database"""
    if not os.path.exists(DB_PATH):
        print("❌ Database file not found. No backup needed.")
        return None
    
    # Create backup directory
    os.makedirs(BACKUP_DIR, exist_ok=True)
    
    # Create backup filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(BACKUP_DIR, f"bot-db_backup_{timestamp}.db")
    
    # Copy database
    shutil.copy2(DB_PATH, backup_path)
    print(f"✅ Backup created: {backup_path}")
    return backup_path

def table_exists(cursor, table_name):
    """Check if table exists in database"""
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name=?
    """, (table_name,))
    return cursor.fetchone() is not None

def column_exists(cursor, table_name, column_name):
    """Check if column exists in table"""
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in cursor.fetchall()]
    return column_name in columns

def migrate_database():
    """Main migration function"""
    print("🚀 Starting database migration...")
    print("=" * 60)
    
    # Create backup
    backup_path = create_backup()
    
    # Connect to database
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Track changes
        tables_created = []
        columns_added = []
        
        # ==================== GUILD CONFIG UPDATES ====================
        print("\n📋 Checking guild_configs table...")
        
        if table_exists(cursor, "guild_configs"):
            # Add new columns to existing table
            new_columns = [
                ("economy_enabled", "INTEGER DEFAULT 1"),
                ("stats_enabled", "INTEGER DEFAULT 1"),
                ("log_channel_id", "BIGINT"),
                ("report_channel_id", "BIGINT"),
            ]
            
            for col_name, col_type in new_columns:
                if not column_exists(cursor, "guild_configs", col_name):
                    cursor.execute(f"ALTER TABLE guild_configs ADD COLUMN {col_name} {col_type}")
                    columns_added.append(f"guild_configs.{col_name}")
                    print(f"  ✅ Added column: {col_name}")
        
        # ==================== ECONOMY TABLES ====================
        print("\n💰 Checking economy tables...")
        
        # UserEconomy table
        if not table_exists(cursor, "user_economy"):
            cursor.execute("""
                CREATE TABLE user_economy (
                    id INTEGER PRIMARY KEY,
                    guild_id BIGINT,
                    user_id BIGINT,
                    balance INTEGER DEFAULT 0,
                    bank INTEGER DEFAULT 0,
                    last_daily DATETIME,
                    last_work DATETIME,
                    FOREIGN KEY (guild_id) REFERENCES guild_configs(guild_id)
                )
            """)
            tables_created.append("user_economy")
            print("  ✅ Created table: user_economy")
        
        # ShopItem table
        if not table_exists(cursor, "shop_items"):
            cursor.execute("""
                CREATE TABLE shop_items (
                    id INTEGER PRIMARY KEY,
                    guild_id BIGINT,
                    name VARCHAR(100) NOT NULL,
                    description TEXT,
                    price INTEGER NOT NULL,
                    item_type VARCHAR(20) DEFAULT 'role',
                    item_value VARCHAR(200),
                    stock INTEGER DEFAULT -1,
                    FOREIGN KEY (guild_id) REFERENCES guild_configs(guild_id)
                )
            """)
            tables_created.append("shop_items")
            print("  ✅ Created table: shop_items")
        
        # Transaction table
        if not table_exists(cursor, "transactions"):
            cursor.execute("""
                CREATE TABLE transactions (
                    id INTEGER PRIMARY KEY,
                    guild_id BIGINT,
                    user_id BIGINT,
                    amount INTEGER,
                    transaction_type VARCHAR(50),
                    description TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (guild_id) REFERENCES guild_configs(guild_id)
                )
            """)
            tables_created.append("transactions")
            print("  ✅ Created table: transactions")
        
        # ==================== UTILITY TABLES ====================
        print("\n🔧 Checking utility tables...")
        
        # Reminder table
        if not table_exists(cursor, "reminders"):
            cursor.execute("""
                CREATE TABLE reminders (
                    id INTEGER PRIMARY KEY,
                    guild_id BIGINT,
                    user_id BIGINT NOT NULL,
                    channel_id BIGINT NOT NULL,
                    message TEXT NOT NULL,
                    remind_at DATETIME NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            tables_created.append("reminders")
            print("  ✅ Created table: reminders")
        
        # Poll table
        if not table_exists(cursor, "polls"):
            cursor.execute("""
                CREATE TABLE polls (
                    id INTEGER PRIMARY KEY,
                    guild_id BIGINT,
                    channel_id BIGINT,
                    message_id BIGINT UNIQUE,
                    question TEXT NOT NULL,
                    options TEXT NOT NULL,
                    creator_id BIGINT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    ends_at DATETIME,
                    multiple_choice INTEGER DEFAULT 0,
                    FOREIGN KEY (guild_id) REFERENCES guild_configs(guild_id)
                )
            """)
            tables_created.append("polls")
            print("  ✅ Created table: polls")
        
        # PollVote table
        if not table_exists(cursor, "poll_votes"):
            cursor.execute("""
                CREATE TABLE poll_votes (
                    id INTEGER PRIMARY KEY,
                    poll_id INTEGER,
                    user_id BIGINT,
                    option_index INTEGER,
                    FOREIGN KEY (poll_id) REFERENCES polls(id)
                )
            """)
            tables_created.append("poll_votes")
            print("  ✅ Created table: poll_votes")
        
        # ==================== MODERATION TABLES ====================
        print("\n🛡️ Checking moderation tables...")
        
        # Report table
        if not table_exists(cursor, "reports"):
            cursor.execute("""
                CREATE TABLE reports (
                    id INTEGER PRIMARY KEY,
                    guild_id BIGINT,
                    reporter_id BIGINT,
                    reported_user_id BIGINT,
                    reason TEXT,
                    message_link TEXT,
                    status VARCHAR(20) DEFAULT 'pending',
                    moderator_id BIGINT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    resolved_at DATETIME,
                    FOREIGN KEY (guild_id) REFERENCES guild_configs(guild_id)
                )
            """)
            tables_created.append("reports")
            print("  ✅ Created table: reports")
        
        # MessageLog table
        if not table_exists(cursor, "message_logs"):
            cursor.execute("""
                CREATE TABLE message_logs (
                    id INTEGER PRIMARY KEY,
                    guild_id BIGINT,
                    message_id BIGINT UNIQUE,
                    channel_id BIGINT,
                    user_id BIGINT,
                    content TEXT,
                    attachments TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    deleted_at DATETIME,
                    edited_at DATETIME,
                    old_content TEXT,
                    FOREIGN KEY (guild_id) REFERENCES guild_configs(guild_id)
                )
            """)
            tables_created.append("message_logs")
            print("  ✅ Created table: message_logs")
        
        # UserActivity table
        if not table_exists(cursor, "user_activity"):
            cursor.execute("""
                CREATE TABLE user_activity (
                    id INTEGER PRIMARY KEY,
                    guild_id BIGINT,
                    user_id BIGINT,
                    date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    message_count INTEGER DEFAULT 0,
                    voice_minutes INTEGER DEFAULT 0,
                    FOREIGN KEY (guild_id) REFERENCES guild_configs(guild_id)
                )
            """)
            tables_created.append("user_activity")
            print("  ✅ Created table: user_activity")
        
        # RaidProtection table
        if not table_exists(cursor, "raid_protection"):
            cursor.execute("""
                CREATE TABLE raid_protection (
                    id INTEGER PRIMARY KEY,
                    guild_id BIGINT UNIQUE,
                    enabled INTEGER DEFAULT 0,
                    join_threshold INTEGER DEFAULT 5,
                    action VARCHAR(20) DEFAULT 'kick',
                    lockdown_duration INTEGER DEFAULT 10,
                    FOREIGN KEY (guild_id) REFERENCES guild_configs(guild_id)
                )
            """)
            tables_created.append("raid_protection")
            print("  ✅ Created table: raid_protection")
        
        # SuspiciousJoin table
        if not table_exists(cursor, "suspicious_joins"):
            cursor.execute("""
                CREATE TABLE suspicious_joins (
                    id INTEGER PRIMARY KEY,
                    guild_id BIGINT,
                    user_id BIGINT,
                    joined_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (guild_id) REFERENCES guild_configs(guild_id)
                )
            """)
            tables_created.append("suspicious_joins")
            print("  ✅ Created table: suspicious_joins")
        
        # ==================== GITHUB RELEASE TRACKING ====================
        print("\n🎉 Checking GitHub release tracking table...")
        
        # ReleaseSnapshot table
        if not table_exists(cursor, "release_snapshots"):
            cursor.execute("""
                CREATE TABLE release_snapshots (
                    id INTEGER PRIMARY KEY,
                    tracked_user_id INTEGER,
                    repo_name VARCHAR(100) NOT NULL,
                    release_tag VARCHAR(100) NOT NULL,
                    release_name VARCHAR(255),
                    published_at DATETIME NOT NULL,
                    is_prerelease INTEGER DEFAULT 0,
                    is_draft INTEGER DEFAULT 0,
                    FOREIGN KEY (tracked_user_id) REFERENCES tracked_users(id)
                )
            """)
            tables_created.append("release_snapshots")
            print("  ✅ Created table: release_snapshots")
        
        # ==================== CREATE INDEXES ====================
        print("\n📊 Creating indexes for performance...")
        
        indexes = [
            ("idx_user_economy_guild_user", "user_economy", "guild_id, user_id"),
            ("idx_shop_items_guild", "shop_items", "guild_id"),
            ("idx_transactions_guild_user", "transactions", "guild_id, user_id"),
            ("idx_reminders_remind_at", "reminders", "remind_at"),
            ("idx_polls_message_id", "polls", "message_id"),
            ("idx_reports_guild_status", "reports", "guild_id, status"),
            ("idx_message_logs_guild", "message_logs", "guild_id"),
            ("idx_message_logs_message_id", "message_logs", "message_id"),
            ("idx_user_activity_guild_user", "user_activity", "guild_id, user_id"),
            ("idx_release_snapshots_user_repo", "release_snapshots", "tracked_user_id, repo_name"),
            ("idx_release_snapshots_tag", "release_snapshots", "release_tag"),
        ]
        
        for idx_name, table_name, columns in indexes:
            if table_exists(cursor, table_name):
                try:
                    cursor.execute(f"CREATE INDEX IF NOT EXISTS {idx_name} ON {table_name}({columns})")
                    print(f"  ✅ Created index: {idx_name}")
                except sqlite3.OperationalError:
                    pass  # Index might already exist
        
        # Commit all changes
        conn.commit()
        
        # ==================== SUMMARY ====================
        print("\n" + "=" * 60)
        print("✅ Migration completed successfully!")
        print("=" * 60)
        
        if tables_created:
            print(f"\n📦 Created {len(tables_created)} new tables:")
            for table in tables_created:
                print(f"  • {table}")
        
        if columns_added:
            print(f"\n➕ Added {len(columns_added)} new columns:")
            for column in columns_added:
                print(f"  • {column}")
        
        if not tables_created and not columns_added:
            print("\n✨ Database is already up to date!")
        
        if backup_path:
            print(f"\n💾 Backup saved at: {backup_path}")
        
        print("\n🎉 You can now start the bot with: python main.py")
        
    except Exception as e:
        print(f"\n❌ Error during migration: {e}")
        print(f"💾 Database backup is available at: {backup_path}")
        print("🔄 You can restore it if needed")
        conn.rollback()
        return False
    
    finally:
        conn.close()
    
    return True

def verify_database():
    """Verify database integrity after migration"""
    print("\n🔍 Verifying database integrity...")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check integrity
        cursor.execute("PRAGMA integrity_check")
        result = cursor.fetchone()
        
        if result[0] == "ok":
            print("✅ Database integrity check passed!")
            return True
        else:
            print(f"⚠️ Database integrity check failed: {result[0]}")
            return False
    
    except Exception as e:
        print(f"❌ Error verifying database: {e}")
        return False
    
    finally:
        conn.close()

def main():
    """Main entry point"""
    print("""
╔══════════════════════════════════════════════════════════╗
║     Alfheim Guide Bot - Database Migration Tool         ║
║                  Version 2026.4.15                       ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    # Check if database exists
    if not os.path.exists(DB_PATH):
        print("ℹ️  No existing database found.")
        print("✨ A new database will be created when you start the bot.")
        print("\n💡 Run: python main.py")
        return
    
    # Ask for confirmation
    print("⚠️  This script will modify your database.")
    print("📦 A backup will be created automatically.")
    response = input("\n❓ Continue with migration? (yes/no): ").lower().strip()
    
    if response not in ['yes', 'y', 'да', 'д']:
        print("❌ Migration cancelled.")
        return
    
    # Run migration
    success = migrate_database()
    
    if success:
        # Verify database
        verify_database()
        print("\n✅ All done! Your database is ready.")
    else:
        print("\n❌ Migration failed. Please check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
