import asyncio
from aiohttp import web
import discord
from discord.ext import commands

# Replace placeholders with your actual credentials
DISCORD_TOKEN = "DISCORD_TOKEN"  # Update with the new bot token
CHANNEL_ID = 1312759469561741322  # Replace with your channel ID

# Messages storage
messages = []

# Discord Bot Setup
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Flask API with aiohttp
app = web.Application()

async def send_message(request):
    """API to receive messages from the website and send to Discord."""
    data = await request.json()
    username = data.get("username")
    message = data.get("message")

    if username and message:
        channel = bot.get_channel(CHANNEL_ID)
        if channel:
            await channel.send(f"{username}: {message}")
            return web.json_response({"status": "Message sent to Discord"})
    return web.json_response({"error": "Invalid request"}, status=400)

async def receive_messages(request):
    """API to send messages from Discord to the website."""
    return web.json_response(messages[-50:])  # Only return the last 50 messages

app.router.add_post('/api/messages', send_message)
app.router.add_get('/api/messages/receive', receive_messages)

@bot.event
async def on_message(message):
    """Handles messages received in the Discord channel."""
    if message.channel.id == CHANNEL_ID and not message.author.bot:
        messages.append({
            "username": message.author.name,
            "message": message.content
        })
        # Limit stored messages to 100 to save memory
        if len(messages) > 100:
            messages.pop(0)

async def main():
    """Run both Flask and Discord bot together."""
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 5000)
    await site.start()

    # Run the bot concurrently
    await bot.start(DISCORD_TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
