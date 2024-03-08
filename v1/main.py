import nextcord
from nextcord import Interaction, SlashOption
from nextcord.ext import commands

# IDS ARE ONLY VALID FOR RYZEN'S SERVER
# User IDs
ryzenuserid = 487638433179762688

#Role Aliass
ownerrole = 1094750540132515950, "Ryzen"
modrole = 1094776533308149842, "Mod"
botrole = 1094750630674960424, "Bot", "Bots"

#Channel IDs
logschannelid = 1094781943633154149

#Miscellaneous
token = "OTk3MjA2MTE2ODYzODUyNzA2.GSiZpf.mGbHqB7OKgdn3qyNJWj09umv8lDwamKqIgxG7c"
overwritepermsforlocking = nextcord.PermissionOverwrite()
overwritepermsforlocking.send_messages = False

logging = True
intents = nextcord.Intents.default()
intents = nextcord.Intents().all()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"{bot.user.name} is now online")

@bot.slash_command()
async def kick(interaction: nextcord.Interaction, user: nextcord.Member, reason: str):
    if not interaction.user.has_any_role(ownerrole, modrole):
        await interaction.response.send_message("You don't have permission to use this command", ephemeral=True)
    else:
        await interaction.response.send_message(f"Kicked {user.mention}", ephemeral=True)
        if logging is True:
            log_channel = bot.get_channel(logschannelid)
            await log_channel.send(f"{interaction.user.mention} kicked {user.mention}. Reason = **{reason}**")
        await user.kick(reason=reason)
        
@bot.slash_command()
async def ban(interaction: nextcord.Interaction, user: nextcord.Member, reason: str):
    if not interaction.user.has_any_role(ownerrole, modrole):
        await interaction.response.send_message("You don't have permission to use this command", ephemeral=True)
    else:
        await interaction.response.send_message(f"Banned {user.mention}", ephemeral=True)
        if logging is True:
            log_channel = bot.get_channel(logschannelid)
            await log_channel.send(f"{interaction.user.mention} banned {user.mention}. Reason = **{reason}**")
        await user.ban(reason=reason)
        
@bot.slash_command()
async def unban(interaction: nextcord.Interaction, user: nextcord.Member):
    if not interaction.user.has_any_role(ownerrole, modrole):
        await interaction.response.send_message("You don't have permission to use this command", ephemeral=True)
    else:
        await interaction.response.send_message(f"Unbanned {user.mention}", ephemeral=True)
        if logging is True:
            log_channel = bot.get_channel(logschannelid)
            await log_channel.send(f"{interaction.user.mention} unbanned {user.mention}")
        await interaction.guild.unban(user)

@bot.slash_command()
async def lockchannel(interaction: nextcord.Interaction, reason: str):
    if not interaction.user.has_any_role(ownerrole, modrole):
        await interaction.response.send_message("You don't have permission to use this command", ephemeral=True)
    else:
        await interaction.response.send_message(f"Locked {message.channel.mention} because {reason}")
        if logging is True:
            log_channel = bot.get_channel(logschannelid)
        await message.channel.set_permissions(member, overwritepermsforlocking=overwritepermsforlocking)
        
@bot.slash_command()
async def unlockchannel(interaction: nextcord.Interaction):
    if not interaction.user.has_any_role(ownerrole, modrole):
        await interaction.response.send_message("You don't have permission to use this command", ephemeral=True)
    else:
        await interaction.response.send_message(f"Unlocked {message.channel.mention}")
        if logging is True:
            log_channel = bot.get_channel(logschannelid)
        await message.channel.set_permissions(member, overwritepermsforlocking=overwritepermsforlocking)

bot.run(token)