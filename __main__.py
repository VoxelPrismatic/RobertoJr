import discord
from discord.ext import commands
import json
import re
import random
import time
import os
import pickle
import traceback

from defaults import *

bot = discord.Client(intents = discord.Intents.all())
tree = discord.app_commands.CommandTree(bot)
for dir_name, dir_listing, file_listing in os.walk(ROOT_COMMANDS):
    for file_name in file_listing:
        if file_name.endswith(".py"):
            print(dir_name + "/" + file_name)
            exec(open(dir_name + "/" + file_name).read())

@bot.event
async def on_raw_reaction_add(payload):
    await handle_raw_reaction(payload)
@bot.event
async def on_raw_reaction_remove(payload):
    await handle_raw_reaction(payload)
@bot.event
async def on_ready():
    await tree.sync(guild = discord.Object(GUILD))
    await update_presence(1)
@bot.event
async def on_message(msg):
    give_xp(msg.author)

# ==================================================================================================================== #
# ==================================================================================================================== #
# ==================================================================================================================== #

presence_time = 0

async def update_presence(force = 0):
    global presence_time
    if random.randint(0, 8) != 0 and not force or time.time() - presence_time < 30:
        return
    presence = random.choice(PRESENCES)
    print("new presence", presence)
    await bot.change_presence(
        activity = discord.Activity(**presence),
        status = discord.Status.idle
    )
    presence_time = time.time()

# ==================================================================================================================== #
# ==================================================================================================================== #
# ==================================================================================================================== #

starred_timeout = {}

async def handle_raw_reaction(payload):
    await update_presence()
    if str(payload.emoji) != LISTENING_EMOJIS:
        return
    msg = await bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
    for reaction in msg.reactions:
        if str(reaction.emoji) == str(payload.emoji):
            break
        else:
            return #print("no matching emoji found")

    if str(reaction.emoji) == STAR_EMOJI:
        return await handle_add_star(msg, reaction)
    if str(reaction.emoji) == DEAD_EMOJI:
        return await handle_add_star(msg, reaction)

async def handle_add_dead(msg, reaction):
    if msg.user.bot:
        return
    if os.path.isfile(ROOT_DATA + f"dead/{msg.id}"):
        return
    if reaction.count < BAD_COUNT:
        return

    # await msg.reply("Wow, people think that comment sucked! That'll cost you 150 XP")
    give_xp(msg.author, -150)
    open(ROOT_DATA + "dead/" + str(msg.id), "w+").write("")

async def handle_remove_star(msg, reaction):
    if reaction.count > DEL_COUNT:
        return
    try:
        starred_msg = await bot.get_channel(STARBOARD).fetch_message(
            int(open(ROOT_DATA + f"stars/{msg.id}", "r").read().strip())
        )
    except FileNotFoundError:
        return
    await starred_msg.delete()
    os.remove(f"stars/{msg.id}")

async def handle_add_star(msg, reaction):
    if reaction.count < TOP_COUNT:
        return await handle_remove_star(msg, reaction)
    embed = discord.Embed(
        description = msg.content,
        color = 0xB3B7AC
    )
    embed.set_author(
        name = str(msg.author),
        icon_url = str(msg.author.avatar.url)
    )
    embed.set_footer(
        text = f"Worth {reaction.count} dice",
        icon_url = "https://cdn.discordapp.com/emojis/1088929649704312914.webp"
    )
    attachments = [att.url for att in msg.attachments]
    link_attachment = False
    try:
        att = msg.embeds[0].image.url
        if att:
            attachments.append(att)
            link_attachment = True
    except:
        pass
    if " " not in msg.content and re.search(r"^https?://.*\.(png|jpg|gif|jpeg|bmp|tiff)(\?.*)?$", msg.content.lower()):
        attachments.append(msg.content)
        link_attachment = True
    if len(attachments):
        embed.add_field(
            name = 'Attachments',
            value = ' | '.join(f"[[{i+1}]]({u})" for i, u in enumerate(attachments[:4])),
            inline = False
        )
    try:
        if not link_attachment:
            msg.attachments[0].height
        embed.set_image(url = attachments[0])
    except:
        pass

    if msg.reference:
        embed.add_field(
            name = "In response to",
            value = f"<@{msg.reference.author.id}>: {msg.reference.content[:512] + ('...' if len(msg.reference) >= 512 else '')}",
            inline = False
        )
    embed.add_field(
        name = "Credit to",
        value = f"<@{msg.author.id}> in <#{msg.channel.id}>",
        inline = False
    )
    view = discord.ui.View(timeout = None)
    view.add_item(
        discord.ui.Button(
            style = discord.ButtonStyle.grey,
            label = 'Jump to message',
            url = str(msg.jump_url)
        )
    )
    for msg_id in list(starred_timeout):
        if time.time() - starred_timeout[msg_id] > 1:
            del starred_timeout[msg_id]
    try:
        try:
            starred_msg = await bot.get_channel(STARBOARD).fetch_message(
                int(open(ROOT_DATA + f"stars/{msg.id}", "r").read().strip())
            )
            if starred_msg.id in starred_timeout:
                return
            await starred_msg.edit(embed = embed, view = view)
        except:
            starred_msg = await bot.get_channel(STARBOARD).send(embed = embed, view = view)
            give_xp(msg.author, 500)
            open(ROOT_DATA + f"stars/{msg.id}", "w+").write(str(starred_msg.id))
    except Exception as ex:
        print(ex)


# ==================================================================================================================== #
# ==================================================================================================================== #
# ==================================================================================================================== #


if __name__ == "__main__":
    bot.run("MTEwMzgwMDcyNTAyNjM3MzcwMg.GUyg5x.FWgILjuBzh_oln8zk9MqTIpQx8qJoAsEva6j4U")
