import discord
from discord.ext import commands
from flask import Flask, request, jsonify
import threading
import os

# 1. SETUP FROM RAILWAY VARIABLES
# These names must match exactly what you typed in the Railway Variables tab
TOKEN = os.getenv("DISCORD_TOKEN")
# We use int() because Discord IDs are numbers, but environment variables are strings
CHANNEL_ID = int(os.getenv("CHANNEL_ID")) 

bot = commands.Bot(command_prefix="!", intents=discord.Intents.default())
app = Flask(__name__)

@app.route('/roblox-log', methods=['POST'])
def roblox_log():
    data = request.json
    channel = bot.get_channel(CHANNEL_ID)
    
    if channel:
        # Create the Embed to match your screenshot
        embed = discord.Embed(
            title="Star Hub Notifier",
            description="A new server has been indexed.",
            color=0x007bff # A nice blue color
        )
        
        # Adding the data fields
        embed.add_field(name="Name", value=f"```\n{data.get('player_list', 'None')}\n```", inline=False)
        embed.add_field(name="Players", value=data.get("player_count", "0/0"), inline=True)
        
        # Footer shows the server ID
        embed.set_footer(text=f"Star Hub Finder | Server: {data.get('job_id', 'Unknown')}")

        # Send to Discord
        bot.loop.create_task(channel.send(embed=embed))
    
    return jsonify({"status": "success"}), 200

def run_flask():
    # Railway uses the PORT variable automatically
    port = int(os.getenv("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    # Start the web server (Flask) in the background
    threading.Thread(target=run_flask, daemon=True).start()
    # Start the Discord Bot
    bot.run(TOKEN)
