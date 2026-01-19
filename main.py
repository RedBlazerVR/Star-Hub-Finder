import discord
from discord.ext import commands
from flask import Flask, request, jsonify
import threading
import os

# --- 1. SETUP & CONFIG ---
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID_RAW = os.getenv("CHANNEL_ID")
# Railway provides the port via the 'PORT' environment variable
PORT = int(os.getenv("PORT", 5000))

# --- 2. DISCORD BOT SETUP ---
# Standard intents for 2026: Default + Message Content
intents = discord.Intents.default()
intents.message_content = True 

bot = commands.Bot(command_prefix="!", intents=intents)
app = Flask(__name__)

# --- 3. WEB SERVER ROUTES ---
@app.route('/roblox-log', methods=['POST'])
def roblox_log():
    if not CHANNEL_ID_RAW:
        return jsonify({"error": "CHANNEL_ID variable is missing"}), 500
    
    data = request.json
    channel = bot.get_channel(int(CHANNEL_ID_RAW))
    
    if channel:
        embed = discord.Embed(
            title="Star Hub Notifier",
            description="A new server has been indexed.",
            color=0x007bff
        )
        embed.add_field(name="Player List", value=f"```\n{data.get('player_list', 'None')}\n```", inline=False)
        embed.add_field(name="Player Count", value=data.get("player_count", "0/0"), inline=True)
        embed.set_footer(text=f"Job ID: {data.get('job_id', 'Unknown')}")

        # Send to Discord
        bot.loop.create_task(channel.send(embed=embed))
        return jsonify({"status": "success"}), 200
    
    return jsonify({"error": "Channel not found"}), 404

@bot.event
async def on_ready():
    print(f'✅ Bot is online as {bot.user}')

# --- 4. THE RUNNER ---
def run_flask():
    # use_reloader=False is the most important part! 
    # It stops Flask from starting a second time and crashing the port.
    app.run(host='0.0.0.0', port=PORT, debug=False, use_reloader=False)

if __name__ == "__main__":
    if not TOKEN:
        print("❌ ERROR: No DISCORD_TOKEN found in Railway variables.")
    else:
        # Start the Flask web server in its own thread
        flask_thread = threading.Thread(target=run_flask, daemon=True)
        flask_thread.start()
        
        # Start the Discord Bot (this stays in the main thread)
        bot.run(TOKEN)
