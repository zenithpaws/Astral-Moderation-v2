import nextcord
from nextcord.ext import commands
from enum import Enum

# Set your bot's prefix
prefix = "/"

# Create a bot instance with a command prefix
intents = nextcord.Intents.default()
intents = nextcord.Intents.all()
intents.messages = True
intents.message_content = True  # Enable MESSAGE_CONTENT intent
bot = commands.Bot(command_prefix=prefix, intents=intents)

# Global variable to store the announcement channel ID
announcement_channel_id = 1094785912111636502

# Global variable to store the current logging channel ID
logging_channel_id = 1094781943633154149
logging_enabled = True  # Set initial logging status to enabled

# Function: Log events to the specified logging channel
async def log(ctx, action, message):
    global logging_enabled
    if logging_enabled:
        log_channel = bot.get_channel(logging_channel_id)
        user_display_name = ctx.user.display_name if isinstance(ctx, nextcord.Interaction) else ctx.user.display_name
        log_message = f'{user_display_name} | {message}'  # Include action and user's display name
        await log_channel.send(log_message)

# Dictionary to store warns for each member
warns = {}

# Global variables to store warn threshold and punishment settings
warn_threshold = 3
punishment_action = "mute"  # Default punishment action

class ApplicationCommandOptionType(Enum):
    STRING = 3

# Event: When the bot is ready
@bot.event
async def on_ready():
    print(f'{bot.user} is now online')
    await bot.change_presence(status=nextcord.Status.do_not_disturb)
    
# Logic to enforce punishments when the warn threshold is crossed or met
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandInvokeError):
        original_error = error.original
        if isinstance(original_error, nextcord.Forbidden):
            # If the bot lacks permissions to perform an action, handle the error gracefully
            await ctx.send("I do not have permission to perform that action.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Missing required argument.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Bad argument provided.")
    else:
        await ctx.send("An error occurred while processing the command.")

@bot.event
async def on_member_join(member):
    if member.id in warns and len(warns[member.id]) >= warn_threshold:
        if punishment_action == "mute":
            # Implement mute logic
            pass
        elif punishment_action == "kick":
            await member.kick(reason="Crossed warn threshold.")
        elif punishment_action == "ban":
            await member.ban(reason="Crossed warn threshold.")

# Command: Ban a member
@bot.slash_command(description="Ban a member from the server.")
async def ban(ctx, member: nextcord.Member, *, reason=None):
    """Ban a member from the server."""
    await member.ban(reason=reason)
    if reason:
        response = f'{member.mention} has been banned for {reason}.'
        log_message = f'{member.mention} has been banned for {reason}.'
    else:
        response = f'{member.mention} has been banned.'
        log_message = f'{member.mention} has been banned.'

    await ctx.send(response)
    await log(ctx, "Ban", log_message)

# Command: Unban a member
@bot.slash_command(description="Unban a member from the server.")
async def unban(ctx, *, member):
    """Unban a member from the server."""
    banned_users = await ctx.guild.bans()
    member_name, member_discriminator = member.split('#')

    for ban_entry in banned_users:
        user = ban_entry.user

        if (user.name, user.discriminator) == (member_name, member_discriminator):
            await ctx.guild.unban(user)
            await ctx.send(f'{user.mention} has been unbanned.')
            await log(ctx, "Unban", f'{user.mention} has been unbanned.')
            return

# Command: Kick a member
@bot.slash_command(description="Kick a member from the server.")
async def kick(ctx, member: nextcord.Member, *, reason=None):
    """Kick a member from the server."""
    await member.kick(reason=reason)
    if reason:
        response = f'{member.mention} has been kicked for {reason}.'
        log_message = f'{member.mention} has been kicked for {reason}.'
    else:
        response = f'{member.mention} has been kicked.'
        log_message = f'{member.mention} has been kicked.'

    await ctx.send(response)
    await log(ctx, "Kick", log_message)

# Command: Warn a member
@bot.slash_command(description="Warn a member.")
async def warn(ctx, member: nextcord.Member, *, reason: str):
    """Warn a member."""
    # Add the member to the warns dictionary if not already present
    if member.id not in warns:
        warns[member.id] = []

    # Add the warn reason to the member's list of warns
    warns[member.id].append(reason)

    # Send a confirmation message
    await ctx.send(f'{member.mention} has been warned for {reason}.')
    await log(ctx, "Warn", f'{member.mention} has been warned for {reason}.')

# Command: View warns for a member
@bot.slash_command(description="View warns for a member.")
async def warns(ctx, member: nextcord.Member):
    """View warns for a member."""
    if member.id in warns:
        warn_list = "\n".join(warns[member.id])
        await ctx.send(f'Warns for {member.mention}:\n{warn_list}')
    else:
        await ctx.send(f'{member.mention} has no warns.')

