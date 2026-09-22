import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"✅ {bot.user} est connecté !")


@bot.event
async def on_raw_reaction_add(payload):
    print(f"Réaction ajoutée : {payload.emoji}")


@bot.event
async def on_raw_reaction_remove(payload):
    print(f"Réaction retirée : {payload.emoji}")


bot.run(TOKEN)
