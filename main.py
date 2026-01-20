import discord
from discord.ext import commands
from flask import Flask, request, jsonify
import threading
import os
import time

# --- 1. CONFIGURATION ---
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID_RAW = os.getenv("CHANNEL_ID")
PORT = int(os.getenv("PORT", 5000))

# Internal database: { job_id: {"players": "6/8", "player_list": "...", "last_updated": 123456} }
server_db = {}
EXPIRY_TIME = 600  # 10 minutes in seconds

# --- 2. BOT SETUP ---
intents = discord.Intents.default()
intents.message_content = True 
bot = commands.Bot(command_prefix="!", intents=intents)
app = Flask(__name__)

# --- 3. AUTO-CLEANUP LOGIC ---
def start_cleanup_task():
    """Background thread to remove inactive servers automatically."""
    def cleanup():
        while True:
            current_time = time.time()
            # Find IDs older than 10 minutes
            expired_ids = [
                jid for jid, info in server_db.items() 
                if current_time - info.get('last_updated', 0) > EXPIRY_TIME
            ]
            for jid in expired_ids:
                del server_db[jid]
            time.sleep(30) # Check every 30 seconds
            
    threading.Thread(target=cleanup, daemon=True).start()

# --- 4. ROUTES ---

@app.route('/roblox-log', methods=['POST'])
def roblox_log():
    data = request.json
    job_id = data.get('job_id', 'Unknown')
    player_count = data.get('player_count', '0/0')
    player_list = data.get('player_list', 'None')
    
    # Check if any rares were actually found
    if player_list == "None" or not player_list:
        return jsonify({"status": "ignored"}), 200

    # Save to the internal database with a timestamp for cleanup
    server_db[job_id] = {
        "players": player_count,
        "player_list": player_list,
        "last_updated": time.time()
    }

    # --- DISCORD EMBED ---
    channel = bot.get_channel(int(CHANNEL_ID_RAW))
    if channel:
        # Blue color 0x007bff
        embed = discord.Embed(title="Star Hub Notifier", color=0x007bff)
        embed.add_field(name="Name", value=player_list, inline=False)
        embed.add_field(name="Players", value=player_count, inline=False)
        embed.set_footer(text=f"NovaHub Finder | Server: {job_id}")

        bot.loop.create_task(channel.send(embed=embed))
        
    return jsonify({"status": "success"}), 200

@app.route('/get-servers', methods=['GET'])
def get_servers():
    """Returns the current list of logged servers to the Roblox Hub"""
    # Create a clean version of the DB without the timestamps to send to Roblox
    clean_data = {}
    for jid, info in server_db.items():
        clean_data[jid] = {
            "players": info["players"],
            "player_list": info["player_list"]
        }
    return jsonify(clean_data)

@bot.event
async def on_ready():
    print(f'✅ Bot Online: {bot.user}')

# --- 5. EXECUTION ---

def run_flask():
    app.run(host='0.0.0.0', port=PORT, debug=False, use_reloader=False)

if __name__ == "__main__":
    if not TOKEN:
        print("❌ CRITICAL: DISCORD_TOKEN is missing!")
    else:
        # Start the background systems
        start_cleanup_task()
        threading.Thread(target=run_flask, daemon=True).start()
        # Start Discord Bot
        bot.run(TOKEN)
