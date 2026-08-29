"""
Red Ticket Bot — entrypoint.

Loads config from environment variables (see .env.example), registers
the Red Ticket cog, and starts the bot.
"""

import logging
import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

from red_ticket_cog import RedTicketCog

load_dotenv()

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("red_ticket_bot")

RED_TICKET_BOT_TOKEN = os.environ["RED_TICKET_BOT_TOKEN"]

# Optional: restrict the slash command sync to a single guild for instant
# propagation during development. Leave RED_TICKET_GUILD_ID unset to sync
# globally (can take up to an hour to show up everywhere).
GUILD_ID = os.environ.get("RED_TICKET_GUILD_ID")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def setup_hook() -> None:
    await bot.add_cog(RedTicketCog(bot))

    try:
        if GUILD_ID:
            guild = discord.Object(id=int(GUILD_ID))
            bot.tree.copy_global_to(guild=guild)
            await bot.tree.sync(guild=guild)
            log.info("Synced commands to guild %s", GUILD_ID)
        else:
            await bot.tree.sync()
            log.info("Synced commands globally")
    except discord.Forbidden:
        log.error(
            "Command sync failed with 'Missing Access'. This means either the bot "
            "isn't actually a member of RED_TICKET_GUILD_ID=%s, or it was invited "
            "without the 'applications.commands' OAuth2 scope. Re-invite it with "
            "both 'bot' and 'applications.commands' checked and try again. The bot "
            "will still come online, but /redticket won't appear until this is fixed.",
            GUILD_ID,
        )


@bot.event
async def on_ready() -> None:
    log.info("Logged in as %s (ID: %s)", bot.user, bot.user.id)


if __name__ == "__main__":
    bot.run(RED_TICKET_BOT_TOKEN)
