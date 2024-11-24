import os
import nextcord
import firebase_admin
from nextcord import SlashOption, Embed
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

async def get_channel_id(str):
    """Get the channel ID from Firestore."""
    channel_ref = db.collection("channel_ids").document(str)
    try:
        snapshot = channel_ref.get()
        if snapshot.exists:
            return snapshot.to_dict().get("id")
        else:
            return None
    except Exception as e:
        print(f"Error getting channel ID: {e}")
        return None

async def set_channel_id(str, channel_name, channel_id):
    """Set the channel ID in Firestore."""
    channel_ref = db.collection("channel_ids").document(str)
    try:
        channel_ref.set({"id": channel_id})
    except Exception as e:
        print(f"Error setting channel ID: {e}")

async def set_role_id(str, role_name, role_id):
    """Set the role ID in Firestore."""
    channel_ref = db.collection("roles").document(str)
    try:
        channel_ref.set({"id": role_id})
    except Exception as e:
        print(f"Error setting role ID: {e}")

# Function to get a role id from Firestore
async def get_role_id(str):
    """Get the role id from Firestore."""
    try:
        channel_ref = db.collection("roles").document(str)
        snapshot = channel_ref.get()
        if snapshot.exists:
            return snapshot.to_dict().get("id")
    except Exception as e:
        print(f"Error getting role id: {e}")
    return None

# Function to set what roles are allowed to run commands
async def set_allowed_role(role_name: str, allow: bool):
    """Set allowed roles in Firestore."""
    try:
        doc_ref = db.collection('roles').document('allowed_commands')
        doc = doc_ref.get()

        if doc.exists:
            data = doc.to_dict()
        else:
            data = {}

        data[role_name] = allow
        doc_ref.set(data)
    except Exception as e:
        print(f"Error setting allowed role: {e}")

# Function to check what roles are allowed to run commands
async def get_allowed_roles():
    """Retrieve allowed roles from Firestore."""
    allowed_roles = {}

    try:
        doc_ref = db.collection('roles').document('allowed_commands')
        doc = doc_ref.get()  # Remove 'await' from here
        if doc.exists:
            data = doc.to_dict()
            allowed_roles = {role_name: allow for role_name, allow in data.items()}  # Get the dictionary of allowed roles
    except Exception as e:
        print(f"Error fetching allowed roles: {e}")

    return allowed_roles

async def apply_punishment(ctx, member: nextcord.Member, action: str):
    """Apply the specified punishment to the member and log the action."""
    guild = ctx.guild
    reason = "Warn threshold reached."

    if action == "mute":
        # Ensure you have the necessary permissions and role for muting
        mute_role = nextcord.utils.get(guild.roles, name="Muted")
        if mute_role:
            await member.add_roles(mute_role)
            await ctx.send(f"{member.mention} has been muted.")
            await log_events(ctx, f'{member.mention} has been muted for for reaching the warn threshold.')
        else:
            await ctx.send("Mute role not found.")
    elif action == "kick":
        try:
            await member.kick(reason=reason)
            await ctx.send(f"{member.mention} has been kicked.")
            
            # Log the kick event
            await log_events(ctx, f"{member.mention} has been kicked for reaching the warn threshold.")
            
            # Store kick information in Firebase
            try:
                kicks_ref = db.collection("data").document("kicks")
                kick_info = {
                    member.display_name: {
                        "user_id": str(member.id),
                        "username": member.name,
                        "kick_reason": reason
                    }
                }
                kicks_ref.set(kick_info, merge=True)
            except Exception as e:
                print(f"Error storing kick information: {e}")
                
        except nextcord.Forbidden:
            await ctx.send("I don't have permission to kick members.")
    elif action == "ban":
        try:
            await member.ban(reason=reason)
            await ctx.send(f"{member.mention} has been banned.")
            
            # Log the ban event
            await log_events(ctx, f"{member.mention} has been banned for reaching the warn threshold.")
            
            # Store ban information in Firebase
            try:
                bans_ref = db.collection("data").document("bans")
                ban_info = {
                    member.display_name: {
                        "user_id": str(member.id),
                        "username": member.name,
                        "ban_reason": reason
                    }
                }
                bans_ref.set(ban_info, merge=True)
            except Exception as e:
                print(f"Error storing ban information: {e}")
                
        except nextcord.Forbidden:
            await ctx.send("I don't have permission to ban members.")

