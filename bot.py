import os
import nextcord
import firebase_admin
from nextcord.ext import commands
from firebase_admin import credentials, firestore
from enum import Enum

pid = os.getpid()

with open('Flask/pid.txt', 'w') as file:
    file.write(str(pid))
print(f"PID ({pid}) stored in Flask/pid.txt")

# Set your bot's prefix
prefix = "/"

# Create a bot instance with a command prefix
intents = nextcord.Intents.all()
intents.messages = True
intents.message_content = True  # Enable MESSAGE_CONTENT intent
bot = commands.Bot(command_prefix=prefix, intents=intents)

# Initialize Firebase
cred = credentials.Certificate("firebase.json")
firebase_admin.initialize_app(cred)

# Initialize Firestore
db = firestore.client()

async def get_setting(setting_name):
    setting_ref = db.collection("command_configuration").document(setting_name)
    snapshot = setting_ref.get()
    if snapshot.exists:
        return snapshot.to_dict().get("value")
    else:
        return None  # Return None if the snapshot does not exist

async def set_setting(setting_name, setting_value):
    setting_ref = db.collection("command_configuration").document(setting_name)
    if isinstance(setting_value, bool):
        setting_ref.set({"value": setting_value})
    else:
        setting_ref.set({"value": setting_value})

async def get_channel_id(command_name, channel_name):
    """Get the channel ID from Firestore."""
    channel_ref = db.collection("channel_ids").document(command_name)
    try:
        snapshot = channel_ref.get()
        if snapshot.exists:
            return snapshot.to_dict().get(channel_name)
        else:
            return None
    except Exception as e:
        print(f"Error getting channel ID: {e}")
        return None

async def set_channel_id(command_name, channel_name, channel_id):
    """Set the channel ID in Firestore."""
    channel_ref = db.collection("channel_ids").document(command_name)
    try:
        channel_ref.set({channel_name: channel_id})
    except Exception as e:
        print(f"Error setting channel ID: {e}")

# Function to check what roles are allowed to run commands
async def get_allowed_roles():
    """Retrieve allowed roles from Firestore."""
    allowed_roles = {}

    try:
        doc_ref = db.collection('role_names').document('allowed_commands')
        doc = doc_ref.get()  # Remove 'await' from here
        if doc.exists:
            data = doc.to_dict()
            allowed_roles = {role_name: allow for role_name, allow in data.items()}  # Get the dictionary of allowed roles
    except Exception as e:
        print(f"Error fetching allowed roles: {e}")

    return allowed_roles

# Function to check the user for permissions to run the command
async def permission_check(ctx):
    """Check permissions for executing commands."""
    allowed_roles = await get_allowed_roles()  # Await the asynchronous operation

    # Get the names of the roles the user has
    user_role_names = [role.name for role in ctx.user.roles]

    # Check if any of the user's roles are allowed
    for role_name in user_role_names:
        if role_name in allowed_roles and allowed_roles[role_name]:
            return True

    # If none of the user's roles match the allowed roles or if the roles are not allowed
    await ctx.send("You do not have permission to use this command.")
    return False

# Function to get the bot token from Firestore
def get_bot_token():
    # Assuming the personal access token is stored in a document named 'bot_token'
    token_ref = db.collection("secrets").document("bot_token")
    token_doc = token_ref.get()
    if token_doc.exists:
        return token_doc.to_dict().get("token")
    else:
        return None

# Function to start the bot
def run_bot():
    # Get the personal access token from Firestore
    token = get_bot_token()
    if token:
        # Initialize the bot with the token
        bot.run(token)
    else:
        print("Failed to retrieve Firebase personal access token.")

# Function to retrieve command configuration from Firestore
async def get_command_config():
    settings_ref = db.collection("command_configuration").document("command_config")
    snapshot = settings_ref.get()
    if snapshot.exists:
        return snapshot.to_dict() or {}
    else:
        return {}

# Function to set command configuration in Firestore
async def set_command_config(config):
    settings_ref = db.collection("command_configuration").document("command_config")
    settings_ref.set(config)  # No need to use await here

