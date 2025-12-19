import discord
from discord import app_commands
from datetime import datetime, timedelta
import asyncio
import os
import random
from zoneinfo import ZoneInfo  # For time zones (Python 3.9+)

# Replace 'YOUR_BOT_TOKEN' with your actual Discord bot token
TOKEN = os.getenv("TOKEN")

# Define Vietnam time zone
VIETNAM_TZ = ZoneInfo("Asia/Ho_Chi_Minh")

# Create a bot instance with intents
intents = discord.Intents.default()
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)

# Dictionary to store user balances for the game
user_balances = {}

@tree.command(name="time", description="Get the current time in Vietnam")
async def time_command(interaction: discord.Interaction):
    # Get the current time in Vietnam (UTC+7)
    current_time = datetime.now(VIETNAM_TZ).strftime("%Y-%m-%d %H:%M:%S ICT")  # ICT is Indochina Time
    await interaction.response.send_message(f"The current time in Vietnam is: {current_time}")

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
    
    # Calculate completion time in UTC for internal delay calculation
    now_utc = datetime.now(ZoneInfo("UTC"))
    completion_time_utc = now_utc + timedelta(hours=hours, minutes=minutes)
    delay = (completion_time_utc - now_utc).total_seconds()
    
    # Display completion time in Vietnam time zone
    completion_time_vietnam = completion_time_utc.astimezone(VIETNAM_TZ).strftime("%Y-%m-%d %H:%M:%S ICT")
    
    # Respond immediately
    await interaction.response.send_message(f"Added farm process for {name} with {resource}, completion at {completion_time_vietnam}")
    
    # Schedule the completion message
    asyncio.create_task(send_completion_message(interaction.channel, name, time_str, delay))

@tree.command(name="info", description="info bot")
async def info_command(interaction: discord.Interaction):
    await interaction.response.send_message("Hi! tôi tên là Penguin, nhà phát triển của tôi là Hứa Thịnh. Hiện tại tôi đang ở phiên bản beta và vẫn đang trong giai đoạn phát triển cũng như vá một số lỗi cần thiết!")

@tree.command(name="game", description="Register for the game")
async def game_command(interaction: discord.Interaction):
    user_id = interaction.user.id
    user_balances[user_id] = 10  # Initial balance
    await interaction.response.send_message('Successfully Registered. Current Balance: 10$')

@tree.command(name="play", description="Start playing the game")
async def play_command(interaction: discord.Interaction):
    user_id = interaction.user.id
    if user_id not in user_balances:
        await interaction.response.send_message('Please register first with /game.')
        return
    await interaction.response.send_message('Choose the Result That You Predict: even/odd/number. Bet amount (use /bet command)')

@tree.command(name="bet", description="Place a bet on the game")
@app_commands.describe(choice="Choose the result you predict", bet_amount="Amount to bet", number="If choosing 'number', specify the number (1-10)")
@app_commands.choices(choice=[
    app_commands.Choice(name="even", value="even"),
    app_commands.Choice(name="odd", value="odd"),
])
async def bet_command(interaction: discord.Interaction, choice: str, bet_amount: int, number: int = None):
    user_id = interaction.user.id
    if user_id not in user_balances:
        await interaction.response.send_message('Please register first with /game.')
        return
    
    choice = choice.lower()
    if choice not in ['even', 'odd' ]:
        await interaction.response.send_message('Invalid choice. Choose even, odd, or number.')
        return
    
    if bet_amount <= 0 or bet_amount > user_balances[user_id]:
        await interaction.response.send_message('Invalid bet amount. Must be positive and not exceed your balance.')
        return
    
    
    
    # Generate random number (1-10)
    result = random.randint(1, 10)
    
    # Check if prediction is correct
    correct = False
    if choice == 'even' and result % 2 == 0:
        correct = True
    elif choice == 'odd' and result % 2 != 0:
        correct = True
    
    
    if correct:
        user_balances[user_id] += bet_amount
        await interaction.response.send_message(f'Correct! The result was {result}. You won {bet_amount}$. Current Balance: {user_balances[user_id]}$')
    else:
        user_balances[user_id] -= bet_amount
        await interaction.response.send_message(f'Wrong! The result was {result}. You lost {bet_amount}$. Current Balance: {user_balances[user_id]}$')

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
