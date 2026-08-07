# Astral Moderation 7/19/2024 Changelog

## Summary
- Added the ability to automatically add a set role to a member upon joining the server
- Fixed warn capabilities
- Cleaned up code

**Bug Fixes**
- Fixed `/serverwarns` and `/warns` not working due to a missing function
- Fixed leave messages not being sent due to a mistyped variable
- Fixed warn capabilities, members will now be punished after reaching the warn threshold

## Commands

**Additions**
- Readded `/getjoinmessage` command
- Readded `/getleavemessage` command
- Added `/clearserverwarns` command
- Added `/unwarn` command
- Added `/setjoinrole` command

**Miscellaneous Changes**
- Changed how warns are stored to make entires easier to understand
- Changed `/warnpunishment` to have static options to ensure the punishment can be carried out
- Updated `/warn` to log the user who issued a warn
- Updated the minor announcement role value name from `minorannouncementrole` to `minorannouncement_role`
- Updated the testing and development role value name from `testingrole` to `testing_role`
- Updated `/addrole` to mention the role that was added
- Updated `/removerole` to mention the role that was removed
- Updated the confirmation message for `/setwarnpunishment` from "Punishment for crossing/meeting the warn threshold set to \<option>." to "Punishment for meeting the warn threshold set to \<option>".
- Updated and corrected command descriptions

## Functions

**Additions**
- Added `get_warn_info` function
- Added `apply_punishment` function

**Deletions**
- Removed `get_warn_count` function