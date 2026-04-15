#!/usr/bin/env python3
"""
Database Status Checker for Alfheim Guide Bot
Shows current database structure and statistics
"""

import os
import sqlite3
from datetime import datetime

DB_PATH = "db/bot-db.db"

def format_size(size_bytes):
    """Format bytes to human readable size"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"

def check_database():
    """Check database status and structure"""
    
    print("""
╔══════════════════════════════════════════════════════════╗
║     Alfheim Guide Bot - Database Status Checker         ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    # Check if database exists
    if not os.path.exists(DB_PATH):
        print("❌ Database not found!")
        print(f"📁 Expected location: {DB_PATH}")
        print("\n💡 Run 'python main.py' to create the database")
        return
    
    # Get file info
    file_size = os.path.getsize(DB_PATH)
    modified_time = datetime.fromtimestamp(os.path.getmtime(DB_PATH))
    
    print(f"📊 Database Information")
    print("=" * 60)
    print(f"📁 Location: {DB_PATH}")
    print(f"💾 Size: {format_size(file_size)}")
    print(f"🕐 Last Modified: {modified_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Connect to database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Get all tables
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' 
            ORDER BY name
        """)
        tables = [row[0] for row in cursor.fetchall()]
        
        print(f"\n📋 Tables ({len(tables)} total)")
        print("=" * 60)
        
        # Required tables for v2.0.0
        required_tables = {
            # Core
            "guild_configs": "⚙️ Server Settings",
            
            # Economy
            "user_economy": "💰 User Balances",
            "shop_items": "🛒 Shop Items",
            "transactions": "💳 Transaction History",
            
            # Utilities
            "reminders": "⏰ Reminders",
            "polls": "📊 Polls",
            "poll_votes": "🗳️ Poll Votes",
            
            # Moderation
            "reports": "🚨 User Reports",
            "message_logs": "📝 Message Logs",
            "user_activity": "📈 User Activity",
            "raid_protection": "🛡️ Raid Protection",
            "suspicious_joins": "⚠️ Suspicious Joins",
            
            # Existing
            "tracked_users": "🔍 GitHub Users",
            "repo_snapshots": "📦 GitHub Repos",
            "user_levels": "📊 User Levels",
            "warnings": "⚠️ Warnings",
            "temp_bans": "⏳ Temporary Bans",
            "voice_channel_configs": "🎤 Voice Configs",
            "temp_voice_channels": "🔊 Temp Channels",
            "ticket_categories": "🎫 Ticket Categories",
            "verification_configs": "🔐 Verification",
            "verification_buttons": "🔘 Verification Buttons",
        }
        
        # Check each table
        for table in tables:
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            
            # Get column count
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()
            col_count = len(columns)
            
            # Status indicator
            status = "✅" if table in required_tables else "📦"
            description = required_tables.get(table, "Legacy Table")
            
            print(f"{status} {table:<30} {description:<25} ({count:>6} rows, {col_count:>2} cols)")
        
        # Check for missing tables
        missing_tables = set(required_tables.keys()) - set(tables)
        if missing_tables:
            print(f"\n⚠️  Missing Tables ({len(missing_tables)})")
            print("=" * 60)
            for table in missing_tables:
                print(f"❌ {table:<30} {required_tables[table]}")
            print("\n💡 Run 'python migrate_database.py' to add missing tables")
        
        # Check guild_configs columns
        print(f"\n⚙️  Guild Config Columns")
        print("=" * 60)
        
        if "guild_configs" in tables:
            cursor.execute("PRAGMA table_info(guild_configs)")
            columns = cursor.fetchall()
            
            required_columns = {
                "guild_id": "Server ID",
                "target_channel_id": "Notification Channel",
                "language": "Language (RU/EN)",
                "embed_color": "Embed Color",
                "levels_enabled": "Levels Module",
                "github_enabled": "GitHub Module",
                "welcome_enabled": "Welcome Module",
                "economy_enabled": "Economy Module",
                "stats_enabled": "Statistics Module",
                "automod_enabled": "Auto-Moderation",
                "log_channel_id": "Log Channel",
                "report_channel_id": "Report Channel",
            }
            
            existing_cols = {col[1] for col in columns}
            
            for col_name, description in required_columns.items():
                status = "✅" if col_name in existing_cols else "❌"
                print(f"{status} {col_name:<25} {description}")
            
            missing_cols = set(required_columns.keys()) - existing_cols
            if missing_cols:
                print(f"\n⚠️  Missing {len(missing_cols)} columns in guild_configs")
                print("💡 Run 'python migrate_database.py' to add them")
        
        # Statistics
        print(f"\n📊 Database Statistics")
        print("=" * 60)
        
        stats = {}
        
        # Economy stats
        if "user_economy" in tables:
            cursor.execute("SELECT COUNT(*), SUM(balance + bank) FROM user_economy")
            count, total = cursor.fetchone()
            stats["Economy Users"] = f"{count:,}"
            stats["Total Coins"] = f"{total or 0:,}"
        
        if "shop_items" in tables:
            cursor.execute("SELECT COUNT(*) FROM shop_items")
            stats["Shop Items"] = f"{cursor.fetchone()[0]:,}"
        
        if "transactions" in tables:
            cursor.execute("SELECT COUNT(*) FROM transactions")
            stats["Transactions"] = f"{cursor.fetchone()[0]:,}"
        
        # Utility stats
        if "reminders" in tables:
            cursor.execute("SELECT COUNT(*) FROM reminders")
            stats["Active Reminders"] = f"{cursor.fetchone()[0]:,}"
        
        if "polls" in tables:
            cursor.execute("SELECT COUNT(*) FROM polls")
            stats["Total Polls"] = f"{cursor.fetchone()[0]:,}"
        
        # Moderation stats
        if "reports" in tables:
            cursor.execute("SELECT COUNT(*) FROM reports WHERE status='pending'")
            stats["Pending Reports"] = f"{cursor.fetchone()[0]:,}"
        
        if "message_logs" in tables:
            cursor.execute("SELECT COUNT(*) FROM message_logs")
            stats["Logged Messages"] = f"{cursor.fetchone()[0]:,}"
        
        if "warnings" in tables:
            cursor.execute("SELECT COUNT(*) FROM warnings")
            stats["Total Warnings"] = f"{cursor.fetchone()[0]:,}"
        
        # Other stats
        if "guild_configs" in tables:
            cursor.execute("SELECT COUNT(*) FROM guild_configs")
            stats["Configured Servers"] = f"{cursor.fetchone()[0]:,}"
        
        if "user_levels" in tables:
            cursor.execute("SELECT COUNT(*) FROM user_levels")
            stats["Users with Levels"] = f"{cursor.fetchone()[0]:,}"
        
        if "tracked_users" in tables:
            cursor.execute("SELECT COUNT(*) FROM tracked_users")
            stats["Tracked GitHub Users"] = f"{cursor.fetchone()[0]:,}"
        
        # Print stats
        for key, value in stats.items():
            print(f"  {key:<25} {value:>10}")
        
        # Database health check
        print(f"\n🏥 Database Health")
        print("=" * 60)
        
        cursor.execute("PRAGMA integrity_check")
        integrity = cursor.fetchone()[0]
        
        if integrity == "ok":
            print("✅ Integrity Check: PASSED")
        else:
            print(f"❌ Integrity Check: FAILED - {integrity}")
        
        cursor.execute("PRAGMA foreign_key_check")
        fk_errors = cursor.fetchall()
        
        if not fk_errors:
            print("✅ Foreign Keys: OK")
        else:
            print(f"⚠️  Foreign Key Errors: {len(fk_errors)}")
        
        # Version check
        print(f"\n📦 Version Information")
        print("=" * 60)
        
        # Check if all v2.0.0 tables exist
        v2_tables = [
            "user_economy", "shop_items", "transactions",
            "reminders", "polls", "poll_votes",
            "reports", "message_logs", "user_activity",
            "raid_protection", "suspicious_joins"
        ]
        
        v2_exists = all(table in tables for table in v2_tables)
        
        if v2_exists:
            print("✅ Database Version: 2026.4.15 (Latest)")
            print("🎉 All features available!")
        else:
            print("⚠️  Database Version: Outdated")
            print("💡 Run 'python migrate_database.py' to upgrade to v2026.4.15")
        
        print("\n" + "=" * 60)
        print("✅ Database check complete!")
        
    except Exception as e:
        print(f"\n❌ Error checking database: {e}")
    
    finally:
        conn.close()

def main():
    check_database()

if __name__ == "__main__":
    main()
