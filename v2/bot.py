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
cred = credentials.Certificate("ryzen-moderation-firebase-adminsdk.json")
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
    allowed_roles = []

    try:
        doc_ref = db.collection('role_ids').document('commandpermissions')
        doc = await doc_ref.get()  # Await the asynchronous operation
        if doc.exists:
            data = doc.to_dict()
            allowed_roles = data.get('allowed', {}).values()  # Extract role IDs from the map
    except Exception as e:
        print(f"Error fetching allowed roles: {e}")

    return allowed_roles

async def commandpermissions(ctx, command_name):
    """Check permissions for executing commands."""
    allowed_roles = await get_allowed_roles()  # Await the asynchronous operation

    if ctx.user.guild_permissions.administrator:
        # Only administrators can modify the allowed roles
        await ctx.send("You are not allowed to use this command.")
        return False

    if any(role.id in allowed_roles for role in ctx.user.roles):
        # User is allowed to modify the allowed roles
        await ctx.send("You are allowed to use this command.")
        return True
    else:
        await ctx.send("You do not have permission to use this command.")
        return False
        
# Function to get the bot token from Firestore
async def get_bot_token():
    bot_token_ref = db.collection("secrets").document("bot_token")
    snapshot = await bot_token_ref.get()  # Await the asynchronous operation
    if snapshot.exists:
        return snapshot.to_dict().get("value")
    else:
        raise ValueError("Bot token not found in Firestore.")


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

async def log_events(ctx, action, message):
    log_channel_id = await get_channel_id(command_name='logging',channel_name='modlogs')
    if log_channel_id:
        log_channel = bot.get_channel(int(log_channel_id))
        if log_channel:
            user_display_name = ctx.user.display_name if isinstance(ctx, nextcord.Interaction) else ctx.user.display_name
            log_message = f'{user_display_name} | {message}'  # Include action and user's display name
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
    await bot.change_presence(status=nextcord.Status.do_not_disturb)

## Command: Ban a member
@bot.slash_command(description="Ban a member from the server.")
async def ban(ctx, member: nextcord.Member, *, reason=None):
    """Ban a member from the server."""
    if await commandpermissions(ctx, "ban"):
        await member.ban(reason=reason)
        await ctx.send(f'{member.mention} has been banned.')
        await log_events(ctx, "Ban", f'{member.mention} has been banned for {reason}.')

# Command: Unban a member
@bot.slash_command(description="Unban a member from the server.")
async def unban(ctx, *, member):
    """Unban a member from the server."""
    if await commandpermissions(ctx, "unban"):
        banned_users = await ctx.guild.bans()
        member_name, member_discriminator = member.split('#')

        for ban_entry in banned_users:
            user = ban_entry.user
            if (user.name, user.discriminator) == (member_name, member_discriminator):
                await ctx.guild.unban(user)
                await ctx.send(f'{user.mention} has been unbanned.')
                await log_events(ctx, "Unban", f'{user.mention} has been unbanned.')
                return

# Command: Kick a member
@bot.slash_command(description="Kick a member from the server.")
async def kick(ctx, member: nextcord.Member, *, reason=None):
    """Kick a member from the server."""
    if await commandpermissions(ctx, "kick"):
        await member.kick(reason=reason)
        await ctx.send(f'{member.mention} has been kicked.')
        await log_events(ctx, "Kick", f'{member.mention} has been kicked for {reason}.')

# Command: Warn a member
@bot.slash_command(description="Warn a member.")
async def warn(ctx, member: nextcord.Member, reason: str):
    """Warn a member."""
    if await commandpermissions(ctx, "warn"):
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
        await log_events(ctx, "Warn", f'{member.mention} has been warned for {reason}.')

# Command: View all warnings for the server
@bot.slash_command(description="View all warnings for the server.")
async def serverwarns(ctx):
    """View all warnings for the server."""
    if await commandpermissions(ctx, "serverwarns"):
        server_warns = await get_server_warns(ctx.guild)
        await ctx.send(server_warns)

# Command: View warns for a member
@bot.slash_command(description="View warns for a member.")
async def warns(ctx, member: nextcord.Member):
    """View warns for a member."""
    if await commandpermissions(ctx, "warns"):
        member_warns = await get_member_warns(member)
        await ctx.send(member_warns)

# Command: Clear warns for a member
@bot.slash_command(description="Clear warns for a member.")
async def clearwarnings(ctx, member: nextcord.Member):
    """Clear warns for a member."""
    if await commandpermissions(ctx, "clearwarnings"):
        await clear_member_warns(member)
        await ctx.send(f'Warns cleared for {member.mention}.')
        await log_events(ctx, "Clear Warns", f'Warns cleared for {member.mention}.')

# Command: Set warn threshold
@bot.slash_command(description="Set the warn threshold.")
async def setwarnthreshold(ctx, threshold: int):
    """Set the warn threshold."""
    if await commandpermissions(ctx, "setwarnthreshold"):
        await set_setting("warn_threshold", threshold)
        await ctx.send(f"Warn threshold set to {threshold}.")

# Command: Set punishment for crossing or meeting the warn threshold
@bot.slash_command(description="Set the punishment for crossing/meeting the warn threshold. Options: mute, kick, ban")
async def setwarnpunishment(ctx, action: str):
    """Set the punishment for crossing/meeting the warn threshold."""
    if await commandpermissions(ctx, "setwarnpunishment"):
        await set_setting("punishment_action", action.lower())
        await ctx.send(f"Punishment for crossing/meeting the warn threshold set to {action}.")

