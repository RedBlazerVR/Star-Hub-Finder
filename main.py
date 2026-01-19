import discord
from discord.ext import commands
from flask import Flask, request, jsonify
import threading
import os
import time

# 1. SETUP VARIABLES
TOKEN = os.getenv("DISCORD_TOKEN")
# We use .get() to avoid crashing if the variable isn't set yet
CHANNEL_ID_RAW = os.getenv("CHANNEL_ID")
PORT = int(os.getenv("PORT", 5000))

# 2. DISCORD INTENTS (Fixes the 'PrivilegedIntentsRequired' error)
# Note: You MUST still enable these in the Discord Developer Portal!
intents = discord.Intents.default()
intents.message_content = True  # Allows bot to see message data
intents.members = True          # Optional but helpful for logging

bot = commands.Bot(command_prefix="!", intents=intents)
app = Flask(__name__)

@app.route('/roblox-log', methods=['POST'])
def roblox_log():
    if not CHANNEL_ID_RAW:
        return jsonify({"error": "CHANNEL_ID variable is missing in Railway"}), 500
    
    data = request.json
    channel = bot.get_channel(int(CHANNEL_ID_RAW))
    
    if channel:
        embed = discord.Embed(
            title="NovaHub Notifier",
            description="A new server has been indexed.",
            color=0x007bff
        )
        embed.add_field(name="Player List", value=f"```\n{data.get('player_list', 'None')}\n```", inline=False)
        embed.add_field(name="Count", value=data.get("player_count", "0/0"), inline=True)
        embed.set_footer(text=f"Server ID: {data.get('job_id', 'Unknown')}")

        # Send to Discord using the bot's event loop
        bot.loop.create_task(channel.send(embed=embed))
        return jsonify({"status": "success"}), 200
    return jsonify({"error": "Bot could not find that channel"}), 404

@bot.event
async def on_ready():
    print(f'✅ Bot is online: {bot.user}')

def run_flask():
    # use_reloader=False is REQUIRED to prevent the Port 5000 "Address already in use" error
    app.run(host='0.0.0.0', port=PORT, debug=False, use_reloader=False)

if __name__ == "__main__":
    if not TOKEN:
        print("❌ TOKEN MISSING")
    else:
        # Run Flask in the background
        threading.Thread(target=lambda: app.run(host='0.0.0.0', port=PORT, use_reloader=False), daemon=True).start()
        # Run Bot in the foreground
        bot.run(TOKEN)
