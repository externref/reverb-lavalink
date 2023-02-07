from __future__ import annotations

import os

import hikari

import reverb

TOKEN = os.environ["DEV_TOKEN"]
HOST = "127.0.0.0"
PORT = 2333
PASSWORD = "youshallnotpass"
BOT_ID = 964195658468835358

bot = hikari.GatewayBot(TOKEN, logs="DEBUG")
lavalink: reverb.LavalinkClient | None = None


@bot.listen()
async def setup_lavalink(_: hikari.StartingEvent) -> None:
    global lavalink
    lavalink = await reverb.LavalinkClient.build(
        host=HOST, port=PORT, password=PASSWORD, application_id=BOT_ID, bot=bot
    )


@bot.listen()
async def lavalink_ready(event: reverb.LavalinkReadyEvent) -> None:
    print("connected to lavalink!")


@bot.listen()
async def player_update(event: reverb.PlayerUpdateEvent) -> None:
    print(event.data)


bot.run()
