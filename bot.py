import discord
from discord.ext import commands
import requests
from datetime import datetime
import os
import asyncio
import random
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Bot is online!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

TOKEN = os.getenv('DISCORD_TOKEN')
API_URL = 'http://46.250.239.109:6001/api/create-uid'
AUTH_COOKIE = os.getenv('AUTH_COOKIE')
PASTEBIN_URL = os.getenv('PASTEBIN_URL')

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

def check_status():
    try:
        response = requests.get(PASTEBIN_URL, timeout=5)
        return response.text.strip().upper()
    except:
        return "OFF"

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="!free <uid>"))
    print(f'Logged in as {bot.user.name}')

@bot.command()
async def free(ctx, uid: str = None):
    status = check_status()
    if status != "ON":
        embed = discord.Embed(title="🚫 SYSTEM EXPIRED", description="**Free bypass access has ended.**\nPlease contact the developer to purchase a premium license.", color=0xFF0000, timestamp=datetime.utcnow())
        embed.set_author(name="TANVIR EXE", icon_url=bot.user.display_avatar.url)
        embed.add_field(name="📢 NOTICE", value="`FREE BYPASS ENDED`", inline=False)
        embed.set_footer(text="Developed by TANVIR", icon_url=bot.user.display_avatar.url)
        await ctx.send(embed=embed)
        return
    if uid is None:
        await ctx.send("⚠️ Usage: `!free <uid>`")
        return
    payload = {"uid": uid, "duration": 1, "hours": 24, "cost": 0.00}
    headers = {"Cookie": AUTH_COOKIE, "Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
    try:
        response = requests.post(API_URL, json=payload, headers=headers, timeout=10)
        if response.status_code in [200, 201]:
            embed = discord.Embed(title="⚡ ACCESS GRANTED", description=f"UID: **{uid}** activated!", color=0x00FFFF, timestamp=datetime.utcnow())
            embed.set_author(name="TANVIR EXE SYSTEM", icon_url=bot.user.display_avatar.url)
            embed.set_footer(text="Developed by TANVIR", icon_url=bot.user.display_avatar.url)
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"❌ Error: {response.status_code}")
    except Exception as e:
        await ctx.send(f"**Error:** {str(e)}")

async def start_main():
    Thread(target=run_flask).start()
    while True:
        try:
            await bot.start(TOKEN)
        except discord.errors.HTTPException as e:
            if e.status == 429:
                wait_time = random.randint(60, 120)
                print(f"Rate limited. Waiting {wait_time}s...")
                await asyncio.sleep(wait_time)
            else:
                print(f"Connection error: {e}")
                await asyncio.sleep(10)
        except Exception as e:
            print(f"Bot stopped: {e}")
            await asyncio.sleep(10)

if __name__ == "__main__":
    try:
        asyncio.run(start_main())
    except KeyboardInterrupt:
        pass
