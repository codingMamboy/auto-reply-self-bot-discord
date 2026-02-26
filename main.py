import datetime
import os
import json

import discord # discord.py-self
import human_readable
from dotenv import load_dotenv

load_dotenv()
bot = discord.Client()

STATE_FILE = "./data/state.json"
with open(STATE_FILE, "w") as f:
  f.write("{}")


def load_state():
  if not os.path.exists(STATE_FILE):
    with open(STATE_FILE, "w") as f:
      json.dump({}, f)
      return {}
  with open(STATE_FILE, "r") as f:
    return json.load(f)

def save_state(state):
  with open(STATE_FILE, "w") as f:
    json.dump(state, f, indent=4)

global messages
import data.messages as messages
online = messages.online
idle = messages.idle
dnd = messages.dnd

statuses = {
  "online": online,
  "idle": idle,
  "dnd": dnd,
}
correct = {"do_not_disturb": "dnd"}

async def get_state():
  global statuses
  return json.dumps(
    {
      "status": str(correct.get(str(bot.status), bot.status)).capitalize(),
      "means": statuses[str(correct.get(str(bot.status), bot.status)).lower()],
    },
    indent=2,
  )

@bot.event
async def on_ready():
  print(f"✅ Logged in as {bot.user.name} ({bot.user.id})")


@bot.event
async def on_message(message):
  if message.author == bot.user:
    return

  if isinstance(message.channel, discord.DMChannel):
    state = load_state()
    author_id = str(message.author.id)

    now_ts = int(datetime.datetime.now().timestamp())
    cooldown_ts = state.get(author_id, 0)
    if cooldown_ts == 0:
      print(f"No cooldown for {message.author.name} ({author_id})")

    if now_ts < cooldown_ts + 60*60*24:
      print(f"{
        human_readable.date_time(
          datetime.datetime.fromtimestamp(cooldown_ts + 60*60*24),
        )
      }"
      )
      return
    
    state[author_id] = now_ts
    save_state(state)

    print(f"DM From {message.author.name} ({author_id})")

    state = await get_state()
    if bot.status == discord.Status.online:
      await message.channel.send(
        messages.online
      )
      return
    elif bot.status == discord.Status.idle:
      await message.channel.send(
        messages.idle
      )
      return
    elif bot.status == discord.Status.dnd:
      await message.channel.send(
        messages.dnd
      )
      return
    else:
      await message.channel.send(
        messages.online
      )
      return

bot.run(os.getenv("TOKEN", ""))
