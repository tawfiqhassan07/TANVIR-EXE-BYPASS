import discord
from discord.ext import commands
import requests
import datetime
from flask import Flask
from threading import Thread
import os

# --- Flask Server (Keep Alive) ---
app = Flask('')

@app.route('/')
def home():
    return "I am alive!"

def run():
    # Render সাধারণত 8080 বা 10000 পোর্ট ব্যবহার করে
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- Discord Bot Code ---
# ⚠️ টোকেনটি দ্রুত রিসেট করুন এবং এখানে নতুন টোকেন দিন
TOKEN = 'MTQ3NDQ0NjAwNDM2NjYxMDc3Nw.G7Tlkv.LOjJFQ0LA-ytR5NMd2pRbKdr3UyLA5riRsXBuI'
CLAIM_URL = 'http://92.118.206.166:30282/claim_free_access'

COLOR_MAIN = 0x5865F2  
COLOR_SUCCESS = 0x2ECC71 
COLOR_ERROR = 0xE74C3C   
COLOR_PROCESS = 0xF1C40F 

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.competing, 
        name="TANVIR EXE BYPASS"
    ))
    print(f'>>> System Online: {bot.user}')

@bot.command()
async def free(ctx, uid: str = None):
    if uid is None:
        embed = discord.Embed(
            title="⚠️ Access Denied",
            description="```Usage: !free <UID_NUMBER>```",
            color=COLOR_ERROR
        )
        await ctx.send(embed=embed)
        return

    if not uid.isdigit():
        embed = discord.Embed(
            title="🚫 Invalid Format",
            description="The UID provided is not a valid number.",
            color=COLOR_ERROR
        )
        await ctx.send(embed=embed)
        return

    loading_embed = discord.Embed(
        title="🔄 TANVIR EXE SYSTEM",
        description=f"Authenticating UID: **{uid}**\nPlease wait while we process your request...",
        color=COLOR_PROCESS
    )
    status_msg = await ctx.send(embed=loading_embed)

    try:
        payload = {'uid': uid}
        response = requests.post(CLAIM_URL, data=payload, timeout=12)

        if response.status_code == 200:
            result = response.json()
            is_ok = result.get('success')
            api_msg = result.get('message', 'Process completed.')

            final_embed = discord.Embed(
                title="⚡ TANVIR EXE FREE BYPASS",
                description="Bypass access has been synchronized with the server.",
                timestamp=datetime.datetime.utcnow(),
                color=COLOR_SUCCESS if is_ok else COLOR_ERROR
            )
            
            final_embed.add_field(name="📡 Status", value=f"```yaml\n{api_msg}\n```", inline=False)
            final_embed.add_field(name="👤 Target UID", value=f"`{uid}`", inline=True)
            final_embed.add_field(name="🔑 Access Type", value="`3 Days Free`", inline=True)
            
            if bot.user.avatar:
                final_embed.set_thumbnail(url=bot.user.avatar.url)
            
            final_embed.set_footer(text=f"Requested by {ctx.author.name} • Developed by TANVIR", icon_url=bot.user.avatar.url if bot.user.avatar else None)

            await status_msg.edit(embed=final_embed)
        else:
            raise Exception(f"Server returned {response.status_code}")

    except Exception as e:
        error_embed = discord.Embed(
            title="🧨 System Exception",
            description=f"An error occurred while connecting to the bypass server.",
            color=COLOR_ERROR
        )
        error_embed.add_field(name="Error Detail", value=f"`{str(e)}`")
        await status_msg.edit(embed=error_embed)

# --- Start Bot with Keep Alive ---
if __name__ == "__main__":
    keep_alive() # Flask সার্ভার চালু করবে

    bot.run(TOKEN)
