# Red Ticket Bot

## Setup (Docker — recommended)

1. Copy `.env.example` to `.env` and fill in:
   - `RED_TICKET_BOT_TOKEN` — from the Discord Developer Portal
   - `RED_TICKET_PUBLIC_CHANNEL_ID` — the "Red Tickets" channel
   - `RED_TICKET_LOG_CHANNEL_ID` — the private "Red Ticket Log" channel
   - `RED_TICKET_GUILD_ID` — optional, speeds up command sync while developing
2. In the Developer Portal, under OAuth2 URL Generator, check `bot` and
   `applications.commands`, and grant the bot at minimum: View Channel,
   Send Messages, Embed Links, Attach Files in both target channels.
3. `docker compose up -d --build`
4. `docker compose logs -f` to confirm it logged in and synced commands.

To stop it: `docker compose down`. To pick up code or dependency changes:
`docker compose up -d --build` again.

## Setup (plain Python)

1. `pip install -r requirements.txt`
2. Copy `.env.example` to `.env` and fill in the same values as above.
3. Same Developer Portal / OAuth2 step as above.
4. `python bot.py`

## Requirements

Needs **discord.py >= 2.6**, which added native support for select menus
(including a user picker) inside modals via `discord.ui.Label`. This is
what lets "Owner" be an in-modal @-mention picker rather than a typed
username. If you're on an older discord.py, `pip install -U discord.py`
first — the Label/UserSelect-in-modal API won't be present otherwise.

## How it works

- `/redticket` takes an `attachment` parameter — Discord's own file
  picker handles that as part of the slash command invocation.
- Submitting the command opens a modal with the remaining fields:
  Location, Item, Days to Limbo, Owner (user select), Additional Text.
- On submit, the bot posts the same embed (all five fields, including
  the mentioned Owner) to both channels, attaching the file to each.
  The only difference is the Log channel's embed also adds a
  "Submitted by" field naming whoever ran the command, plus a timestamp.
- "Days to Limbo" is validated as a whole number before either post
  goes out; invalid input gets an ephemeral error instead.

## Notes / things to adjust

- Both embeds currently show the Owner mention. If you'd rather the
  Owner field itself be scrubbed from the public post too (not just the
  submitter's identity), that's a one-line change in `build_embed()` in
  `red_ticket_cog.py`.
- The bot needs `View Channel` + `Send Messages` + `Attach Files` in the
  log channel even though it's private — permission comes from the
  channel's role/member overwrites, not from the bot being able to see
  the channel in the sidebar.
