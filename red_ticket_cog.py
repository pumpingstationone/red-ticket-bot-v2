"""
Red Ticket Bot — /redticket command, modal, and dual-channel posting.

Flow
----
1. /redticket attachment:<file>   -- attachment is picked natively by
   Discord's slash-command UI, no extra step needed for that part.
2. Submitting the command immediately opens a modal with the remaining
   fields: Location, Item, Days to Limbo, Owner (user picker), and
   Additional Text.
3. On submit, two embeds are built from the same field data and posted:
     - Red Tickets (public)   -- the form fields, no submitter identity.
     - Red Ticket Log (private) -- the same fields, plus who submitted
       the ticket and when.

Requires discord.py >= 2.6, which added native support for select
menus (including UserSelect) inside modals via discord.ui.Label. Older
versions of discord.py cannot run this file as written.
"""

import os
from datetime import datetime, timezone

import discord
from discord import app_commands
from discord.ext import commands

PUBLIC_CHANNEL_ID = int(os.environ["RED_TICKET_PUBLIC_CHANNEL_ID"])
LOG_CHANNEL_ID = int(os.environ["RED_TICKET_LOG_CHANNEL_ID"])

RED_COLOR = discord.Color.red()


class RedTicketModal(discord.ui.Modal, title="Red Ticket Details"):
    def __init__(self, attachment: discord.Attachment):
        super().__init__()
        self.attachment = attachment

        self.location_input = discord.ui.TextInput(
            placeholder="e.g. Woodshop, Bay 3",
            max_length=100,
            required=True,
        )
        self.item_input = discord.ui.TextInput(
            placeholder="e.g. Table saw",
            max_length=100,
            required=True,
        )
        self.days_input = discord.ui.TextInput(
            placeholder="e.g. 14",
            max_length=5,
            required=True,
        )
        self.additional_input = discord.ui.TextInput(
            style=discord.TextStyle.paragraph,
            required=False,
            max_length=1000,
        )
        self.owner_select = discord.ui.UserSelect(
            min_values=1,
            max_values=1,
            placeholder="Select the owner",
        )

        self.add_item(discord.ui.Label(text="Location", component=self.location_input))
        self.add_item(discord.ui.Label(text="Item", component=self.item_input))
        self.add_item(discord.ui.Label(text="Days to Limbo", component=self.days_input))
        self.add_item(discord.ui.Label(text="Owner", component=self.owner_select))
        self.add_item(
            discord.ui.Label(
                text="Additional Text",
                description="Optional",
                component=self.additional_input,
            )
        )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        days_raw = self.days_input.value.strip()
        if not days_raw.isdigit():
            await interaction.response.send_message(
                f'"Days to Limbo" must be a whole number — got "{days_raw}".',
                ephemeral=True,
            )
            return

        owner = self.owner_select.values[0]
        location = self.location_input.value.strip()
        item = self.item_input.value.strip()
        additional = self.additional_input.value.strip() or None

        await interaction.response.defer(ephemeral=True, thinking=True)

        public_channel = interaction.client.get_channel(PUBLIC_CHANNEL_ID)
        log_channel = interaction.client.get_channel(LOG_CHANNEL_ID)
        if public_channel is None:
            public_channel = await interaction.client.fetch_channel(PUBLIC_CHANNEL_ID)
        if log_channel is None:
            log_channel = await interaction.client.fetch_channel(LOG_CHANNEL_ID)

        filename = self.attachment.filename

        def build_embed() -> discord.Embed:
            embed = discord.Embed(title="🔴 Red Ticket", color=RED_COLOR)
            embed.add_field(name="Location", value=location, inline=True)
            embed.add_field(name="Item", value=item, inline=True)
            embed.add_field(name="Days to Limbo", value=days_raw, inline=True)
            embed.add_field(name="Owner", value=owner.mention, inline=True)
            if additional:
                embed.add_field(name="Additional Text", value=additional, inline=False)
            embed.set_image(url=f"attachment://{filename}")
            return embed

        public_embed = build_embed()
        public_file = await self.attachment.to_file()
        await public_channel.send(
            embed=public_embed,
            file=public_file,
            allowed_mentions=discord.AllowedMentions(users=[owner]),
        )

        log_embed = build_embed()
        log_embed.add_field(name="Submitted by", value=f"{interaction.user.mention} ({interaction.user})", inline=False)
        log_embed.timestamp = datetime.now(timezone.utc)
        log_file = await self.attachment.to_file()
        await log_channel.send(
            embed=log_embed,
            file=log_file,
            allowed_mentions=discord.AllowedMentions(users=[owner]),
        )

        await interaction.followup.send("Red ticket submitted.", ephemeral=True)


class RedTicketCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="redticket", description="File a red ticket for an item headed to limbo.")
    @app_commands.describe(attachment="A photo of the item/tag")
    async def redticket(self, interaction: discord.Interaction, attachment: discord.Attachment) -> None:
        await interaction.response.send_modal(RedTicketModal(attachment))


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(RedTicketCog(bot))