# Function to get the warn count of a member
async def get_warn_count(member_id):
    """Get the warn count for a member."""
    warn_ref = db.collection("data").document("warns")
    snapshot = warn_ref.get()
    if snapshot.exists:
        data = snapshot.to_dict()
        if data and str(member_id) in data:
            return data[str(member_id)].get("warn_count", 0)
    return 0

# Function to get the server invite link
async def get_server_invite(ctx):
    """Get the server invite link from Firestore."""
    try:
        invite_ref = db.collection("secrets").document("server_invite")
        snapshot = invite_ref.get()
        if snapshot.exists:
            return snapshot.to_dict().get("pawers-smp")
        else:
            return None
    except Exception as e:
        print(f"Error getting server invite: {e}")
        return None

# Function to set the server invite link
async def set_server_invite(invite_data):
    """Set the server invite link in Firestore."""
    try:
        invite_ref = db.collection("secrets").document("server_invite")
        invite_ref.set({"pawers-smp": invite_data})
    except Exception as e:
        print(f"Error setting server invite: {e}")

# Function to get join message channel from Firestore
async def get_join_message_channel():
    """Get the join message channel from Firestore."""
    try:
        join_channel_ref = db.collection("command_configuration").document("join_channel")
        snapshot = join_channel_ref.get()
        if snapshot.exists:
            return snapshot.to_dict().get("channel_id")
    except Exception as e:
        print(f"Error getting join message channel: {e}")
    return None

# Function to set join message channel in Firestore
async def set_join_message_channel(channel_id):
    """Set the join message channel in Firestore."""
    try:
        join_channel_ref = db.collection("command_configuration").document("join_channel")
        join_channel_ref.set({"channel_id": channel_id})
    except Exception as e:
        print(f"Error setting join message channel: {e}")

# Function to get leave message channel from Firestore
async def get_leave_message_channel():
    """Get the leave message channel from Firestore."""
    try:
        leave_channel_ref = db.collection("command_configuration").document("leave_channel")
        snapshot = leave_channel_ref.get()
        if snapshot.exists:
            return snapshot.to_dict().get("channel_id")
    except Exception as e:
        print(f"Error getting leave message channel: {e}")
    return None

# Function to set leave message channel in Firestore
async def set_leave_message_channel(channel_id):
    """Set the leave message channel in Firestore."""
    try:
        leave_channel_ref = db.collection("command_configuration").document("leave_channel")
        leave_channel_ref.set({"channel_id": channel_id})
    except Exception as e:
        print(f"Error setting leave message channel: {e}")

# Function to get welcome message from Firestore
async def get_join_message():
    """Get the welcome message from Firestore."""
    try:
        welcome_ref = db.collection("command_configuration").document("join_message")
        snapshot = welcome_ref.get()
        if snapshot.exists:
            return snapshot.to_dict().get("message")
    except Exception as e:
        print(f"Error getting welcome message: {e}")
    return None

# Function to set welcome message in Firestore
async def set_join_message(message):
    """Set the welcome message in Firestore."""
    try:
        welcome_ref = db.collection("command_configuration").document("join_message")
        welcome_ref.set({"message": message})
    except Exception as e:
        print(f"Error setting welcome message: {e}")

# Function to get leave message from Firestore
async def get_leave_message():
    """Get the leave message from Firestore."""
    try:
        leave_ref = db.collection("command_configuration").document("leave_message")
        snapshot = leave_ref.get()
        if snapshot.exists:
            return snapshot.to_dict().get("message")
    except Exception as e:
        print(f"Error getting leave message: {e}")
    return None

# Function to set leave message in Firestore
async def set_leave_message(message):
    """Set the leave message in Firestore."""
    try:
        leave_ref = db.collection("command_configuration").document("leave_message")
        leave_ref.set({"message": message})
    except Exception as e:
        print(f"Error setting leave message: {e}")

# Event listener: Send join and leave messages
@bot.event
async def on_member_join(member: nextcord.Member):
    join_message_channel_id = await get_join_message_channel()
    if join_message_channel_id:
        join_message_channel = bot.get_channel(join_message_channel_id)
        if join_message_channel:
            join_message = await get_join_message()
            if join_message:
                await join_message_channel.send(f"{member.mention} {join_message}")