# Function to check the user for permissions to run the command
async def permission_check(ctx):
    """Check permissions for executing commands."""
    allowed_roles = await get_allowed_roles()  # Await the asynchronous operation

    # Get the names of the roles the user has
    user_roles = [role.name for role in ctx.user.roles]

    # Check if any of the user's roles are allowed
    for role_name in user_roles:
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

# Function to get the server invite link
async def get_server_invite(ctx):
    """Get the server invite link from Firestore."""
    try:
        invite_ref = db.collection("secrets").document("server_invite")
        snapshot = invite_ref.get()
        if snapshot.exists:
            return snapshot.to_dict().get("link")
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
        invite_ref.set({"link": invite_data})
    except Exception as e:
        print(f"Error setting server invite: {e}")

# Function to get the server invite link
async def get_github_repo(ctx):
    """Get the server invite link from Firestore."""
    try:
        invite_ref = db.collection("secrets").document("github_repo")
        snapshot = invite_ref.get()
        if snapshot.exists:
            return snapshot.to_dict().get("link")
        else:
            return None
    except Exception as e:
        print(f"Error getting GitHub Repository: {e}")
        return None

# Function to set the server invite link
async def set_github_repo(invite_data):
    """Set the GitHub Repository link in Firestore."""
    try:
        invite_ref = db.collection("secrets").document("github_repo")
        invite_ref.set({"link": invite_data})
    except Exception as e:
        print(f"Error setting GitHub Repository: {e}")

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
    # Get the join channel ID and join message
    join_channel_id = await get_channel_id("join_channel")
    if join_channel_id:
        join_channel = bot.get_channel(join_channel_id)
        if join_channel:
            join_message = await get_join_message()
            if join_message:
                await join_channel.send(f"{member.mention} {join_message}")

    # Get the role to add from Firestore
    role_ref = db.collection("roles").document("join_role")
    role_data = role_ref.get().to_dict() or {}
    role_id = role_data.get("id")

    if role_id:
        role = nextcord.utils.get(member.guild.roles, id=int(role_id))
        if role:
            await member.add_roles(role)
        else:
            print(f"Role with ID {role_id} not found.")

@bot.event
async def on_member_remove(member: nextcord.Member):
    leave_channel_id = await get_channel_id("leave_channel")
    if leave_channel_id:
        leave_channel = bot.get_channel(leave_channel_id)
        if leave_channel:
            leave_message = await get_leave_message()
            if leave_message:
                await leave_channel.send(f"{member.mention} {leave_message}")

def get_warn_info(member_id, warns_data):
    """Retrieve warning info for a specific member."""
    warnings = warns_data.get(member_id, [])
    if not warnings:
        return f"Username & User ID | Unknown - {member_id}\nWarns | No warnings found"

    reasons = [warn["reason"] for warn in warnings]
    reason_list = ", ".join(reasons)
    username = warnings[0].get("username", "Unknown")  # Assuming the username is the same for all warnings
    return f"Username & User ID | {username} - {member_id}\nWarns | {reason_list}"

# Function to log ran commands
async def log_events(ctx, message):
    if await get_setting("logging") == True:
        log_channel_id = await get_channel_id("logging_channel")
        if log_channel_id:
            log_channel = bot.get_channel(int(log_channel_id))
            if log_channel:
                log_message = f'Executed: <@{ctx.user.id}> | {message}'  # Include user's display name, action, and channel name
                await log_channel.send(log_message)
        else:
                print("Error: Logging channel not found")
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

import nextcord
from nextcord import Embed

# Command: List banned members and their reasons
@bot.slash_command(description="List banned members and their reasons.")
async def banlist(ctx):
    """List banned members and their ban reasons from Firebase."""
    try:
        # Fetch the 'bans' document from the 'data' collection
        bans_ref = db.collection("data").document("bans")
        bans_doc = bans_ref.get()

        if bans_doc.exists:
            bans_data = bans_doc.to_dict()
            if not bans_data:
                await ctx.send("No members are currently banned.")
                return

            # Create the embed
            embed = Embed(title="**Banned Members List**", color=nextcord.Color.red())

            # Add each banned member's info with reason
            for username, ban_info in bans_data.items():
                ban_reason = ban_info.get("ban_reason", "No reason provided.")
                user_id = ban_info.get("user_id", "Unknown ID")
                user_mention = f"<@{user_id}>"  # Add user mention here

                # Format each banned member's entry without the "Banned By" field
                embed.add_field(
                    name=f"**{username}**",
                    value=f"Mention: {user_mention} | User ID: `{user_id}`\n"
                        f"Reason: {ban_reason}",
                    inline=False
                )

            # Send the embed message
            await ctx.send(embed=embed)
        else:
            await ctx.send("No members are currently banned.")
    except Exception as e:
        await ctx.send(f"An error occurred while fetching the ban list: {e}")

