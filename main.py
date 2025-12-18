import discord
from discord import app_commands
from datetime import datetime, timedelta
import asyncio
import os

# Replace 'YOUR_BOT_TOKEN' with your actual Discord bot token
TOKEN = os.getenv("TOKEN")

# Create a bot instance with intents
intents = discord.Intents.default()
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)

@tree.command(name="time", description="Get the current time")
async def time_command(interaction: discord.Interaction):
    # Get the current time in UTC
    current_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    await interaction.response.send_message(f"The current time is: {current_time}")

@tree.command(name="add", description="Add a farm process with completion notification")
@app_commands.describe(name="Name of the process", resource="Resource type (food/wood/stone/gold)", time_str="Time in format like 2H30P (H for hours, P for minutes)")
async def add_command(interaction: discord.Interaction, name: str, resource: str, time_str: str):
    # Validate resource
    valid_resources = ["food", "wood", "stone", "gold"]
    if resource.lower() not in valid_resources:
        await interaction.response.send_message("Invalid resource. Choose from food, wood, stone, gold.")
        return
    
    # Parse time_str, assuming format "XHYP" where X is hours, Y is minutes (P for minutes)
    try:
        parts = time_str.upper().split('H')
        if len(parts) != 2:
            raise ValueError
        hours = int(parts[0])
        minutes_part = parts[1].split('P')[0]
        minutes = int(minutes_part)
    except ValueError:
        await interaction.response.send_message("Invalid time format. Use like 2H30P for 2 hours 30 minutes.")
        return
    
    # Calculate completion time
    now = datetime.utcnow()
    completion_time = now + timedelta(hours=hours, minutes=minutes)
    delay = (completion_time - now).total_seconds()
    
    # Respond immediately
    await interaction.response.send_message(f"Added farm process for {name} with {resource}, completion at {completion_time.strftime('%Y-%m-%d %H:%M:%S UTC')}")
    
    # Schedule the completion message
    asyncio.create_task(send_completion_message(interaction.channel, name, time_str, delay))

async def send_completion_message(channel, name, time_str, delay):
    await asyncio.sleep(delay)
    await channel.send(f"Completed the Farm Process Of {name} Time {time_str}")

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    # Sync the slash commands
    await tree.sync()

# Run the bot
bot.run(TOKEN)