# Command: Clear warns for a member
@bot.slash_command(description="Clear warns for a member.")
async def clearwarnings(ctx, member: nextcord.Member):
    """Clear warns for a member."""
    # Check if the member has any warns
    if member.id in warns:
        # Clear the warns for the member
        del warns[member.id]
        await ctx.send(f'Warns cleared for {member.mention}.')
        await log(ctx, "Clear Warns", f'Warns cleared for {member.mention}.')
    else:
        await ctx.send(f'{member.mention} has no warns.')
        
# Command: Set warn threshold
@bot.slash_command(description="Set the warn threshold.")
async def setwarnthreshold(ctx, threshold: int):
    """Set the warn threshold."""
    global warn_threshold
    warn_threshold = threshold
    await ctx.send(f"Warn threshold set to {threshold}.")

# Command: Set punishment for crossing or meeting the warn threshold
@bot.slash_command(description="Set the punishment for crossing/meeting the warn threshold. Options: mute, kick, ban")
async def setwarnpunishment(ctx, action: str):
    """Set the punishment for crossing/meeting the warn threshold."""
    global punishment_action
    # Validate the provided action (e.g., "mute", "kick", "ban")
    valid_actions = ["mute", "kick", "ban"]
    if action.lower() in valid_actions:
        punishment_action = action.lower()
        await ctx.send(f"Punishment for crossing/meeting the warn threshold set to {action}.")
    else:
        await ctx.send("Invalid punishment action. Available actions: mute, kick, ban.")

# Command: Mute a member
@bot.slash_command(description="Mute a member to prevent them from sending messages.")
async def mute(ctx, member: nextcord.Member):
    """Mute a member to prevent them from sending messages."""
    role = nextcord.utils.get(ctx.guild.roles, name="Muted")

    if not role:
        # Create a Muted role if it doesn't exist
        role = await ctx.guild.create_role(name="Muted")

        # Set permissions for the Muted role
        for channel in ctx.guild.channels:
            await channel.set_permissions(role, send_messages=False)

    await member.add_roles(role)
    await ctx.send(f'{member.mention} has been muted.')
    await log(ctx, "Mute", f'{member.mention} has been muted.')

# Command: Lock a channel
@bot.slash_command(description="Lock a channel to prevent members from sending messages.")
async def lock(ctx):
    """Lock a channel to prevent members from sending messages."""
    # Get the @everyone role
    everyone_role = ctx.guild.default_role

    # Get the channel's permissions for @everyone
    channel_permissions = ctx.channel.overwrites_for(everyone_role)

    # Set the send_messages permission to False while preserving other permissions
    channel_permissions.send_messages = False

    # Apply the updated permissions to the channel
    await ctx.channel.set_permissions(everyone_role, overwrite=channel_permissions)

    await ctx.send('This channel has been locked.')
    await log(ctx, "Lock", f'{ctx.channel.mention} has been locked.')

# Command: Unlock a channel
@bot.slash_command(description="Unlock a previously locked channel.")
async def unlock(ctx):
    """Unlock a previously locked channel."""
    # Get the @everyone role
    everyone_role = ctx.guild.default_role

    # Get the channel's current permissions for @everyone
    channel_permissions = ctx.channel.overwrites_for(everyone_role)

    # Update the send_messages permission to True while preserving other permissions
    channel_permissions.send_messages = True

    # Apply the updated permissions to the channel
    await ctx.channel.set_permissions(everyone_role, overwrite=channel_permissions)

    await ctx.send('This channel has been unlocked.')
    await log(ctx, "Unlock", f'{ctx.channel.mention} has been unlocked.')

# Command: Purge messages from a channel
@bot.slash_command(description="Purge messages from a channel.")
async def purge(ctx, amount: int, member: nextcord.Member = None):
    """Purge messages from a channel."""
    if member:
        # Purge messages from a specific member
        check = lambda m: m.author == member
        deleted = await ctx.channel.purge(limit=amount, check=check)
        await ctx.send(f'{len(deleted)} messages from {member.mention} have been purged from the channel.')
        await log(ctx, "Purge", f'{len(deleted)} messages from {member.mention} have been purged from {ctx.channel.mention}.')
    else:
        # Purge messages without specifying a member
        deleted = await ctx.channel.purge(limit=amount + 1)
        await ctx.send(f'{len(deleted) - 1} messages have been purged from the channel.')
        await log(ctx, "Purge", f'{len(deleted) - 1} messages have been purged from {ctx.channel.mention}.')

# Command: Add role to a member
@bot.slash_command(description="Add a role to a member.")
async def addrole(ctx, member: nextcord.Member, role: nextcord.Role):
    """Add a role to a member."""
    await member.add_roles(role)
    await ctx.send(f'{member.mention} has been given the {role.name} role.')
    await log(ctx, "Add Role", f'{member.mention} has been given the {role.name} role.')

