import discord
from discord.ext import commands
from flask import Flask, request, jsonify
import threading
import os

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID_RAW = os.getenv("CHANNEL_ID")
PORT = int(os.getenv("PORT", 5000))

# --- NEW: GLOBAL SERVER LIST ---
# This keeps track of servers found by ANYONE using the script
server_database = {} 

intents = discord.Intents.default()
intents.message_content = True 
bot = commands.Bot(command_prefix="!", intents=intents)
app = Flask(__name__)

# --- ROUTE 1: RECEIVE DATA FROM ROBLOX ---
@app.route('/roblox-log', methods=['POST'])
def roblox_log():
    data = request.json
    job_id = data.get('job_id')
    
    # Save/Update the server in our "Database"
    server_database[job_id] = {
        "players": data.get("player_count"),
        "list": data.get("player_list"),
        "last_seen": os.times()[4] # Timestamp
    }
    
    # Send to Discord (Existing code)
    channel = bot.get_channel(int(CHANNEL_ID_RAW))
    if channel:
        embed = discord.Embed(title="NovaHub Indexer", color=0x00ff00)
        embed.add_field(name="Players", value=data.get("player_count"))
        embed.set_footer(text=f"Server: {job_id}")
        bot.loop.create_task(channel.send(embed=embed))
        
    return jsonify({"status": "indexed"}), 200

# --- ROUTE 2: SEND DATABASE TO THE HUB ---
@app.route('/get-servers', methods=['GET'])
def get_servers():
    return jsonify(server_database)

@bot.event
async def on_ready():
    print(f'✅ Bot is online: {bot.user}')

def run_flask():
    app.run(host='0.0.0.0', port=PORT, debug=False, use_reloader=False)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    bot.run(TOKEN)
