import discord
from discord import app_commands
import datetime
import os

# Replace 'YOUR_BOT_TOKEN' with your actual Discord bot token
TOKEN = os.gevenv("TOKEN")

# Create a bot instance with intents
intents = discord.Intents.default()
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)

@tree.command(name="time", description="Get the current time")
async def time_command(interaction: discord.Interaction):
    # Get the current time in UTC
    current_time = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    await interaction.response.send_message(f"The current time is: {current_time}")

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    # Sync the slash commands
    await tree.sync()

# Run the bot
bot.run(TOKEN)