@bot.event
async def on_member_remove(member: nextcord.Member):
    leave_message_channel_id = await get_leave_message_channel()
    if leave_message_channel_id:
        leave_message_channel = bot.get_channel(leave_message_channel_id)
        if leave_message_channel:
            leave_message = await get_leave_message()
            if leave_message:
                await leave_message_channel.send(f"{member.mention} {leave_message}")

# Function to log ran commands
async def log_events(ctx, message):
    log_channel_id = await get_channel_id(command_name='logging', channel_name='modlogs')
    if log_channel_id:
        log_channel = bot.get_channel(int(log_channel_id))
        if log_channel:
            log_message = f'Executed: <@{ctx.user.id}> | {message}'  # Include user's display name, action, and channel name
            await log_channel.send(log_message)
        else:
            print("Error: Log channel not found")
    else:
        print("Error: Logging channel ID not set")
class ApplicationCommandOptionType(Enum):
    STRING = 3

# Event: When the bot is ready
@bot.event
async def on_ready():
    print(f'{bot.user} is now online')
    await bot.change_presence(status=nextcord.Status.online)

# Command: Ban a member
@bot.slash_command(description="Ban a member from the server.")
async def ban(ctx, member: nextcord.Member, *, reason=None):
    """Ban a member from the server."""
    if await permission_check(ctx):
        if ctx.guild.get_member(member.id):  # Check if the user is still a member of the server
            if ctx.guild.me.guild_permissions.ban_members:  # Check if the bot has permission to ban members
                try:
                    # Ban the member
                    await member.ban(reason=reason)
                    await ctx.send(f'{member.mention} has been banned.')

                    # Log the ban event
                    await log_events(ctx, f'{member.mention} has been banned for {reason}.')

                    # Store ban information in Firebase
                    try:
                        bans_ref = db.collection("data").document("bans")
                        member_info = {
                            member.display_name: {
                                "user_id": str(member.id),
                                "username": member.name,
                                "ban_reason": reason
                            }
                        }
                        bans_ref.set(member_info, merge=True)
                    except Exception as e:
                        print(f"Error storing ban information: {e}")
                except nextcord.Forbidden:
                    await ctx.send("I don't have permission to ban members.")
            else:
                await ctx.send("I don't have permission to ban members.")
        else:
            await ctx.send("The user is not a member of this server.")

# Command: Unban a member
@bot.slash_command(description="Unban a member from the server.")
async def unban(ctx, *, member):
    """Unban a member from the server."""
    if await permission_check(ctx):
        try:
            bans_ref = db.collection("data").document("bans")
            bans_data = bans_ref.get().to_dict()    
            if bans_data:
                # Check if the member parameter contains a discriminator
                if "#" in member:
                    member_name, member_discriminator = member.split('#')

                    for ban_id, ban_info in bans_data.items():
                        user_name = ban_info.get("username")
                        user_discriminator = ban_info.get("discriminator")
                        if user_name == member_name and user_discriminator == member_discriminator:
                            user_id = ban_info.get("user_id")
                            user = await bot.fetch_user(user_id)
                            if user:
                                await ctx.guild.unban(user)
                                await ctx.send(f'{user.mention} has been unbanned.')
                                await log_events(ctx, f'{user.mention} has been unbanned.')
                                # Delete the ban entry from Firebase
                                bans_ref.update({ban_id: firestore.DELETE_FIELD})
                                return

                else:
                    # If no discriminator is provided, search for the member using only the name
                    for ban_id, ban_info in bans_data.items():
                        user_name = ban_info.get("username")
                        if user_name == member:
                            user_id = ban_info.get("user_id")
                            user = await bot.fetch_user(user_id)
                            if user:
                                await ctx.guild.unban(user)
                                await ctx.send(f'{user.mention} has been unbanned.')
                                await log_events(ctx, f'{user.mention} has been unbanned.')
                                # Delete the ban entry from the map field in Firebase
                                bans_ref.update({ban_id: firestore.DELETE_FIELD})
                                return

            await ctx.send("User not found in the ban list.")
        except Exception as e:
            print(f"Error fetching ban information: {e}")