# Command: Remove role from a member
@bot.slash_command(description="Remove a role from a member.")
async def removerole(ctx, member: nextcord.Member, role: nextcord.Role):
    """Remove a role from a member."""
    await member.remove_roles(role)
    await ctx.send(f'{member.mention} no longer has the {role.name} role.')
    await log(ctx, "Remove Role", f'{member.mention} no longer has the {role.name} role.')

# Command: Set Logging Channel and Toggle Logging
@bot.slash_command(description="Set or toggle the logging channel.")
async def logging(ctx, channel: nextcord.TextChannel = None, toggle: bool = None):
    """Set or toggle the logging channel."""
    global logging_channel_id, logging_enabled

    if toggle is not None:
        logging_enabled = toggle
        status = "enabled" if logging_enabled else "disabled"
        await ctx.send(f"Logging is now {status}.")
        return

    if channel:
        logging_channel_id = channel.id
        await ctx.send(f"Logging channel set to {channel.mention}.")
    else:
        await ctx.send("Please provide a valid text channel.")

# Command: Make an announcement
@bot.slash_command(description="Make an announcement.")
async def announce(ctx, title: str, description: str, ping_everyone: bool = False):
    """Make an announcement."""
    # Get the announcement channel
    announcement_channel = bot.get_channel(announcement_channel_id)

    # Check if the announcement channel exists
    if announcement_channel:
        # Format the announcement message
        announcement_message = f"**{title}**\n\n{description}"

        # Ping @everyone if specified
        if ping_everyone:
            announcement_message = "@everyone\n" + announcement_message

        # Send the announcement message to the announcement channel
        await announcement_channel.send(announcement_message)
        await ctx.send("Announcement published successfully!")
    else:
        await ctx.send("Announcement channel not found. Please configure the announcement channel ID.")
    
# Command: Create a poll
@bot.slash_command(description="Create a poll.")
async def poll(ctx, question: str, *options: str):
    """Create a poll."""
    if len(options) < 2 or len(options) > 10:
        await ctx.send("Please provide between 2 and 10 options.")
        return

    # Format the poll message
    poll_message = f"**{question}**\n\n"
    for idx, option in enumerate(options, start=1):
        poll_message += f"{idx}. {option}\n"

    # Send the poll message
    poll_embed = nextcord.Embed(title="Poll", description=poll_message, color=nextcord.Color.blue())
    poll_embed.set_footer(text=f"Poll created by {ctx.user.display_name}")
    poll_message = await ctx.send(embed=poll_embed)

    # Add reactions to the poll message for each option
    for i in range(len(options)):
        await poll_message.add_reaction(chr(0x1F1E6 + i))

    await log(ctx, "Create Poll", f"Poll created by {ctx.user.display_name}")

# Command: Server Information
@bot.slash_command(description="Display server information.")
async def serverinfo(ctx):
    """Display summary server information."""
    # Retrieve and format summary information about the server
    summary_info = f"Server Name: {ctx.guild.name}\n"
    summary_info += f"Server Creation Date: {ctx.guild.created_at.strftime('%B %d, %Y')}\n"
    summary_info += f"Total Members: {ctx.guild.member_count}\n"

    # Get the invite link
    invite_link = "https://discord.com/invite/WaTFrzaYxk"
    summary_info += f"Invite Link: {invite_link}\n"

    await ctx.send(summary_info)

# Command: Help - Show all available commands
@bot.slash_command(description="Show all available commands.")
async def help(ctx):
    """Show all available commands."""
    help_message = (
        "**Available commands:**\n\n"
        "**/ban**: Ban a member from the server.\n"
        "**/unban**: Unban a member from the server.\n"
        "**/kick**: Kick a member from the server.\n"
        "**/warn**: Warn a member.\n"
        "**/clearwarnings**: Clear warns for a member.\n"
        "**/warns**: View warns for a member.\n"
        "**/setwarnthreshold**: Set the warn threshold.\n"  # Add the new command
        "**/setwarnpunishment**: Set the punishment for crossing/meeting the warn threshold.\n"  # Add the new command
        "**/mute**: Mute a member to prevent them from sending messages.\n"
        "**/lock**: Lock a channel to prevent members from sending messages.\n"
        "**/unlock**: Unlock a previously locked channel.\n"
        "**/purge**: Purge messages from a channel.\n"
        "**/addrole**: Add a role to a member.\n"
        "**/removerole**: Remove a role from a member.\n"
        "**/logging**: Set or toggle the logging channel.\n"
        "**/announce**: Make an announcement.\n"
        "**/poll**: Create a poll.\n"
        "**/serverinfo**: Display server information.\n"
        "**/help**: Show all available commands.\n"
    )
    await ctx.send(help_message)

# Run the bot with your Discord bot token
bot.run('OTk3MjA2MTE2ODYzODUyNzA2.GSiZpf.mGbHqB7OKgdn3qyNJWj09umv8lDwamKqIgxG7c')