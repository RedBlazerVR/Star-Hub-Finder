import discord
from discord.ext import commands
from flask import Flask, request, jsonify
import threading
import os

# 1. SETUP
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID_STR = os.getenv("CHANNEL_ID")
PORT = int(os.getenv("PORT", 5000))

# Convert Channel ID to integer safely
CHANNEL_ID = int(CHANNEL_ID_STR) if CHANNEL_ID_STR else None

# Set up Bot with Intents (Crucial for 2026 discord.py)
intents = discord.Intents.default()
intents.message_content = True 
bot = commands.Bot(command_prefix="!", intents=intents)

app = Flask(__name__)

@app.route('/roblox-log', methods=['POST'])
def roblox_log():
    if not CHANNEL_ID:
        return jsonify({"error": "CHANNEL_ID not set"}), 500
        
    data = request.json
    channel = bot.get_channel(CHANNEL_ID)
    
    if channel:
        embed = discord.Embed(
            title="NovaHub Notifier",
            description="A new server has been indexed.",
            color=0x007bff
        )
        # Using Code Blocks (```) for cleaner look
        embed.add_field(name="Name", value=f"```\n{data.get('player_list', 'None')}\n```", inline=False)
        embed.add_field(name="Players", value=data.get("player_count", "0/0"), inline=True)
        embed.set_footer(text=f"NovaHub Finder | Server: {data.get('job_id', 'Unknown')}")

        bot.loop.create_task(channel.send(embed=embed))
        return jsonify({"status": "success"}), 200
    return jsonify({"error": "Channel not found"}), 404

@bot.event
async def on_ready():
    print(f'✅ Logged in as {bot.user}')

def run_flask():
    # use_reloader=False prevents the "Port in use" crash
    app.run(host='0.0.0.0', port=PORT, debug=False, use_reloader=False)

if __name__ == "__main__":
    if not TOKEN:
        print("❌ ERROR: DISCORD_TOKEN is missing from Railway variables!")
    else:
        # Start Flask in a background thread
        threading.Thread(target=run_flask, daemon=True).start()
        # Start Bot
        bot.run(TOKEN)