# Command: Kick a member
@bot.slash_command(description="Kick a member from the server.")
async def kick(ctx, member: nextcord.Member, *, reason=None):
    """Kick a member from the server."""
    if await permission_check(ctx):
        await member.kick(reason=reason)
        await ctx.send(f'{member.mention} has been kicked.')
        await log_events(ctx, f'{member.mention} has been kicked for {reason}.')

@bot.slash_command(description="Warn a member.")
async def warn(ctx, member: nextcord.Member, reason: str):
    """Warn a member."""
    if await permission_check(ctx):
        warn_ref = db.collection("data").document("warns")
        member_id = str(member.id)
        warns_data = warn_ref.get().to_dict() or {}

        # Initialize or update the warnings
        member_warns = warns_data.get(member_id, [])
        
        warn_details = {
            "reason": reason,
            "warn_number": len(member_warns) + 1,
            "username": member.name,
            "warned_by": ctx.user.name
        }
        member_warns.append(warn_details)

        # Update the Firestore document
        warn_ref.set({member_id: member_warns}, merge=True)

        # Check if the threshold is met or exceeded
        warn_threshold = await get_setting("warn_threshold")
        punishment_action = await get_setting("punishment_action")

        if len(member_warns) >= warn_threshold:
            if punishment_action:
                await apply_punishment(ctx, member, punishment_action)

        # Notify the user and log the event
        await ctx.send(f'{member.mention} has been warned for {reason}.')
        await log_events(ctx, f'{member.mention} has been warned for {reason}.')

# Command: View all warnings for the server
@bot.slash_command(description="View all warnings for the server.")
async def serverwarns(ctx):
    """Get all warnings for the server."""
    warn_ref = db.collection("data").document("warns")
    warns_data = warn_ref.get().to_dict() or {}

    if not warns_data:
        await ctx.send("No warnings found.")
        return

    # Create the embed
    embed = Embed(title="**Server Warnings List**", color=nextcord.Color.red())

    # Build the report list with each member's warnings
    for member_id, warns in warns_data.items():
        username = warns[0].get("username", "Unknown User")
        user_mention = f"<@{member_id}>"  # Correct mention format
        user_id = member_id  # User ID directly from member_id
        
        # Start the member's entry with their username and ID, labeled
        member_info = f"**{username}**\nMention: {user_mention} | User ID: `{user_id}`"

        # For each warning, add the reason and who warned, with separation between each warning
        for warn in warns:
            warn_reason = warn.get("reason", "No reason provided")
            warned_by = warn.get("warned_by", "Unknown")
            
            # Add the reason and warned by to the member's entry, separated by blank lines
            member_info += f"\n  Reason: {warn_reason}\n  Warned By: {warned_by}\n"

        # Add the formatted member's entry directly without a title
        embed.add_field(name="\u200b", value=member_info, inline=False)  # Use invisible character for the field name

    # Send the embed message with the warnings
    await ctx.send(embed=embed)

@bot.slash_command(description="Clear all warnings")
async def clearserverwarns(ctx):
    """Clear all warnings for all members in the server."""
    if await permission_check(ctx):
        warn_ref = db.collection("data").document("warns")

        # Clear all warnings
        warn_ref.set({})

        await ctx.send("All warnings have been cleared.")
        await log_events(ctx, "All warnings have been cleared.")

