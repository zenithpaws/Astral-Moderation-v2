# Astral Moderation 7/13/2024 Changelog

## Summary
- Added the ability to ping a role for minor announcements when making announcements
- Optimized functions making the bot respond faster to commands
- Made Firebase data easier to understand and more organized

**Bug Fixes**
- Fixed mute capability
- Fixed logging capability

---
## Commands

**Additions**
- Added `/setmuterole` command
- Added `/setminorannouncementrole` command

**Miscellaneous Changes**
- Changed `/setjoinmessagechannel` to `/setjoinchannel`
- Changed `/setleavemessagechannel` to `/setleavechannel`

---
## Functions

**Additions**
- Added `set_channel_id` function
- Added `get_channel_id` function
- Added `set_role_id` function
- Added `get_role_id` function

**Replacements**
- Replaced `set_join_message_channel` with `set_channel_id`
- Replaced `get_join_message_channel` with `get_channel_id`
- Replaced `set_leave_message_channel` with `set_channel_id`
- Replaced `get_leave_message_channel` with `get_channel_id`
- Replaced `get_muted_role_id` with `get_role_id`
