import discord
from discord.ext import commands
import requests
import asyncio
from datetime import datetime, timezone, timedelta
from flask import Flask
from threading import Thread
import os

# ────────────────────────────────────────────────
# RENDER KEEP ALIVE SERVER
# ────────────────────────────────────────────────
app = Flask('')

@app.route('/')
def home():
    return "TANVIR EXE PREMIUM IS ONLINE"

def run():
    # Render-এর পোর্ট ডাইনামিকভাবে ধরার জন্য
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# ────────────────────────────────────────────────
# CONFIGURATION - TANVIR EXE (PREMIUM)
# ────────────────────────────────────────────────
TOKEN = os.environ.get("BOT_TOKEN") 
API_BASE = "http://46.250.239.109:6001/api"
COOKIE_VALUE = os.environ.get("SESSION_COOKIE")

HEADERS = {
    "Content-Type": "application/json",
    "Cookie": f"session={COOKIE_VALUE}"
}

ADMIN_IDS = {1470430137131597936, 1470430137131597555}

used_free_users = set()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

# ────────────────────────────────────────────────
# UTILS & FORMATTERS
# ────────────────────────────────────────────────
def format_expiry(expire_str, duration_hours=None):
    dt = None
    if expire_str and expire_str != "Unknown":
        try:
            dt = datetime.fromisoformat(expire_str.replace("Z", "+00:00"))
        except:
            pass
            
    if dt is None and duration_hours is not None:
        dt = datetime.now(timezone.utc) + timedelta(hours=duration_hours)
    
    if dt:
        full_time = dt.strftime("%d %b %Y, %I:%M %p")
        relative_time = discord.utils.format_dt(dt, "R")
        return f"📅 `{full_time}`\n⏳ {relative_time}"
    
    return "❌ Expiry Calculation Error"

async def api_call(method, endpoint, data=None):
    url = f"{API_BASE}/{endpoint.lstrip('/')}"
    try:
        if method.upper() == "POST":
            resp = requests.post(url, json=data, headers=HEADERS, timeout=12)
        elif method.upper() == "GET":
            resp = requests.get(url, headers=HEADERS, timeout=10)
        else:
            return None, "Method Error"

        if resp.status_code == 401: return None, "Unauthorized (Session Expired)"
        
        try:
            return resp.json(), None
        except:
            return {"status": resp.status_code}, None
    except Exception as e:
        return None, str(e)

# ────────────────────────────────────────────────
# EVENTS
# ────────────────────────────────────────────────
@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="TANVIR EXE | !help"))
    print(f'>>> Logged in as: {bot.user}')
    print(f'>>> Status: Premium System Online')

# ────────────────────────────────────────────────
# COMMANDS
# ────────────────────────────────────────────────
@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title="✨ TANVIR EXE - Premium Control Panel",
        description="Official command list for TANVIR EXE system.",
        color=0x5865F2
    )
    embed.add_field(name="🎁 `!free <uid>`", value="Claim one-time 24-hour free trial", inline=False)
    embed.add_field(name="🔍 `!check <uid>`", value="View current subscription status", inline=False)
    embed.add_field(name="⚡ `!add <uid> <time>`", value="Admin only • Grant custom access (24h/7d/30d)", inline=False)
    
    embed.set_thumbnail(url=bot.user.display_avatar.url)
    embed.set_footer(text="TANVIR EXE • Professional Edition", icon_url=bot.user.display_avatar.url)
    await ctx.send(embed=embed)

@bot.command()
async def free(ctx, uid: str = None):
    if ctx.author.id in used_free_users:
        embed = discord.Embed(
            title="🛑 Access Denied",
            description="You have already claimed your **one-time free trial**.\nOnly one per user allowed.",
            color=0xE74C3C
        )
        return await ctx.send(embed=embed)

    if not uid or not uid.isdigit():
        embed = discord.Embed(
            title="⚠️ Invalid Usage",
            description="Please provide a valid numeric UID.\nExample: `!free 123456789`",
            color=0xE74C3C
        )
        return await ctx.send(embed=embed, delete_after=12)

    msg = await ctx.send(embed=discord.Embed(
        title="🔄 Processing Request",
        description=f"Connecting to server for UID **{uid}**...",
        color=0xF1C40F
    ))

    await asyncio.sleep(1.5)

    payload = {"uid": uid, "duration_hours": 24, "cost": 0.0}
    result, err = await api_call("POST", "uids", payload)

    if err:
        embed = discord.Embed(
            title="⚠️ Activation Failed",
            description=f"Could not activate UID `{uid}`.\nIt may already exist in the system.",
            color=0xE74C3C
        )
        await msg.edit(embed=embed)
    else:
        used_free_users.add(ctx.author.id)
        api_expire = result.get("expires_at") if isinstance(result, dict) else None
        expiry_info = format_expiry(api_expire, duration_hours=24)
        
        embed = discord.Embed(
            title="✅ Free Trial Activated",
            description="24-hour free access granted successfully.",
            color=0x2ECC71
        )
        embed.add_field(name="👤 Target UID", value=f"`{uid}`", inline=True)
        embed.add_field(name="💎 Plan", value="Free 24-Hour Trial", inline=True)
        embed.add_field(name="⏳ Expires", value=expiry_info, inline=False)
        
        embed.set_thumbnail(url=bot.user.display_avatar.url)
        embed.set_footer(text=f"Requested by {ctx.author.name} • TANVIR EXE", icon_url=bot.user.display_avatar.url)
        
        await msg.edit(embed=embed)