# Command: Kick a member
@bot.slash_command(description="Kick a member from the server.")
async def kick(ctx, member: nextcord.Member, *, reason=None):
    """Kick a member from the server."""
    if await permission_check(ctx):
        await member.kick(reason=reason)
        await ctx.send(f'{member.mention} has been kicked.')
        await log_events(ctx, f'{member.mention} has been kicked for {reason}.')

# Command: Warn a member
@bot.slash_command(description="Warn a member.")
async def warn(ctx, member: nextcord.Member, reason: str):
    """Warn a member."""
    if await permission_check(ctx):
        warn_ref = db.collection("data").document("warns")
        member_id = str(member.id)
        warns_data = warn_ref.get()

        if warns_data.exists and member_id in warns_data.to_dict():
            member_warns = warns_data.to_dict()[member_id].get("warns", [])
            warn_count = len(member_warns) + 1
            member_warns.append({"reason": reason, "warn_count": warn_count, "username": member.name, "user_id": member.id})
        else:
            warn_count = 1
            member_warns = [{"reason": reason, "warn_count": warn_count, "username": member.name, "user_id": member.id}]

        warn_ref.set({member_id: {"warns": member_warns}}, merge=True)
        warn_ref.update({f"{member_id}.warn_count": warn_count})

        await ctx.send(f'{member.mention} has been warned for {reason}.')
        await log_events(ctx, f'{member.mention} has been warned for {reason}.')

# Command: View all warnings for the server
@bot.slash_command(description="View all warnings for the server.")
async def serverwarns(ctx):
    """View all warnings for the server."""
    if await permission_check(ctx, "serverwarns"):
        server_warns = await get_server_warns(ctx.guild)  # noqa: F821
        await ctx.send(server_warns)

# Command: View warns for a member
@bot.slash_command(description="View warns for a member.")
async def warns(ctx, member: nextcord.Member):
    """View warns for a member."""
    if await permission_check(ctx):
        member_warns = await get_member_warns(member)  # noqa: F821
        await ctx.send(member_warns)

# Command: Clear warns for a member
@bot.slash_command(description="Clear warns for a member.")
async def clearwarns(ctx, member: nextcord.Member):
    """Clear warns for a member."""
    if await permission_check(ctx):
        await clear_member_warns(member)  # noqa: F821
        await ctx.send(f'Warns cleared for {member.mention}.')
        await log_events(ctx, f'Warns cleared for {member.mention}.')

# Command: Set warn threshold
@bot.slash_command(description="Set the warn threshold.")
async def setwarnthreshold(ctx, threshold: int):
    """Set the warn threshold."""
    if await permission_check(ctx):
        await set_setting("warn_threshold", threshold)
        await ctx.send(f"Warn threshold set to {threshold}.")

# Command: Set punishment for crossing or meeting the warn threshold
@bot.slash_command(description="Set the punishment for crossing/meeting the warn threshold. Options: mute, kick, ban")
async def setwarnpunishment(ctx, action: str):
    """Set the punishment for crossing/meeting the warn threshold."""
    if await permission_check(ctx):
        await set_setting("punishment_action", action.lower())
        await ctx.send(f"Punishment for crossing/meeting the warn threshold set to {action}.")

# Command: Mute a member
@bot.slash_command(description="Mute a member to prevent them from sending messages.")
async def mute(ctx, member: nextcord.Member):
    """Mute a member to prevent them from sending messages."""
    if await permission_check(ctx):
        await member.add_roles(ctx.guild.get_role(get_muted_role_id()))  # noqa: F821
        await ctx.send(f'{member.mention} has been muted.')
        await log_events(ctx, f'{member.mention} has been muted.')

# Command: Unmute a member
@bot.slash_command(description="Unmute a member to allow them to send messages again.")
async def unmute(ctx, member: nextcord.Member):
    """Unmute a member to allow them to send messages again."""
    if await permission_check(ctx):
        await member.remove_roles(ctx.guild.get_role(get_muted_role_id()))  # noqa: F821
        await ctx.send(f'{member.mention} has been unmuted.')
        await log_events(ctx, f'{member.mention} has been unmuted.')

