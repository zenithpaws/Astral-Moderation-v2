import nextcord
import firebase_admin
from nextcord.ext import commands
from firebase_admin import credentials, firestore
from enum import Enum

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
        
async def get_allowed_roles():
    """Retrieve allowed roles from Firestore."""
    allowed_roles = {}

    try:
        doc_ref = db.collection('role_ids').document('commandpermissions')
        doc = doc_ref.get()  # Remove 'await' from here
        if doc.exists:
            data = doc.to_dict()
            allowed_roles = data.get('allowed', {})  # Get the dictionary of allowed roles
    except Exception as e:
        print(f"Error fetching allowed roles: {e}")

    return allowed_roles

async def commandpermissions(ctx):
    """Check permissions for executing commands."""
    allowed_roles = await get_allowed_roles()  # Await the asynchronous operation

    # Get the IDs of the roles the user has
    user_role_ids = [role.id for role in ctx.user.roles]

    # Check if the user has administrator permissions
    if ctx.user.guild_permissions.administrator:
        return True

    # Check if any of the user's roles are allowed
    for role_id in user_role_ids:
        if role_id in allowed_roles and allowed_roles[role_id]:
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

async def get_warn_count(member_id):
    """Get the warn count for a member."""
    warn_ref = db.collection("data").document("warns")
    snapshot = warn_ref.get()
    if snapshot.exists:
        data = snapshot.to_dict()
        if data and str(member_id) in data:
            return data[str(member_id)].get("warn_count", 0)
    return 0

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

async def set_server_invite(invite_data):
    """Set the server invite link in Firestore."""
    try:
        invite_ref = db.collection("secrets").document("server_invite")
        invite_ref.set({"pawers-smp": invite_data})
    except Exception as e:
        print(f"Error setting server invite: {e}")


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

## Command: Ban a member
@bot.slash_command(description="Ban a member from the server.")
async def ban(ctx, member: nextcord.Member, *, reason=None):
    """Ban a member from the server."""
    if await commandpermissions(ctx):
        await member.ban(reason=reason)
        await ctx.send(f'{member.mention} has been banned.')
        await log_events(ctx, f'{member.mention} has been banned for {reason}.')

# Command: Unban a member
@bot.slash_command(description="Unban a member from the server.")
async def unban(ctx, *, member):
    """Unban a member from the server."""
    if await commandpermissions(ctx):
        banned_users = await ctx.guild.bans()
        member_name, member_discriminator = member.split('#')

        for ban_entry in banned_users:
            user = ban_entry.user
            if (user.name, user.discriminator) == (member_name, member_discriminator):
                await ctx.guild.unban(user)
                await ctx.send(f'{user.mention} has been unbanned.')
                await log_events(ctx, f'{user.mention} has been unbanned.')
                return

# Command: Kick a member
@bot.slash_command(description="Kick a member from the server.")
async def kick(ctx, member: nextcord.Member, *, reason=None):
    """Kick a member from the server."""
    if await commandpermissions(ctx):
        await member.kick(reason=reason)
        await ctx.send(f'{member.mention} has been kicked.')
        await log_events(ctx, f'{member.mention} has been kicked for {reason}.')

# Command: Warn a member
@bot.slash_command(description="Warn a member.")
async def warn(ctx, member: nextcord.Member, reason: str):
    """Warn a member."""
    if await commandpermissions(ctx):
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
    if await commandpermissions(ctx, "serverwarns"):
        server_warns = await get_server_warns(ctx.guild)  # noqa: F821
        await ctx.send(server_warns)

# Command: View warns for a member
@bot.slash_command(description="View warns for a member.")
async def warns(ctx, member: nextcord.Member):
    """View warns for a member."""
    if await commandpermissions(ctx):
        member_warns = await get_member_warns(member)  # noqa: F821
        await ctx.send(member_warns)

# Command: Clear warns for a member
@bot.slash_command(description="Clear warns for a member.")
async def clearwarnings(ctx, member: nextcord.Member):
    """Clear warns for a member."""
    if await commandpermissions(ctx):
        await clear_member_warns(member)  # noqa: F821
        await ctx.send(f'Warns cleared for {member.mention}.')
        await log_events(ctx, f'Warns cleared for {member.mention}.')

# Command: Set warn threshold
@bot.slash_command(description="Set the warn threshold.")
async def setwarnthreshold(ctx, threshold: int):
    """Set the warn threshold."""
    if await commandpermissions(ctx):
        await set_setting("warn_threshold", threshold)
        await ctx.send(f"Warn threshold set to {threshold}.")