@bot.command()
async def add(ctx, uid: str = None, dur: str = None):
    if ctx.author.id not in ADMIN_IDS:
        embed = discord.Embed(
            title="🚫 Restricted Command",
            description="This command is **admin only**.",
            color=0xE74C3C
        )
        return await ctx.send(embed=embed)

    if not uid or not dur:
        embed = discord.Embed(
            title="⚠️ Missing Arguments",
            description="Usage: `!add <uid> <24h/7d/30d>`",
            color=0xE74C3C
        )
        return await ctx.send(embed=embed)

    dur = dur.lower()
    try:
        if dur.endswith("h"): hours = int(dur[:-1])
        elif dur.endswith("d"): hours = int(dur[:-1]) * 24
        else: raise ValueError
    except:
        embed = discord.Embed(
            title="🚫 Invalid Format",
            description="Use format like `24h`, `7d`, `30d` with numbers only.",
            color=0xE74C3C
        )
        return await ctx.send(embed=embed)

    msg = await ctx.send(embed=discord.Embed(
        title="🛰️ Updating Database",
        description=f"Granting **{dur.upper()}** access to UID `{uid}`...",
        color=0xF1C40F
    ))

    payload = {"uid": uid, "duration_hours": hours, "cost": 0.0}
    result, err = await api_call("POST", "uids", payload)

    if err:
        embed = discord.Embed(
            title="❌ Update Failed",
            description=f"Server error: `{err}`",
            color=0xE74C3C
        )
        await msg.edit(embed=embed)
    else:
        api_expire = result.get("expires_at") if isinstance(result, dict) else None
        expiry_info = format_expiry(api_expire, duration_hours=hours)
        
        embed = discord.Embed(
            title="🚀 Access Granted",
            description="Premium access successfully added.",
            color=0x1E90FF
        )
        embed.add_field(name="👤 UID", value=f"`{uid}`", inline=True)
        embed.add_field(name="📅 Duration", value=f"`{dur.upper()}`", inline=True)
        embed.add_field(name="⏳ Expires", value=expiry_info, inline=False)
        
        embed.set_thumbnail(url=bot.user.display_avatar.url)
        embed.set_footer(text="TANVIR EXE • Admin Action", icon_url=bot.user.display_avatar.url)
        await msg.edit(embed=embed)

@bot.command()
async def check(ctx, uid: str = None):
    if not uid:
        embed = discord.Embed(
            title="⚠️ Missing UID",
            description="Please provide a UID.\nExample: `!check 123456789`",
            color=0xE74C3C
        )
        return await ctx.send(embed=embed, delete_after=10)

    msg = await ctx.send(embed=discord.Embed(
        title="🔍 Checking Status",
        description=f"Querying database for UID **{uid}**...",
        color=0xF1C40F
    ))

    r, err = await api_call("GET", f"uids/{uid}")
    
    if err or not r:
        embed = discord.Embed(
            title="❌ Not Found",
            description=f"UID `{uid}` is **not active** in the system.",
            color=0xE74C3C
        )
        await msg.edit(embed=embed)
    else:
        exp = format_expiry(r.get("expires_at"))
        embed = discord.Embed(
            title="🔍 Subscription Status",
            color=0x3498DB
        )
        embed.add_field(name="UID", value=f"`{uid}`", inline=True)
        embed.add_field(name="Status", value="**Active** ✅", inline=True)
        embed.add_field(name="Expires", value=exp, inline=False)
        
        embed.set_thumbnail(url=bot.user.display_avatar.url)
        embed.set_footer(text=f"Checked by {ctx.author.name} • TANVIR EXE", icon_url=bot.user.display_avatar.url)
        await msg.edit(embed=embed)

# ────────────────────────────────────────────────
# RUN BOT
# ────────────────────────────────────────────────
if __name__ == "__main__":
    keep_alive() 
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("Error: BOT_TOKEN environment variable not found.")