# Command: Lock a channel
@bot.slash_command(description="Lock a channel to prevent members from sending messages.")
async def lock(ctx):
    """Lock a channel to prevent members from sending messages."""
    if await permission_check(ctx):
        everyone_role = ctx.guild.default_role
        channel_permissions = ctx.channel.overwrites_for(everyone_role)
        channel_permissions.send_messages = False
        await ctx.channel.set_permissions(everyone_role, overwrite=channel_permissions)
        await ctx.send(f'Locked {ctx.channel.mention}')
        await log_events(ctx, f'Locked {ctx.channel.mention}')

# Command: Unlock a channel
@bot.slash_command(description="Unlock a previously locked channel.")
async def unlock(ctx):
    """Unlock a previously locked channel."""
    if await permission_check(ctx):
        everyone_role = ctx.guild.default_role
        channel_permissions = ctx.channel.overwrites_for(everyone_role)
        channel_permissions.send_messages = True
        await ctx.channel.set_permissions(everyone_role, overwrite=channel_permissions)
        await ctx.send(f'Unlocked {ctx.channel.mention}')
        await log_events(ctx, f'Unlocked {ctx.channel.mention}')

# Command: Purge messages from a channel
@bot.slash_command(description="Purge messages from a channel.")
async def purge(ctx, amount: int, member: nextcord.Member = None):
    """Purge messages from a channel."""
    if await permission_check(ctx):
        if member:
            check = lambda m: m.user == member
            deleted = await ctx.channel.purge(limit=amount, check=check)
            await ctx.send(f'{len(deleted)} messages from {member.mention} have been purged from the channel.')
            await log_events(ctx, f'{len(deleted)} messages from {member.mention} have been purged from {ctx.channel.mention}.')
        else:
            deleted = await ctx.channel.purge(limit=amount + 1)
            await ctx.send(f'{len(deleted) - 1} messages have been purged from the channel.')
            await log_events(ctx, f'{len(deleted) - 1} messages have been purged from {ctx.channel.mention}.')

# Command: Add role to a member
@bot.slash_command(description="Add a role to a member.")
async def addrole(ctx, member: nextcord.Member, role: nextcord.Role):
    """Add a role to a member."""
    if await permission_check(ctx):
        await member.add_roles(role)
        await ctx.send(f'{member.mention} has been given the {role.name} role.')
        await log_events(ctx, f'{member.mention} has been given the {role.name} role.')

# Command: Remove role from a member
@bot.slash_command(description="Remove a role from a member.")
async def removerole(ctx, member: nextcord.Member, role: nextcord.Role):
    """Remove a role from a member."""
    if await permission_check(ctx):
        await member.remove_roles(role)
        await ctx.send(f'{member.mention} no longer has the {role.name} role.')
        await log_events(ctx, f'{member.mention} no longer has the {role.name} role.')

# Command: Set or toggle the logging channel.
@bot.slash_command(description="Set or toggle the logging channel.")
async def logging(ctx, channel: nextcord.TextChannel = None, toggle: bool = None):
    """Set or toggle the logging channel."""
    if await permission_check(ctx):
        if channel:
            await set_channel_id("logging", channel.name, channel.id)
            await ctx.send(f"Logging channel set to {channel.mention}.")
        elif toggle is not None:
            await set_setting("logging_toggle", toggle)
            status = "enabled" if toggle else "disabled"
            await ctx.send(f"Logging is now {status}.")
        else:
            await ctx.send("Invalid command usage.")

# Command: Make an announcement.
@bot.slash_command(description="Make an announcement.")
async def announce(ctx, message: str, ping_everyone: bool = False):
    """Make an announcement."""
    if await permission_check(ctx):
        announcement_channel_id = await get_channel_id("setannouncementchannel", "announcements")
        if announcement_channel_id:
            announcement_channel = bot.get_channel(int(announcement_channel_id))
            if ping_everyone:
                await announcement_channel.send("@everyone " + message)
                await ctx.send("Announcement made successfully")
            else:
                await announcement_channel.send(message)
                await ctx.send("Announcement made successfully")
        else:
            await ctx.send("Announcement channel is not set. Use /setannouncementchannel command to set it.")