# Command: Set punishment for crossing or meeting the warn threshold
@bot.slash_command(description="Set the punishment for crossing/meeting the warn threshold. Options: mute, kick, ban")
async def setwarnpunishment(ctx, action: str):
    """Set the punishment for crossing/meeting the warn threshold."""
    if await commandpermissions(ctx):
        await set_setting("punishment_action", action.lower())
        await ctx.send(f"Punishment for crossing/meeting the warn threshold set to {action}.")

# Command: Mute a member
@bot.slash_command(description="Mute a member to prevent them from sending messages.")
async def mute(ctx, member: nextcord.Member):
    """Mute a member to prevent them from sending messages."""
    if await commandpermissions(ctx):
        await member.add_roles(ctx.guild.get_role(get_muted_role_id()))  # noqa: F821
        await ctx.send(f'{member.mention} has been muted.')
        await log_events(ctx, f'{member.mention} has been muted.')

# Command: Unmute a member
@bot.slash_command(description="Unmute a member to allow them to send messages again.")
async def unmute(ctx, member: nextcord.Member):
    """Unmute a member to allow them to send messages again."""
    if await commandpermissions(ctx):
        await member.remove_roles(ctx.guild.get_role(get_muted_role_id()))  # noqa: F821
        await ctx.send(f'{member.mention} has been unmuted.')
        await log_events(ctx, f'{member.mention} has been unmuted.')

# Command: Lock a channel
@bot.slash_command(description="Lock a channel to prevent members from sending messages.")
async def lock(ctx):
    """Lock a channel to prevent members from sending messages."""
    if await commandpermissions(ctx):
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
    if await commandpermissions(ctx):
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
    if await commandpermissions(ctx):
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
    if await commandpermissions(ctx):
        await member.add_roles(role)
        await ctx.send(f'{member.mention} has been given the {role.name} role.')
        await log_events(ctx, f'{member.mention} has been given the {role.name} role.')

# Command: Remove role from a member
@bot.slash_command(description="Remove a role from a member.")
async def removerole(ctx, member: nextcord.Member, role: nextcord.Role):
    """Remove a role from a member."""
    if await commandpermissions(ctx):
        await member.remove_roles(role)
        await ctx.send(f'{member.mention} no longer has the {role.name} role.')
        await log_events(ctx, f'{member.mention} no longer has the {role.name} role.')

# Command: Set or toggle the logging channel.
@bot.slash_command(description="Set or toggle the logging channel.")
async def logging(ctx, channel: nextcord.TextChannel = None, toggle: bool = None):
    """Set or toggle the logging channel."""
    if await commandpermissions(ctx):
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
    if await commandpermissions(ctx):
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
    if await commandpermissions(ctx):
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
    if await commandpermissions(ctx):
        try:
            await set_server_invite(invite)
            await ctx.send("Server invite link has been set")
        except Exception as e:
            await ctx.send(f"Error setting server invite link: {str(e)}")
            


# Command: Show help information.
@bot.slash_command(description="Show help information.")
async def help(ctx):
    """Show help information."""
    await ctx.send(
"""**Moderation Commands:**
- `ban` | Ban a member from the server.
- `unban` | Unban a member from the server.
- `kick` | Kick a member from the server.
- `warn` | Warn a member.
- `serverwarns` | View all warnings for the server.
- `warns` | View warns for a member.
- `clearwarnings` | Clear warns for a member.
- `mute` | Mute a member to prevent them from sending messages.
- `unmute` | Unmute a member to allow them to send messages again.
- `lock` | Lock a channel to prevent members from sending messages.
- `unlock` | Unlock a previously locked channel.
- `announce` | Make an announcement.

**Settings and Configuration Commands**
- `setwarnthreshold` | Set the warn threshold.
- `setwarnpunishment` | Set the punishment for crossing/meeting the warn threshold.
- `logging` | Set or toggle the logging channel.
- `setannouncementchannel` | Set the announcement channel.
- `setinvite` | Set the server invite link.

**Role Management Commands:**
- `addrole` | Add a role to a member.
- `removerole` | Remove a role from a member.

**Utility Commands:**
- `purge` | Purge messages from a channel.
- `invite` | Get server invite link.

**General Commands:**
- `help` | Show help information.""")
    
# Call the run_bot function to start the bot
if __name__ == "__main__":
    run_bot()