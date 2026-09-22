import os
import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ==================================================
# CONFIGURATION DES RÔLES
# ==================================================

# Remplace les 0 par les IDs de tes rôles Discord
ROLE_REACTIONS = {
    "🟢": 0,  # Joueur
    "🔵": 0,  # Annonces
    "🔴": 0,  # Événements
    "🟣": 0,  # Giveaway
}

# L'ID du message créé avec /setup_roles
ROLE_MESSAGE_ID = None


# ==================================================
# CONNEXION DU BOT
# ==================================================

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ {bot.user} est connecté !")


# ==================================================
# /HELP
# ==================================================

@bot.tree.command(name="help", description="Affiche les commandes du bot")
async def help_command(interaction: discord.Interaction):

    embed = discord.Embed(
        title="📖 Aide — Arkadia",
        description="Voici les commandes disponibles :",
        color=discord.Color.blurple()
    )

    embed.add_field(
        name="💬 /say",
        value="Fait parler le bot.",
        inline=False
    )

    embed.add_field(
        name="🎭 /setup_roles",
        value="Crée le panneau de sélection des rôles.",
        inline=False
    )

    embed.add_field(
        name="📖 /help",
        value="Affiche cette aide.",
        inline=False
    )

    await interaction.response.send_message(
        embed=embed,
        ephemeral=True
    )


# ==================================================
# /SAY
# ==================================================

@bot.tree.command(name="say", description="Fait parler le bot")
@app_commands.describe(message="Le message que le bot doit envoyer")
async def say(interaction: discord.Interaction, message: str):

    await interaction.response.send_message(message)


# ==================================================
# /SETUP_ROLES
# ==================================================

@bot.tree.command(
    name="setup_roles",
    description="Crée le panneau de sélection des rôles"
)
@app_commands.checks.has_permissions(administrator=True)
async def setup_roles(interaction: discord.Interaction):

    global ROLE_MESSAGE_ID

    embed = discord.Embed(
        title="🎭 Choisis tes rôles",
        description=(
            "Réagis avec l'emoji correspondant au rôle que tu veux.\n\n"
            "🟢 — Joueur\n"
            "🔵 — Annonces\n"
            "🔴 — Événements\n"
            "🟣 — Giveaway\n\n"
            "Tu peux retirer ta réaction pour retirer le rôle."
        ),
        color=discord.Color.blurple()
    )

    await interaction.response.send_message(
        "✅ Panneau des rôles créé !",
        ephemeral=True
    )

    message = await interaction.channel.send(embed=embed)

    ROLE_MESSAGE_ID = message.id

    for emoji in ROLE_REACTIONS:
        await message.add_reaction(emoji)

    print(f"✅ Panel de rôles créé : {message.id}")


# ==================================================
# QUAND UNE RÉACTION EST AJOUTÉE
# ==================================================

@bot.event
async def on_raw_reaction_add(payload):

    if payload.message_id != ROLE_MESSAGE_ID:
        return

    if payload.user_id == bot.user.id:
        return

    emoji = str(payload.emoji)

    if emoji not in ROLE_REACTIONS:
        return

    guild = bot.get_guild(payload.guild_id)

    if guild is None:
        return

    role_id = ROLE_REACTIONS[emoji]

    if role_id == 0:
        print(f"⚠️ Aucun rôle configuré pour {emoji}")
        return

    role = guild.get_role(role_id)

    if role is None:
        print(f"⚠️ Rôle introuvable : {role_id}")
        return

    member = guild.get_member(payload.user_id)

    if member is None:
        try:
            member = await guild.fetch_member(payload.user_id)
        except discord.NotFound:
            return

    try:
        await member.add_roles(role)
        print(f"✅ {member} a reçu le rôle {role.name}")

    except discord.Forbidden:
        print("❌ Le bot n'a pas la permission de gérer ce rôle.")


# ==================================================
# QUAND UNE RÉACTION EST RETIRÉE
# ==================================================

@bot.event
async def on_raw_reaction_remove(payload):

    if payload.message_id != ROLE_MESSAGE_ID:
        return

    emoji = str(payload.emoji)

    if emoji not in ROLE_REACTIONS:
        return

    guild = bot.get_guild(payload.guild_id)

    if guild is None:
        return

    role_id = ROLE_REACTIONS[emoji]

    if role_id == 0:
        return

    role = guild.get_role(role_id)

    if role is None:
        return

    member = guild.get_member(payload.user_id)

    if member is None:
        try:
            member = await guild.fetch_member(payload.user_id)
        except discord.NotFound:
            return

    try:
        await member.remove_roles(role)
        print(f"✅ {member} a perdu le rôle {role.name}")

    except discord.Forbidden:
        print("❌ Le bot n'a pas la permission de gérer ce rôle.")


# ==================================================
# GESTION DES ERREURS
# ==================================================

@setup_roles.error
async def setup_roles_error(
    interaction: discord.Interaction,
    error
):

    if isinstance(error, app_commands.errors.MissingPermissions):
        await interaction.response.send_message(
            "❌ Tu dois être administrateur pour utiliser cette commande.",
            ephemeral=True
        )


# ==================================================
# LANCEMENT
# ==================================================

bot.run(TOKEN)