# Command: Mute a member
@bot.slash_command(description="Mute a member to prevent them from sending messages.")
async def mute(ctx, member: nextcord.Member):
    """Mute a member to prevent them from sending messages."""
    if await commandpermissions(ctx, "mute"):
        await member.add_roles(ctx.guild.get_role(get_muted_role_id()))
        await ctx.send(f'{member.mention} has been muted.')
        await log_events(ctx, "Mute", f'{member.mention} has been muted.')

# Command: Unmute a member
@bot.slash_command(description="Unmute a member to allow them to send messages again.")
async def unmute(ctx, member: nextcord.Member):
    """Unmute a member to allow them to send messages again."""
    if await commandpermissions(ctx, "unmute"):
        await member.remove_roles(ctx.guild.get_role(get_muted_role_id()))
        await ctx.send(f'{member.mention} has been unmuted.')
        await log_events(ctx, "Unmute", f'{member.mention} has been unmuted.')

# Command: Lock a channel
@bot.slash_command(description="Lock a channel to prevent members from sending messages.")
async def lock(ctx):
    """Lock a channel to prevent members from sending messages."""
    if await commandpermissions(ctx, "lock"):
        everyone_role = ctx.guild.default_role
        channel_permissions = ctx.channel.overwrites_for(everyone_role)
        channel_permissions.send_messages = False
        await ctx.channel.set_permissions(everyone_role, overwrite=channel_permissions)
        await ctx.send('This channel has been locked.')
        await log_events(ctx, "Lock", f'{ctx.channel.mention} has been locked.')

# Command: Unlock a channel
@bot.slash_command(description="Unlock a previously locked channel.")
async def unlock(ctx):
    """Unlock a previously locked channel."""
    if await commandpermissions(ctx, "unlock"):
        everyone_role = ctx.guild.default_role
        channel_permissions = ctx.channel.overwrites_for(everyone_role)
        channel_permissions.send_messages = True
        await ctx.channel.set_permissions(everyone_role, overwrite=channel_permissions)
        await ctx.send('This channel has been unlocked.')
        await log_events(ctx, "Unlock", f'{ctx.channel.mention} has been unlocked.')

# Command: Purge messages from a channel
@bot.slash_command(description="Purge messages from a channel.")
async def purge(ctx, amount: int, member: nextcord.Member = None):
    """Purge messages from a channel."""
    if await commandpermissions(ctx, "purge"):
        if member:
            check = lambda m: m.author == member
            deleted = await ctx.channel.purge(limit=amount, check=check)
            await ctx.send(f'{len(deleted)} messages from {member.mention} have been purged from the channel.')
            await log_events(ctx, "Purge", f'{len(deleted)} messages from {member.mention} have been purged from {ctx.channel.mention}.')
        else:
            deleted = await ctx.channel.purge(limit=amount + 1)
            await ctx.send(f'{len(deleted) - 1} messages have been purged from the channel.')
            await log_events(ctx, "Purge", f'{len(deleted) - 1} messages have been purged from {ctx.channel.mention}.')

# Command: Add role to a member
@bot.slash_command(description="Add a role to a member.")
async def addrole(ctx, member: nextcord.Member, role: nextcord.Role):
    """Add a role to a member."""
    if await commandpermissions(ctx, "addrole"):
        await member.add_roles(role)
        await ctx.send(f'{member.mention} has been given the {role.name} role.')
        await log_events(ctx, "Add Role", f'{member.mention} has been given the {role.name} role.')

# Command: Remove role from a member
@bot.slash_command(description="Remove a role from a member.")
async def removerole(ctx, member: nextcord.Member, role: nextcord.Role):
    """Remove a role from a member."""
    if await commandpermissions(ctx, "removerole"):
        await member.remove_roles(role)
        await ctx.send(f'{member.mention} no longer has the {role.name} role.')
        await log_events(ctx, "Remove Role", f'{member.mention} no longer has the {role.name} role.')

# Command: Set or toggle the logging channel.
@bot.slash_command(description="Set or toggle the logging channel.")
async def logging(ctx, channel: nextcord.TextChannel = None, toggle: bool = None):
    """Set or toggle the logging channel."""
    if await commandpermissions(ctx, "logging"):
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
async def announce(ctx, message: str):
    """Make an announcement."""
    if await commandpermissions(ctx, "announce"):
        announcement_channel_id = await get_setting("announcement_channel_id")
        if announcement_channel_id:
            announcement_channel = bot.get_channel(int(announcement_channel_id))
            await announcement_channel.send(message)
        else:
            await ctx.send("Announcement channel is not set. Use /setannouncementchannel command to set it.")

# Command: Set the announcement channel.
@bot.slash_command(description="Set the announcement channel.")
async def setannouncementchannel(ctx, channel: nextcord.TextChannel):
    """Set the announcement channel."""
    if await commandpermissions(ctx, "setannouncementchannel"):
        await set_channel_id("announcement_channel", channel.name, channel.id)
        await ctx.send(f"Announcement channel set to {channel.mention}.")

# Command: Show help information.
@bot.slash_command(description="Show help information.")
async def help(ctx):
    """Show help information."""
    if await commandpermissions(ctx, "help"):
        help_message = """
        **Available Commands:**
        **/lock** - Lock a channel to prevent members from sending messages.
        **/unlock** - Unlock a previously locked channel.
        **/purge** - Purge messages from a channel.
        **/addrole** - Add a role to a member.
        **/removerole** - Remove a role from a member.
        **/logging** - Set or toggle the logging channel.
        **/announce** - Make an announcement.
        **/setannouncementchannel** - Set the announcement channel.
        """
        await ctx.send(help_message)

# Start the bot
bot_token = get_bot_token()
if bot_token:
    bot.run(bot_token)
else:
    print("Bot token not found in Firestore.")