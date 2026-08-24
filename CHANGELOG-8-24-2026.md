Here is the changelog for all the awesome work we did today! :3

# Astral Moderation 8/24/2026 Changelog

## Summary

* Integrated a lightweight `aiohttp` web server for Railway container health checks and Nightbell monitoring
* Implemented a comprehensive birthday tracking and announcement system using Firebase and UTC timestamps
* Added an automated background task loop to send birthday announcements exactly at midnight UTC
* Added interaction deferrals to database-heavy commands to prevent Discord timeout errors
* Updated existing commands to enforce the custom permission system

## Commands

**Additions**

* Added `/birthday` command to allow users to save their birth month, day, and year as a native Timestamp to Firestore
* Added `/birthdays` command to list members celebrating today and display a chronologically sorted calendar of all stored server birthdays

**Modifications**

* Updated `/banlist` to include the `permission_check(ctx)` validation
* Updated `/birthday` to remove permission checks so all users can access it
* Updated `/birthday` and `/birthdays` to use `await ctx.response.defer()` to prevent 3-second application non-response errors

## Functions & Architecture

**Additions**

* Added `health_check(request)` endpoint to return a `200 OK` HTTP status for uptime monitors
* Added `start_web_server()` function to initialize the `aiohttp` server on Railway's assigned `$PORT`
* Added `check_birthdays()` background task loop to check Firebase and send announcements daily at `00:00 UTC`

**Modifications**

* Updated `on_ready()` event to trigger both `start_web_server()` and `check_birthdays.start()` upon bot boot
* Updated `commands.Bot()` initialization to include `default_guild_ids` for rapid slash command population during development
