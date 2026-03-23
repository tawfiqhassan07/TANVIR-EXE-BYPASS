import discord
from discord.ext import commands
import requests
from datetime import datetime
import os
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

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="!free <uid>"))
    print(f'Logged in as {bot.user.name}')

@bot.command()
async def free(ctx, uid: str = None):
    if uid is None:
        embed = discord.Embed(
            title="⚠️ Command Usage",
            description="Please provide a valid UID.\nExample: `!free 12345678`",
            color=0xFFA500
        )
        await ctx.send(embed=embed)
        return

    if len(uid) < 6 or len(uid) > 12:
        embed = discord.Embed(
            title="🚫 Access Denied",
            description="The UID length must be between 6 and 12 characters.",
            color=0xFF0000
        )
        await ctx.send(embed=embed)
        return

    payload = {
        "uid": uid,
        "duration": 1,
        "hours": 24,
        "cost": 0.00
    }

    headers = {
        "Cookie": AUTH_COOKIE,
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = requests.post(API_URL, json=payload, headers=headers, timeout=10)
        
        if response.status_code in [200, 201]:
            embed = discord.Embed(
                title="⚡ ACCESS GRANTED",
                description=f"Successfully activated UID: **{uid}**",
                color=0x00FFFF,
                timestamp=datetime.utcnow()
            )
            embed.set_author(name="TANVIR EXE SYSTEM", icon_url=bot.user.display_avatar.url)
            embed.add_field(name="📶 STATUS", value="`ACTIVE`", inline=True)
            embed.add_field(name="⏳ DURATION", value="`24 HOURS`", inline=True)
            embed.add_field(name="💎 PLAN", value="`FREE BYPASS`", inline=True)
            embed.set_thumbnail(url=bot.user.display_avatar.url)
            embed.set_footer(text="Developed by TANVIR", icon_url=bot.user.display_avatar.url)
            
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                title="❌ System Error",
                description=f"Failed to connect to dashboard. Code: {response.status_code}",
                color=0xFF0000
            )
            await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send(f"**Error:** {str(e)}")

def start_bot():
    Thread(target=run_flask).start()
    bot.run(TOKEN)

if __name__ == "__main__":
    start_bot()