# Command: View warns for a member
@bot.slash_command(description="View warns for a member.")
async def warns(ctx, member: nextcord.Member):
    """Get warnings for a specific member."""
    warn_ref = db.collection("data").document("warns")
    warns_data = warn_ref.get().to_dict() or {}

    member_id = str(member.id)
    if member_id not in warns_data:
        await ctx.send(f"No warnings found for {member.name}.")
        return

    # Create the embed
    embed = Embed(title=f"Warnings for {member.name}", color=nextcord.Color.red())

    # Build the formatted member entry
    user_mention = f"<@{member_id}>"
    user_id = member_id  # User ID directly from member_id

    # Add the username, mention, and user ID at the top
    member_entry = f"{member.name}\nMention: {user_mention} | User ID: `{user_id}`"

    # For each warning, add the reason and who warned, with spacing between each warning
    for warn in warns_data[member_id]:
        warn_reason = warn.get("reason", "No reason provided")
        warned_by = warn.get("warned_by", "Unknown")
        
        # Add each warning's details to the entry
        member_entry += f"\n  Reason: {warn_reason}\n  Warned By: {warned_by}\n"

    # Add the formatted entry to the embed
    embed.add_field(name="\u200b", value=member_entry, inline=False)

    # Send the embed message with the warnings
    await ctx.send(embed=embed)

@bot.slash_command(description="Remove a specific warning for a member.")
async def unwarn(ctx, member: nextcord.Member, warn_number: int):
    """Remove a specific warning for a member based on warn number."""
    if await permission_check(ctx):
        warn_ref = db.collection("data").document("warns")
        member_id = str(member.id)
        warns_data = warn_ref.get().to_dict() or {}

        if member_id not in warns_data:
            await ctx.send(f"No warnings found for {member.mention}.")
            return
        
        member_warns = warns_data[member_id]
        
        # Check if the warn number is valid
        if warn_number < 1 or warn_number > len(member_warns):
            await ctx.send(f"Invalid warning number {warn_number} for {member.mention}.")
            return
        
        # Update the warn numbers for remaining warnings
        for i, warn in enumerate(member_warns):
            warn["warn_number"] = i + 1
        
        # Update the Firestore document
        if member_warns:
            warn_ref.set({member_id: member_warns}, merge=True)
        else:
            warn_ref.update({member_id: firestore.DELETE_FIELD})

        await ctx.send(f"Warning number {warn_number} for {member.mention} has been removed.")
        await log_events(ctx, f"Warning number {warn_number} for {member.mention} has been removed.")

# Command: Set warn threshold
@bot.slash_command(description="Set the warn threshold.")
async def setwarnthreshold(ctx, threshold: int):
    """Set the warn threshold."""
    if await permission_check(ctx):
        await set_setting("warn_threshold", threshold)
        await ctx.send(f"Warn threshold set to {threshold}.")

@bot.slash_command(description="Set the punishment for meeting the warn threshold.")
async def setwarnpunishment(ctx, action: str = SlashOption(choices=["mute", "kick", "ban"])):
    """Set the punishment for meeting the warn threshold."""
    if await permission_check(ctx):
        await set_setting("punishment_action", action.lower())
        await ctx.send(f"Punishment for meeting the warn threshold set to {action}.")

# Command: Mute a member
@bot.slash_command(description="Mute a member to prevent them from sending messages.")
async def mute(ctx, member: nextcord.Member):
    """Mute a member to prevent them from sending messages."""
    if await permission_check(ctx):
        await member.add_roles(ctx.guild.get_role(await get_role_id("mute_role")))
        await ctx.send(f'{member.mention} has been muted.')
        await log_events(ctx, f'{member.mention} has been muted.')

# Command: Unmute a member
@bot.slash_command(description="Unmute a member to allow them to send messages again.")
async def unmute(ctx, member: nextcord.Member):
    """Unmute a member to allow them to send messages again."""
    if await permission_check(ctx):
        await member.remove_roles(ctx.guild.get_role(await get_role_id("mute_role")))
        await ctx.send(f'{member.mention} has been unmuted.')
        await log_events(ctx, f'{member.mention} has been unmuted.')

# Command: Set the announcement channel.
@bot.slash_command(description="Set the mute role.")
async def setmuterole(ctx, role: nextcord.Role):
    """Set the minor announcement channel."""
    if await permission_check(ctx):
        await set_role_id("mute_role", role.name, role.id)
        await ctx.send(f"Mute role set to {role.mention}.")

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
            deleted = await ctx.channel.purge(limit=amount)
            await ctx.send(f'{len(deleted)} messages have been purged from the channel.')
            await log_events(ctx, f'{len(deleted)} messages have been purged from {ctx.channel.mention}.')

# Command: Add role to a member
@bot.slash_command(description="Add a role to a member.")
async def addrole(ctx, member: nextcord.Member, role: nextcord.Role):
    """Add a role to a member."""
    if await permission_check(ctx):
        await member.add_roles(role)
        await ctx.send(f'{member.mention} has been given the {role.mention} role.')
        await log_events(ctx, f'{member.mention} has been given the {role.mention} role.')

