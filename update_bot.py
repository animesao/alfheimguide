#!/usr/bin/env python3
"""
Manual update script for Alfheim Guide Bot
Run this to check for updates and optionally install them
"""

import asyncio
import sys
import argparse
from update_checker import check_and_update

def print_banner():
    print("=" * 60)
    print("🤖 Alfheim Guide Bot - Update Manager")
    print("=" * 60)
    print()

async def main():
    parser = argparse.ArgumentParser(description="Check and install bot updates")
    parser.add_argument(
        "--auto-update",
        action="store_true",
        help="Automatically install updates if available"
    )
    parser.add_argument(
        "--version",
        type=str,
        default=None,
        help="Current version (reads from version.txt if not provided)"
    )
    
    args = parser.parse_args()
    
    print_banner()
    
    # Get current version
    current_version = args.version
    if not current_version:
        try:
            with open("version.txt", "r") as f:
                current_version = f.read().strip()
        except FileNotFoundError:
            print("❌ Error: version.txt not found")
            sys.exit(1)
    
    print(f"📦 Current version: v{current_version}")
    print()
    
    # Check for updates
    print("🔍 Checking for updates...")
    update_info = await check_and_update(current_version, auto_update=args.auto_update)
    
    if update_info:
        print()
        print("🎉 NEW VERSION AVAILABLE!")
        print(f"   Version: v{update_info.get('version')}")
        print(f"   Release: {update_info.get('name')}")
        print(f"   URL: {update_info.get('html_url')}")
        print()
        
        if update_info.get("body"):
            print("📝 Release Notes:")
            print("-" * 60)
            # Print first 10 lines of release notes
            lines = update_info["body"].split("\n")[:10]
            for line in lines:
                print(f"   {line}")
            if len(update_info["body"].split("\n")) > 10:
                print("   ...")
            print("-" * 60)
            print()
        
        if args.auto_update:
            if update_info.get("auto_update_success"):
                print("✅ Update installed successfully!")
                print("🔄 Please restart the bot to apply changes")
                print()
                print("   python main.py")
            else:
                print("❌ Auto-update failed")
                print("💡 Try manual update:")
                print("   git pull origin main")
                print("   pip install -r requirements.txt --upgrade")
        else:
            print("💡 To install this update, run:")
            print("   python update_bot.py --auto-update")
            print()
            print("   Or manually:")
            print("   git pull origin main")
            print("   pip install -r requirements.txt --upgrade")
    else:
        print("✅ Bot is up to date!")
    
    print()
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
