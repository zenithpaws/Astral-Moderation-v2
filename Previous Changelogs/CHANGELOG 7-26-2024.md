# Astral Moderation Flask Front & Backend 7/26/2024 Changelog

## Summary
- Integrated Firebase data into the control panel
- Implemented system status monitoring
- Updated endpoint functions for better error handling and data processing
- Overhauled control panel interface
- Removed virtual environments

---

## UI Updates

**HTML Structure Changes**
- Added forms for each new endpoint action
- Improved layout and readability of the control panel interface

## Functions

**Additions**
- Added `get_network_upload_rate` and `get_network_download_rate` functions for network monitoring

## Endpoints

**Additions**
- Added `firebasedata` endpoint to fetch and display Firebase settings, warnings, and bans
- Added `systemstatus` endpoint to monitor and display system performance metrics

**Replacements**
- Removed `gitfetch` endpoint and replaced it with `gitpull`

**Miscellaneous Changes**
- Adjusted `start`, `stop`, and `restart` endpoints for improved functionality
- Improved error handling and logging for better diagnostics