# Command: Remove role from a member
@bot.slash_command(description="Remove a role from a member.")
async def removerole(ctx, member: nextcord.Member, role: nextcord.Role):
    """Remove a role from a member."""
    if await permission_check(ctx):
        await member.remove_roles(role)
        await ctx.send(f'{member.mention} no longer has the {role.mention} role.')
        await log_events(ctx, f'{member.mention} no longer has the {role.mention} role.')

# Command: Set roles allowed to use commands
@bot.slash_command(description="Set roles allowed to use commands.")
async def setcommandrole(ctx, role: nextcord.Role, allow: bool):
    """Set a role to be allowed or disallowed for commands."""
    if await permission_check(ctx):
        try:
            await set_allowed_role(role.name, allow)
            status = 'allowed' if allow else 'not allowed'
            await ctx.send(f'{role.mention} {status} commands.')
            await log_events(ctx, f'{role.mention} {status} commands.')
        except Exception as e:
            await ctx.send(f'Error setting role: {e}')

# Command: Set or toggle the logging channel.
@bot.slash_command(description="Set or toggle the logging channel.")
async def logging(ctx, channel: nextcord.TextChannel = None, toggle: bool = None):
    """Set or toggle the logging channel."""
    if await permission_check(ctx):
        if channel:
            await set_channel_id("logging_channel", channel.name, channel.id)
            await ctx.send(f"Logging channel set to {channel.mention}.")
        elif toggle is not None:
            await set_setting("logging", toggle)
            status = "enabled" if toggle else "disabled"
            await ctx.send(f"Logging is now {status}.")
        else:
            await ctx.send("Invalid command usage.")

# Command: Make an announcement.
@bot.slash_command(description="Make an announcement.")
async def announce(ctx, message: str, ping_everyone: bool = False, minor_announcement: bool = False, testing_ping: bool = False):
    """Make an announcement."""
    if await permission_check(ctx):
        announcement_channel = await get_channel_id("announcement_channel")
        if announcement_channel:
            announcement_channel = bot.get_channel(int(announcement_channel))
            if ping_everyone:
                await announcement_channel.send("@everyone " + message)
                await ctx.send("Announcement sent successfully")
            else:
                if minor_announcement:
                    minorannouncement_role = await get_role_id("minorannouncement_role")
                    await announcement_channel.send(f"<@&{minorannouncement_role}> " + message)
                    await ctx.send("Announcement sent successfully")
                else:
                    if testing_ping:
                        testing_role = await get_role_id("testing_role")
                        await announcement_channel.send(f"<@&{testing_role}> " + message)
                        await ctx.send("Development announcement sent successfully")
                    else:
                        await announcement_channel.send(message)
                        await ctx.send("Announcement sent successfully")
    else:
        await ctx.send("Announcement channel or minor announcement role is not set. Use /setannouncementchannel or /setminorannouncementrole command to set it.")

# Command: Set the announcement channel.
@bot.slash_command(description="Set the announcement channel.")
async def setannouncementchannel(ctx, channel: nextcord.TextChannel):
    """Set the announcement channel."""
    if await permission_check(ctx):
        await set_channel_id("announcement_channel", channel.name, channel.id)
        await ctx.send(f"Announcement channel set to {channel.mention}.")

# Command: Set the minor announcement role.
@bot.slash_command(description="Set the minor announcement role.")
async def setminorannouncementrole(ctx, role: nextcord.Role):
    """Set the minor announcement channel."""
    if await permission_check(ctx):
        await set_role_id("minorannouncement_role", role.name, role.id)
        await ctx.send(f"Minor announcement role set to {role.mention}.")

# Command: Set the testing role channel.
@bot.slash_command(description="Set the testing and development role.")
async def settestingrole(ctx, role: nextcord.Role):
    """Set the testing and development role."""
    if await permission_check(ctx):
        await set_role_id("testing_role", role.name, role.id)
        await ctx.send(f"Testing role set to {role.mention}.")

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

# Command: Get GitHub Repository link
@bot.slash_command(description="Get GitHub Repository link")
async def githubrepo(ctx):
    """Get server invite link"""
    github_repo = await get_github_repo(ctx)
    await ctx.send(github_repo)

