import os
token = os.environ['BOT_TOKEN']
import nextcord
from nextcord import Interaction, SlashOption
from nextcord.ext import commands

intents = nextcord.Intents.default()
intents = nextcord.Intents().all()
bot=commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"{bot.user.name} is now online")

logging = False
logschannelid = "null"

@bot.slash_command()
async def timeout(interaction: nextcord.Interaction, user: nextcord.Member, reason: str):
    if not interaction.User.guild.permissions.administrator or not nextcord.User.id == 487638433179762688:
        await interaction.response.send_message("You don't have permission to use this command", ephemeral=True)
    else:
        await interaction.response.send_message(f"Timed out {user.mention}", ephemeral=True)
        if logging is True:
            log_channel = bot.get_channel(logschannelid)
            await log_channel.send(f"{interaction.user.mention} Timed out {user.mention}. Reason = **{reason}**")
        await nextcord.Member.timeout(reason=reason)

@bot.slash_command()
async def kick(interaction: nextcord.Interaction, user: nextcord.Member, reason: str):
    if not interaction.User.guild.permissions.administrator or not nextcord.User.id == 487638433179762688:
        await interaction.response.send_message("You don't have permission to use this command", ephemeral=True)
    else:
        await interaction.response.send_message(f"Kicked {user.mention}", ephemeral=True)
        if logging is True:
            log_channel = bot.get_channel(logschannelid)
            await log_channel.send(f"{interaction.user.mention} kicked {user.mention}. Reason = **{reason}**")
        await user.kick(reason=reason)
        
@bot.slash_command()
async def ban(interaction: nextcord.Interaction, user: nextcord.Member, reason: str):
    if not interaction.User.guild.permissions.administrator or not nextcord.User.id == 487638433179762688:
        await interaction.response.send_message("You don't have permission to use this command", ephemeral=True)
    else:
        await interaction.response.send_message(f"Banned {user.mention}", ephemeral=True)
        if logging is True:
            log_channel = bot.get_channel(logschannelid)
            await log_channel.send(f"{interaction.user.mention} banned {user.mention}. Reason = **{reason}**")
        await user.ban(reason=reason)
        
@bot.slash_command()
async def unban(interaction: nextcord.Interaction, user: nextcord.Member):
    if not interaction.User.guild.permissions.administrator or not nextcord.User.id == 487638433179762688:
        await interaction.response.send_message("You don't have permission to use this command", ephemeral=True)
    else:
        await interaction.response.send_message(f"Unbanned {user.mention}", ephemeral=True)
        if logging is True:
            log_channel = bot.get_channel(logschannelid)
            await log_channel.send(f"{interaction.user.mention} unbanned {user.mention}")
        await interaction.guild.unban(user)

bot.run(token)