# Command: Set the announcement channel.
@bot.slash_command(description="Set the announcement channel.")
async def setannouncementchannel(ctx, channel: nextcord.TextChannel):
    """Set the announcement channel."""
    if await permission_check(ctx):
        await set_channel_id("setannouncementchannel", channel.name, channel.id)
        await ctx.send(f"Announcement channel set to {channel.mention}.")

# Command: Get server invite link
@bot.slash_command(description="Get server invite link")
async def invite(ctx):
    """Get server invite link"""
    server_invite = await get_server_invite(ctx)
    await ctx.send(server_invite)

# Command: Set the server invite link
@bot.slash_command(description="Set the server invite link")
async def setinvite(ctx, invite: str):
    """Set the server invite link"""
    if await permission_check(ctx):
        try:
            await set_server_invite(invite)
            await ctx.send("Server invite link has been set")
        except Exception as e:
            await ctx.send(f"Error setting server invite link: {str(e)}")

# Command: Set welcome message
@bot.slash_command(description="Set the welcome message.")
async def setjoinmessage(ctx, message: str):
    """Set the welcome message."""
    if await permission_check(ctx):
        await set_join_message(message)
        await ctx.send("Welcome message set successfully.")

# Command: Set leave message
@bot.slash_command(description="Set the leave message.")
async def setleavemessage(ctx, message: str):
    """Set the leave message."""
    if await permission_check(ctx):
        await set_leave_message(message)
        await ctx.send("Leave message set successfully.")

# Command: Set join message channel
@bot.slash_command(description="Set the channel for sending join messages.")
async def setjoinmessagechannel(ctx, channel: nextcord.TextChannel):
    """Set the channel for sending join messages."""
    if await permission_check(ctx):
        await set_join_message_channel(channel.id)
        await ctx.send(f"Join message channel set to {channel.mention}.")

# Command: Set leave message channel
@bot.slash_command(description="Set the channel for sending leave messages.")
async def setleavemeesagechannel(ctx, channel: nextcord.TextChannel):
    """Set the channel for sending leave messages."""
    if await permission_check(ctx):
        await set_leave_message_channel(channel.id)
        await ctx.send(f"Leave message channel set to {channel.mention}.")

# Command: Show help information.
@bot.slash_command(description="Show help information.")
async def help(ctx):
    """Show help information."""
    await ctx.send(
"""**Moderation Commands:**
- `/ban` | Ban a member from the server.
- `/unban` | Unban a member from the server.
- `/kick` | Kick a member from the server.
- `/warn` | Warn a member.
- `/serverwarns` | View all warnings for the server.
- `/warns` | View warns for a member.
- `/clearwarns` | Clear warns for a member.
- `/mute` | Mute a member to prevent them from sending messages.
- `/unmute` | Unmute a member to allow them to send messages again.
- `/lock` | Lock a channel to prevent members from sending messages.
- `/unlock` | Unlock a previously locked channel.
- `/announce` | Make an announcement.

**Settings and Configuration Commands**
- `/setwarnthreshold` | Set the warn threshold.
- `/setwarnpunishment` | Set the punishment for crossing/meeting the warn threshold.
- `/logging` | Set or toggle the logging channel.
- `/setannouncementchannel` | Set the announcement channel.
- `/setinvite` | Set the server invite link.
- `/setjoinmessage` | Set the welcome message.
- `/setleavemessage` | Set the leave message.
- `/setjoinmessagechannel` | Set the channel for sending join messages.
- `/setleavemeesagechannel` | Set the channel for sending leave messages.

**Role Management Commands:**
- `/addrole` | Add a role to a member.
- `/removerole` | Remove a role from a member.

**Utility Commands:**
- `/purge` | Purge messages from a channel.
- `/invite` | Get server invite link.

**General Commands:**
- `/help` | Show help information.""")

# Call the run_bot function to start the bot
if __name__ == "__main__":
    run_bot()