# Command: Set the GitHub Repository link
@bot.slash_command(description="Set the GitHub Repository link")
async def setgithubrepo(ctx, link: str):
    """Set the GitHub Repository link"""
    if await permission_check(ctx):
        try:
            await set_github_repo(link)
            await ctx.send("GitHub Repository link has been set")
        except Exception as e:
            await ctx.send(f"Error setting GitHub Repository link: {str(e)}")

# Command: Set join message channel
@bot.slash_command(description="Set the channel for sending join messages.")
async def setjoinchannel(ctx, channel: nextcord.TextChannel):
    """Set the channel for sending join messages."""
    if await permission_check(ctx):
        await set_channel_id("join_channel", channel.name, channel.id)
        await ctx.send(f"Join message channel set to {channel.mention}.")

# Command: Set leave message channel
@bot.slash_command(description="Set the channel for sending leave messages.")
async def setleavechannel(ctx, channel: nextcord.TextChannel):
    """Set the channel for sending leave messages."""
    if await permission_check(ctx):
        await set_channel_id("leave_channel", channel.name, channel.id)
        await ctx.send(f"Leave message channel set to {channel.mention}.")

# Command: Set welcome message
@bot.slash_command(description="Set the welcome message.")
async def setjoinmessage(ctx, message: str):
    """Set the welcome message."""
    if await permission_check(ctx):
        await set_join_message(message)
        await ctx.send("Welcome message set successfully.")

# Command: Get join message
@bot.slash_command(description="Get the join message.")
async def getjoinmessage(ctx):
    """Get the join message."""
    if await permission_check(ctx):
        join_message = await get_join_message()
        if join_message:
            await ctx.send(f"Current join message:\n{join_message}")
        else:
            await ctx.send("Join message is not set.")

# Command: Set leave message
@bot.slash_command(description="Set the leave message.")
async def setleavemessage(ctx, message: str):
    """Set the leave message."""
    if await permission_check(ctx):
        await set_leave_message(message)
        await ctx.send("Leave message set successfully.")

# Command: Get leave message
@bot.slash_command(description="Get the leave message.")
async def getleavemessage(ctx):
    """Get the leave message."""
    if await permission_check(ctx):
        leave_message = await get_leave_message()
        if leave_message:
            await ctx.send(f"Current leave message:\n{leave_message}")
        else:
            await ctx.send("Leave message is not set.")

@bot.slash_command(description="Set the role to be added when a member joins.")
async def setjoinrole(ctx, role: nextcord.Role):
    """Set the role to be added when a member joins."""
    if await permission_check(ctx):
        role_ref = db.collection("roles").document("join_role")
        
        # Update or set the role ID in Firestore
        role_ref.set({"id": str(role.id)}, merge=True)

        await ctx.send(f"The join role has been set to {role.mention}.")

# Command: Show help information.
@bot.slash_command(description="Show help information.")
async def help(ctx):
    """Show help information."""
    await ctx.send(
"""**Moderation Commands:**
- `/ban` | Ban a member from the server.
- `/banlist` | View all banned members and their reasons.
- `/unban` | Unban a member from the server.
- `/kick` | Kick a member from the server.
- `/warn` | Warn a member.
- `/serverwarns` | View all warnings for the server.
- `/clearserverwarns` | Clear all warnings for the server.
- `/warns` | View warns for a member.
- `/unwarn` | Clear warns for a member.
- `/mute` | Mute a member to prevent them from sending messages.
- `/unmute` | Unmute a member to allow them to send messages again.
- `/lock` | Lock a channel to prevent members from sending messages.
- `/unlock` | Unlock a previously locked channel.
- `/announce` | Make an announcement.

**Settings and Configuration Commands**
- `/setwarnthreshold` | Set the warn threshold.
- `/setwarnpunishment` | Set the punishment for crossing/meeting the warn threshold.
- `/setmuterole` | Set the role to assign for muted members.
- `/logging` | Set or toggle the logging channel.
- `/setannouncementchannel` | Set the announcement channel.
- `/setminorannouncementrole` | Set the minor announcement role.
- `/setinvite` | Set the server invite link.
- `/setjoinmessage` | Set the welcome message.
- `/setleavemessage` | Set the leave message.
- `/setjoinchannel` | Set the channel for sending join messages.
- `/setleavechannel` | Set the channel for sending leave messages.
- `/setjoinrole` | Set the role added to members upon joining

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