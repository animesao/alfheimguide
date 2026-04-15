#!/usr/bin/env python3
"""
Debug script to check GitHub tracking status
"""

import os
from dotenv import load_dotenv
from database import SessionLocal, TrackedUser, GuildConfig, RepoSnapshot

load_dotenv()

def check_github_tracking():
    print("🔍 Checking GitHub Tracking Status...")
    print("=" * 60)
    
    # Check GITHUB_TOKEN
    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        print("❌ GITHUB_TOKEN not found in .env file!")
        print("💡 Add GITHUB_TOKEN to your .env file")
        return
    else:
        print(f"✅ GITHUB_TOKEN found: {github_token[:10]}...")
    
    # Check database
    session = SessionLocal()
    try:
        # Check tracked users
        tracked_users = session.query(TrackedUser).all()
        print(f"\n📊 Tracked Users: {len(tracked_users)}")
        
        if not tracked_users:
            print("⚠️  No users are being tracked!")
            print("💡 Use /add_user command to add GitHub users")
            return
        
        for user in tracked_users:
            print(f"\n👤 User: {user.github_username}")
            print(f"   Guild ID: {user.guild_id}")
            
            # Check guild config
            config = session.query(GuildConfig).filter_by(guild_id=user.guild_id).first()
            if not config:
                print(f"   ❌ No config found for guild {user.guild_id}")
                continue
            
            print(f"   GitHub Enabled: {'✅' if config.github_enabled else '❌'}")
            print(f"   Target Channel: {config.target_channel_id or 'Not set'}")
            
            if not config.github_enabled:
                print(f"   ⚠️  GitHub tracking is DISABLED for this server")
                print(f"   💡 Use: /config module:GitHub action:Enable")
            
            if not config.target_channel_id:
                print(f"   ⚠️  No notification channel set")
                print(f"   💡 Use: /set_channel")
            
            # Check snapshots
            snapshots = session.query(RepoSnapshot).filter_by(tracked_user_id=user.id).all()
            print(f"   Repositories: {len(snapshots)}")
            
            if snapshots:
                print(f"   Latest repos:")
                for snap in snapshots[:5]:
                    print(f"      • {snap.repo_name} (last push: {snap.last_pushed_at})")
        
        # Summary
        print("\n" + "=" * 60)
        print("📋 Summary:")
        
        active_tracking = 0
        for user in tracked_users:
            config = session.query(GuildConfig).filter_by(guild_id=user.guild_id).first()
            if config and config.github_enabled and config.target_channel_id:
                active_tracking += 1
        
        print(f"   Total tracked users: {len(tracked_users)}")
        print(f"   Active tracking: {active_tracking}")
        print(f"   Inactive tracking: {len(tracked_users) - active_tracking}")
        
        if active_tracking == 0:
            print("\n⚠️  GitHub tracking is not active!")
            print("\n🔧 To fix:")
            print("   1. Enable GitHub module: /config module:GitHub action:Enable")
            print("   2. Set notification channel: /set_channel")
            print("   3. Add GitHub user: /add_user username:octocat")
        else:
            print("\n✅ GitHub tracking is active!")
            print("   Bot checks for updates every 2 minutes")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    check_github_tracking()
