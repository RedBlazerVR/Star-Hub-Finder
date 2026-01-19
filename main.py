import discord
from discord.ext import commands
from flask import Flask, request, jsonify
import threading
import os

# --- 1. CONFIGURATION ---
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID_RAW = os.getenv("CHANNEL_ID")
PORT = int(os.getenv("PORT", 5000))

# Internal database to store servers for the Hub
server_db = {}

# --- 2. BOT SETUP ---
# Requires 'Message Content Intent' enabled in Discord Developer Portal
intents = discord.Intents.default()
intents.message_content = True 
bot = commands.Bot(command_prefix="!", intents=intents)
app = Flask(__name__)

# --- 3. ROUTES ---

@app.route('/roblox-log', methods=['POST'])
def roblox_log():
    data = request.json
    job_id = data.get('job_id', 'Unknown')
    player_count = data.get('player_count', '0/0')
    player_list = data.get('player_list', 'No players found')
    
    # Save to the internal database for your Roblox Script Hub
    server_db[job_id] = {
        "players": player_count,
        "player_list": player_list
    }

    # --- DISCORD EMBED (Matches your Screenshot) ---
    channel = bot.get_channel(int(CHANNEL_ID_RAW))
    if channel:
        # Blue color 0x007bff matches the image provided
        embed = discord.Embed(title="Star Hub Notifier", color=0x007bff)
        
        # 'Name' field for the vertical list of players
        embed.add_field(name="Name", value=player_list, inline=False)
        
        # 'Players' field for the count (e.g., 7/8)
        embed.add_field(name="Players", value=player_count, inline=False)
        
        # Footer for the Server Job ID
        embed.set_footer(text=f"NovaHub Finder | Server: {job_id}")

        bot.loop.create_task(channel.send(embed=embed))
        
    return jsonify({"status": "success"}), 200

@app.route('/get-servers', methods=['GET'])
def get_servers():
    """Returns the current list of logged servers to the Roblox Hub"""
    return jsonify(server_db)

@bot.event
async def on_ready():
    print(f'✅ Bot Online: {bot.user}')

# --- 4. EXECUTION ---

def run_flask():
    # use_reloader=False prevents the 'Address already in use' error
    app.run(host='0.0.0.0', port=PORT, debug=False, use_reloader=False)

if __name__ == "__main__":
    if not TOKEN:
        print("❌ CRITICAL: DISCORD_TOKEN is missing from Railway variables!")
    else:
        # Start Web Server in background
        threading.Thread(target=run_flask, daemon=True).start()
        # Start Discord Bot
        bot.run(TOKEN)
