# Astral Moderation 7/27/2024 Changelog

## Summary
- Added a command to view and set the GitHub repository
- Fixed `/purge` command
- Corrected mislabeled field in Flask
- Added a command to set moderator roles

**Bug Fixes**
- Fixed a bug where `/purge` deletes 1 more message than specified 

## Commands

**Additions**
- Added `/githubrepo` command
- Added `/setgihubrepo` command
- Added `/setcommandrole` command

## Functions

**Additions**
- Added `set_github_repo` function
- Added `get_github_repo` function
- Added `set_allowed_role` function

# Flask

## Summary
- Corrected mislabeled field in control panel

**Miscellaneous Changes**
- Changed "Disk Usage" to "Disk Space Used" in control panel