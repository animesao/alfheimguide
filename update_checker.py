"""
Auto-update checker for Alfheim Guide Bot
Checks GitHub for new releases and attempts to update automatically
"""

import os
import sys
import json
import logging
from typing import Optional, Dict, Any
from datetime import datetime
import aiohttp
import asyncio

logger = logging.getLogger("update_checker")

GITHUB_REPO = "animesao/alfheimguide"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
VERSION_FILE = ".version"
CURRENT_VERSION_FILE = "version.txt"


class UpdateChecker:
    def __init__(self, current_version: str):
        self.current_version = current_version
        self.latest_version: Optional[str] = None
        self.update_available = False
        self.release_info: Optional[Dict[str, Any]] = None
    
    async def check_for_updates(self) -> bool:
        """Check if a new version is available on GitHub"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(GITHUB_API_URL, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.release_info = data
                        
                        # Get version from tag_name (e.g., "v2026.4.15" -> "2026.4.15")
                        tag_name = data.get("tag_name", "")
                        self.latest_version = tag_name.lstrip("v")
                        
                        # Compare versions
                        if self.latest_version and self._compare_versions(
                            self.latest_version, self.current_version
                        ):
                            self.update_available = True
                            logger.info(
                                f"🎉 New version available: {self.latest_version} (current: {self.current_version})"
                            )
                            return True
                        else:
                            logger.info(f"✅ Bot is up to date (v{self.current_version})")
                            return False
                    else:
                        logger.warning(f"Failed to check for updates: HTTP {response.status}")
                        return False
        except asyncio.TimeoutError:
            logger.warning("Update check timed out")
            return False
        except Exception as e:
            logger.error(f"Error checking for updates: {e}")
            return False
    
    def _compare_versions(self, latest: str, current: str) -> bool:
        """Compare version strings (format: YYYY.M.DD)"""
        try:
            # Split versions into parts
            latest_parts = [int(x) for x in latest.split(".")]
            current_parts = [int(x) for x in current.split(".")]
            
            # Pad with zeros if needed
            while len(latest_parts) < 3:
                latest_parts.append(0)
            while len(current_parts) < 3:
                current_parts.append(0)
            
            # Compare each part
            for l, c in zip(latest_parts, current_parts):
                if l > c:
                    return True
                elif l < c:
                    return False
            
            return False  # Versions are equal
        except Exception as e:
            logger.error(f"Error comparing versions: {e}")
            return False
    
    def get_update_info(self) -> Dict[str, Any]:
        """Get information about the available update"""
        if not self.release_info:
            return {}
        
        return {
            "version": self.latest_version,
            "name": self.release_info.get("name", ""),
            "body": self.release_info.get("body", ""),
            "published_at": self.release_info.get("published_at", ""),
            "html_url": self.release_info.get("html_url", ""),
            "download_url": self.release_info.get("zipball_url", ""),
        }
    
    async def _run_git(self, args: list[str]) -> tuple[int, str, str]:
        proc = await asyncio.create_subprocess_exec(
            "git", *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=30)
            return proc.returncode or 0, stdout.decode("utf-8", errors="replace"), stderr.decode("utf-8", errors="replace")
        except asyncio.TimeoutError:
            proc.kill()
            raise

    async def _run_pip(self, args: list[str]) -> tuple[int, str, str]:
        proc = await asyncio.create_subprocess_exec(
            sys.executable, "-m", "pip", *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=120)
            return proc.returncode or 0, stdout.decode("utf-8", errors="replace"), stderr.decode("utf-8", errors="replace")
        except asyncio.TimeoutError:
            proc.kill()
            raise

    async def attempt_auto_update(self) -> bool:
        """Attempt to automatically update the bot"""
        if not self.update_available:
            return False

        logger.info("🔄 Attempting automatic update...")

        try:
            code, out, err = await self._run_git(["rev-parse", "--git-dir"])
            if code != 0:
                logger.warning("Not a git repository, cannot auto-update")
                return False

            logger.info("📥 Fetching latest changes from GitHub...")
            code, out, err = await self._run_git(["fetch", "origin", "main"])
            if code != 0:
                logger.error(f"Failed to fetch: {err}")
                return False

            code, out, err = await self._run_git(["status", "--porcelain"])
            if out.strip():
                logger.warning("⚠️ Local changes detected, skipping auto-update")
                logger.info("Please commit or stash your changes before updating")
                return False

            logger.info("⬇️ Pulling latest changes...")
            code, out, err = await self._run_git(["pull", "origin", "main"])
            if code != 0:
                logger.error(f"Failed to pull: {err}")
                return False

            logger.info("📦 Installing dependencies...")
            code, out, err = await self._run_pip(["install", "-r", "requirements.txt", "--upgrade"])
            if code != 0:
                logger.warning(f"Dependency installation had issues: {err}")

            logger.info(f"✅ Successfully updated to v{self.latest_version}!")
            logger.info("🔄 Please restart the bot to apply changes")

            return True

        except asyncio.TimeoutError:
            logger.error("Update process timed out")
            return False
        except Exception as e:
            logger.error(f"Error during auto-update: {e}")
            return False


async def check_and_update(current_version: str, auto_update: bool = True) -> Optional[Dict[str, Any]]:
    """
    Check for updates and optionally attempt to auto-update
    
    Args:
        current_version: Current bot version
        auto_update: Whether to attempt automatic update
    
    Returns:
        Update info dict if update is available, None otherwise
    """
    checker = UpdateChecker(current_version)
    
    has_update = await checker.check_for_updates()
    
    if has_update:
        update_info = checker.get_update_info()
        
        if auto_update:
            success = await checker.attempt_auto_update()
            update_info["auto_update_success"] = success
        
        return update_info
    
    return None
