import discord
import discord.ext
from discord.ext import commands
import nextcord  # noqa: F401
from nextcord import SlashOption  # noqa: F401
from enum import Enum

# Set your bot's prefix
prefix = "/"

# Create a bot instance with a command prefix
intents = discord.Intents.default()
intents = discord.Intents().all()
intents.messages = True
intents.message_content = True  # Enable MESSAGE_CONTENT intent
bot = commands.Bot(command_prefix=prefix, intents=intents)

# Global variable to store the announcement channel ID
announcement_channel_id = 1094785912111636502

# Global variable to store the current logging channel ID
logging_channel_id = 1094781943633154149
logging_enabled = True  # Set initial logging status to enabled

# Function: Log events to the specified logging channel
async def log(ctx, message):
    global logging_enabled
    if logging_enabled:
        log_channel = bot.get_channel(logging_channel_id)
        await log_channel.send(message)

# Dictionary to store warns for each member
warns = {}

class ApplicationCommandOptionType(Enum):
    STRING = 3

# Event: When the bot is ready
@bot.event
async def on_ready():
    print(f'{bot.user} is now online')
    await bot.change_presence(status=discord.Status.do_not_disturb)

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
    await log(ctx, log_message)

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
            await log(ctx, f'{user.mention} has been unbanned.')
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
    await log(ctx, log_message)

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
    await log(ctx, f'{member.mention} has been warned for {reason}.')

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
        await log(ctx, f'Warns cleared for {member.mention}.')
    else:
        await ctx.send(f'{member.mention} has no warns.')
  
# Command: Mute a member
@bot.slash_command(description="Mute a member to prevent them from sending messages.")
async def mute(ctx, member: nextcord.Member):
    """Mute a member to prevent them from sending messages."""
    role = discord.utils.get(ctx.guild.roles, name="Muted")

    if not role:
        # Create a Muted role if it doesn't exist
        role = await ctx.guild.create_role(name="Muted")

        # Set permissions for the Muted role
        for channel in ctx.guild.channels:
            await channel.set_permissions(role, send_messages=False)

    await member.add_roles(role)
    await ctx.send(f'{member.mention} has been muted.')
    await log(ctx, f'{member.mention} has been muted.')

# Command: Lock a channel
@bot.slash_command(description="Lock a channel to prevent members from sending messages.")
async def lock(ctx):
    """Lock a channel to prevent members from sending messages."""
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
    await ctx.send('This channel has been locked.')
    await log(ctx, f'{ctx.channel.mention} has been locked.')

# Command: Unlock a channel
@bot.slash_command(description="Unlock a previously locked channel.")
async def unlock(ctx):
    """Unlock a previously locked channel."""
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
    await ctx.send('This channel has been unlocked.')
    await log(ctx, f'{ctx.channel.mention} has been unlocked.')
    
# Command: Purge messages from a channel
@bot.slash_command(description="Purge messages from a channel.")
async def purge(ctx, amount: int, member: nextcord.Member = None):
    """Purge messages from a channel."""
    if member:
        # Purge messages from a specific member
        check = lambda m: m.author == member
        deleted = await ctx.channel.purge(limit=amount, check=check)
        await ctx.send(f'{len(deleted)} messages from {member.mention} have been purged from the channel.')
        await log(ctx, f'{len(deleted)} messages from {member.mention} have been purged from {ctx.channel.mention}.')
    else:
        # Purge messages without specifying a member
        deleted = await ctx.channel.purge(limit=amount + 1)
        await ctx.send(f'{len(deleted) - 1} messages have been purged from the channel.')
        await log(ctx, f'{len(deleted) - 1} messages have been purged from {ctx.channel.mention}.')

# Command: Add role to a member
@bot.slash_command(description="Add a role to a member.")
async def addrole(ctx, member: discord.Member, role: discord.Role):
    """Add a role to a member."""
    await member.add_roles(role)
    await ctx.send(f'{member.mention} has been given the {role.name} role.')
    await log(ctx, f'{member.mention} has been given the {role.name} role.')

# Command: Remove role from a member
@bot.slash_command(description="Remove a role from a member.")
async def removerole(ctx, member: discord.Member, role: discord.Role):
    """Remove a role from a member."""
    await member.remove_roles(role)
    await ctx.send(f'{member.mention} no longer has the {role.name} role.')
    await log(ctx, f'{member.mention} no longer has the {role.name} role.')

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
    poll_embed = discord.Embed(title="Poll", description=poll_message, color=discord.Color.blue())
    poll_embed.set_footer(text=f"Poll created by {ctx.author.display_name}")
    poll_message = await ctx.send(embed=poll_embed)

    # Add reactions to the poll message for each option
    for i in range(len(options)):
        await poll_message.add_reaction(chr(0x1F1E6 + i))

    await log(ctx, f"Poll created by {ctx.author.display_name}")

# Command: Help - Show all available commands
@bot.slash_command(description="Show all available commands.")
async def commandhelp(ctx):
    """Show all available commands."""
    help_message = (
        "**Available commands:**\n\n"
        "**/kick**: Kick a member from the server.\n"
        "**/ban**: Ban a member from the server.\n"
        "**/unban**: Unban a member from the server.\n"
        "**/lock**: Lock a channel to prevent members from sending messages.\n"
        "**/unlock**: Unlock a previously locked channel.\n"
        "**/mute**: Mute a member to prevent them from sending messages.\n"
        "**/addrole**: Add a role to a member.\n"
        "**/removerole**: Remove a role from a member.\n"
        "**/purge**: Purge messages from a channel.\n"
        "**/warn**: Warn a member.\n"
        "**/logging**: Set or toggle the logging channel.\n"
        "**/announce**: Make an announcement.\n"
        "**/poll**: Create a poll.\n"
        "**/commandhelp**: Show all available commands.\n"
    )
    await ctx.send(help_message)

# Run the bot with your Discord bot token
bot.run('OTk3MjA2MTE2ODYzODUyNzA2.GSiZpf.mGbHqB7OKgdn3qyNJWj09umv8lDwamKqIgxG7c')