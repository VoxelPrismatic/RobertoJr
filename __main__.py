try:
    import os
    import discord
    from discord.ext import commands
    import json
    import re
    import random
    import time
    import pickle
    import traceback
    import math
    import subprocess
    import asyncio
    import pytz
    import datetime
    from phevaluator import evaluate_cards
except:
    os.system("python3 -m pip install -U pip discord aiohttp[speedups] phevaluator pytz --user")
    exit()

from defaults import *

for d in DATA_DIRS:
    os.makedirs(ROOT.DATA + d, exist_ok = True)

bot = discord.Client(intents = discord.Intents.all())
tree = discord.app_commands.CommandTree(bot)
for dir_name, dir_listing, file_listing in os.walk(ROOT.COMMANDS):
    for file_name in file_listing:
        if file_name.endswith(".py"):
            print(dir_name + "/" + file_name)
            exec(open(dir_name + "/" + file_name).read())

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

@tree.command(
    name = "tiers",
    description = "Understand the roles and tiers available in the Timcast Discord server",
    guild = ID.GUILD_OBJ
)
@discord.app_commands.guild_only()
async def com_tiers(interaction: discord.Interaction):
    ephemeral = (interaction.channel.id not in ID.CHANNEL.BOTS) and not interaction.permissions.administrator
    msg = f"""
<@&{ID.ROLE.TIER.LOUNGE}> - $10/mo

**Call in or ask questions on the After Show:**
<@&{ID.ROLE.TIER.VIP}> - $10/mo for 6 months

<@&{ID.ROLE.TIER.SILVER}> - $25/mo

<@&{ID.ROLE.TIER.ELITE}> - $100/mo"""
    embed = discord.Embed(
        title = "Roles",
        description = msg,
        color = 0xff0088
    )
    return await interaction.response.send_message(embed = embed, ephemeral = ephemeral)

@tree.command(
    name = "onboarding",
    description = "Help someone else with onboarding",
    guild = ID.GUILD_OBJ
)
@discord.app_commands.choices(
    phase = [
        discord.app_commands.Choice(name = "/link", value = 1),
        discord.app_commands.Choice(name = "/verify", value = 2),
        discord.app_commands.Choice(name = "Both /link & /verify", value = 3),
        discord.app_commands.Choice(name = "Welcome/Congrats", value = 4),
        discord.app_commands.Choice(name = "Trailer", value = 8),
    ]
)
@discord.app_commands.describe(
    member = "Who to ping with help"
)
@discord.app_commands.guild_only()
async def com_help_onboarding(interaction: discord.Interaction, member: discord.User, phase: int = 3):
    ephemeral = (interaction.channel.id not in ID.CHANNEL.BOTS) and not interaction.permissions.administrator
    try:
        member = await interaction.guild.fetch_member(member.id)
    except discord.errors.NotFound:
        return await interaction.response.send_message(f"<@{member.id}> seems to have left the server")

    # if member.is_on_mobile():
    #     send_inst = "Then, hit the send button"
    #     print("MOBILE!")
    # else:
    #     send_inst = "Then, press the enter key"
    # print(member.mobile_status)
    # print(member.desktop_status)
    # print(member.web_status)
    # print(member.activity)

    if phase & 1:
        msg = f"""Hello, <@{member.id}>!
**Thanks for joining the Timcast Discord server!**

\x31\ufe0f\u20e3 To get started, click this button: >>> </link:{ID.COMMAND.LINK}> <<<
Then send the message. On PC, hit the enter key. On mobile, press {ID.EMOJI.SEND}

\x32\ufe0f\u20e3 Follow the instructions from BeanieBot to provide your email
You will receive a verification code, be sure to check your spam folder"""
    else:
        msg = f"<@{member.id}>"

    if phase & 2:
        msg += f"""\


\x33\ufe0f\u20e3 Once you receive your code, click this button: >>> </verify:{ID.COMMAND.VERIFY}> <<<
Then send the message. On PC, hit the enter key. On mobile, press {ID.EMOJI.SEND}

\x34\ufe0f\u20e3 Enter the code you just received in this dialog box and hit submit.
And that's it!"""

    if phase & 4:
        msg = f"""<@{member.id}>, welcome aboard!

\x31\ufe0f\u20e3 You can now access different chats available on the left side of your screen
On mobile, swipe the chat screen to the right

\x32\ufe0f\u20e3 If you feel overwhelmed, you can hide certain channels by clicking here >>> <id:browse> <<<
Or, simply select the ones you may be interested in

\x33\ufe0f\u20e3 Be sure to drop by <#{ID.CHANNEL.IRL}> and say hi!"""

    if phase & 8:
        msg = "\n\nhttps://media.discordapp.net/attachments/1083510074032533555/1176241164811243580/StuckInBotChannel.mp4"
#        msg += "\n<mobile>" if member.is_on_mobile() else "\n[pc]"

    if interaction.channel.id == ID.CHANNEL.BOT:
        return await interaction.response.send_message(msg)

    await bot.get_channel(ID.CHANNEL.BOT).send(msg)
    return await interaction.response.send_message(f"Instructions sent in <#{ID.CHANNEL.BOT}>")


# ==================================================================================================================== #
# ==================================================================================================================== #
# ==================================================================================================================== #

starred_timeout = {}

async def handle_reaction(msg, reaction, user):
    if msg.channel.category.id == ID.CATEGORY.DEBATE:
        if str(reaction.emoji) in ID.EMOJI.LISTENING:
            if user.id == bot.user.id:
                return
            if user in msg.channel.overwrites:
                return await reaction.remove(user)

    if str(reaction.emoji) == ID.EMOJI.STAR:
        if msg.author == user:
            return await reaction.remove(user)
        return await handle_add_star(msg, reaction)

    if str(reaction.emoji) == ID.EMOJI.DEAD:
        return await handle_add_dead(msg, reaction)


async def handle_raw_reaction(payload):
    await update_presence()
    if str(payload.emoji) not in ID.EMOJI.LISTENING:
        return
    msg = await bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
    user = bot.get_guild(payload.guild_id).get_member(payload.user_id)
    if user is None:
        user = await bot.get_guild(payload.guild_id).fetch_member(payload.user_id)

    for reaction in msg.reactions:
        if str(reaction.emoji) == str(payload.emoji):
            break
    else:
        return print("no matching emoji found")

    return await handle_reaction(msg, reaction, user)

async def handle_add_dead(msg, reaction):
    if msg.author.bot:
        return
    if os.path.isfile(ROOT.DATA + f"dead/{msg.id}"):
        return
    if reaction.count < BAD_COUNT:
        return

    give_xp(msg.author, -150)
    # await msg.reply("Wow, people think that comment sucked! That'll cost you 150 XP")
    open(ROOT.DATA + "dead/" + str(msg.id), "w+").write("")

async def handle_remove_star(msg, reaction):
    if reaction.count > DEL_COUNT:
        return
    try:
        starred_msg = await bot.get_channel(ID.CHANNEL.STARBOARD).fetch_message(
            int(open(ROOT.DATA + f"stars/{msg.id}", "r").read().strip())
        )
    except FileNotFoundError:
        return
    except:
        starred_msg = None
    os.remove(ROOT.DATA + f"stars/{msg.id}")
    give_xp(msg.author, -500)
    if starred_msg:
        await starred_msg.delete()

async def handle_add_star(msg, reaction):
    if reaction.count < TOP_COUNT:
        return await handle_remove_star(msg, reaction)
    embed = discord.Embed(
        description = msg.content,
        color = 0xB3B7AC
    )
    embed.set_author(
        name = str(msg.author),
        icon_url = str((msg.author.guild_avatar or msg.author.avatar or msg.author.default_avatar).url)
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
            value = ' | '.join(f"[[{u.split('?')[0].rsplit('.')[-1]}]]({u})" for u in attachments[:4]),
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
            starred_msg = await bot.get_channel(ID.CHANNEL.STARBOARD).fetch_message(
                int(open(ROOT.DATA + f"stars/{msg.id}", "r").read().strip())
            )
            if starred_msg.id in starred_timeout:
                return
            await starred_msg.edit(embed = embed, view = view)
        except:
            starred_msg = await bot.get_channel(ID.CHANNEL.STARBOARD).send(embed = embed, view = view)
            give_xp(msg.author, 500)
            open(ROOT.DATA + f"stars/{msg.id}", "w+").write(str(starred_msg.id))
    except Exception as ex:
        print(ex)


# ==================================================================================================================== #
# ==================================================================================================================== #
# ==================================================================================================================== #

cached_messages = []
INTERACTION_COMMANDS = {}
def COMMAND_STR(cmd):
    return f"</{cmd}:{INTERACTION_COMMANDS[cmd]}>"

@bot.event
async def on_reaction_add(reaction, user):
    global cached_messages
    cached_messages.append(reaction.message.id)
    return await handle_reaction(reaction.message, reaction, user)

@bot.event
async def on_reaction_remove(reaction, user):
    global cached_messages
    cached_messages.append(reaction.message.id)
    if reaction.count == 0:
        return print("[Cache] This reaction emoji was cleared")
    return await handle_reaction(reaction.message, reaction, user)

@bot.event
async def on_raw_reaction_add(payload):
    global cached_messages
    if payload.message_id in cached_messages:
        return cached_messages.remove(payload.message_id)
    await handle_raw_reaction(payload)

@bot.event
async def on_raw_reaction_remove(payload):
    global cached_messages
    if payload.message_id in cached_messages:
        return cached_messages.remove(payload.message_id)
    await handle_raw_reaction(payload)

@bot.event
async def on_ready():
    global INTERACTION_COMMANDS
    await tree.sync(guild = ID.GUILD_OBJ)
    for cmd in await tree.fetch_commands(guild = ID.GUILD_OBJ):
        INTERACTION_COMMANDS[cmd.name] = cmd.id
        print(cmd)
    await update_presence(1)

@bot.event
async def on_message(msg):
    if msg.author.bot and msg.author.id != ID.USER.BEANIE_BOT:
        return
    give_xp(msg.author)
    if msg.channel.id == ID.CHANNEL.IRL:
        return await handle_irl_channel(msg)

    if msg.channel.category.id == ID.CATEGORY.DEBATE:
        return await handle_debate_msg(msg)

    if msg.channel.id != ID.CHANNEL.BOT:
        return

    if msg.author.id == ID.USER.BEANIE_BOT:
        if msg.interaction.name == "verify":
            pass #ID.COMMAND.VERIFY = msg.interaction.id

        elif msg.interaction.name == "link":
            pass #ID.COMMAND.LINK = msg.interaction.id

        elif msg.interaction.name == "refresh":
            pass #ID.COMMAND.REFRESH = msg.interaction.id
            if re.search(r"\d+ not found", msg.content):
                return await msg.reply(f"<@{msg.interaction.user.id}>, use </link:{ID.COMMAND.LINK}> and </verify:{ID.COMMAND.VERIFY}> to reconnect your account")

        return

#    now = datetime.datetime.utcnow().astimezone(pytz.timezone("America/Chicago"))
#    if now.hour not in [18, 19, 20, 21, 22, 23, 0, 1, 2, 3, 4, 5, 6]:
#        return

    if re.search(r'^[ "]*/? *[lL][iI][nN][kK]', msg.content) or re.search(r"[\d\w_.-]+@[\d\w_.-]+(\.\w+)+", msg.content):
        await msg.reply(
            f"Woops! Try clicking here: >>> </link:{ID.COMMAND.LINK}> <<<, wait a few seconds, then send the message.\n" + \
            f"On PC, hit the enter key. On mobile, press {ID.EMOJI.SEND}\n" + \
            "## Please do not place your email here\nyou will place it in a popup like below: "
            "https://media.discordapp.net/attachments/1164048175976415262/1200268179524554902/image.png"
        )
        if "@" in msg.content:
            await msg.delete()
        return

    if re.search(r'^[ "]*/? *[vV][eE][rR][iI][fF][yY]', msg.content) or re.search(r'^\d{6}', msg.content):
        await msg.reply(
            f"Woops! Try clicking here: >>> </verify:{ID.COMMAND.VERIFY}> <<<, wait a few seconds, then send the message.\n" + \
            f"On PC, hit the enter key. On mobile, press {ID.EMOJI.SEND}\n" + \
            "## Please do not place your code here\nyou will place it in a popup like below: "
            "https://media.discordapp.net/attachments/1164048175976415262/1200268509280735344/image.png"
        )
        return


async def on_interaction_whipser_guide_create(interaction):
    category = bot.get_channel(ID.CATEGORY.TMG)
    pages, embed, view, selector = await create_guide(interaction, category, 0)
    view.add_item(selector)
    return await interaction.response.send_message(
        embed = embed,
        view = view,
        ephemeral = True
    )

async def on_interaction_whisper_guide_category(interaction):
    category = bot.get_channel(int(interaction.data["values"][0]))
    pages, embed, view, selector = await create_guide(interaction, category, 0)
    view.add_item(selector)
    return await interaction.response.edit_message(embed = embed, view = view)

async def on_interaction_whisper_guide_page(interaction):
    cat_id = interaction.data["custom_id"].split("id=")[1]
    category = bot.get_channel(int(cat_id)) if cat_id != "None" else None
    page = int(interaction.data["custom_id"].split("page=")[1].split(";")[0])
    pages, embed, view, selector = await create_guide(interaction, category, page)
    if interaction.message.flags.ephemeral:
        view.add_item(selector)
    else:
        view.add_item(
            discord.ui.Button(
                style = discord.ButtonStyle.grey,
                custom_id = 'init-msg',
                label = 'Guide',
                emoji = discord.PartialEmoji.from_str(chr(129517)), #Compass emoji
            )
        )
    return await interaction.response.edit_message(embed = embed, view = view)

async def on_interaction_xp_leaderboard_page(interaction):
    start = int(interaction.data["custom_id"].split("xp-start=")[1].split(";")[0])
    user_id = int(interaction.data["custom_id"].split("user=")[1])
    user = bot.get_guild(ID.GUILD).get_member(user_id)
    if not user:
        user = interaction.user
    embed, view, fp = await xp_create_embed(interaction.user, user, start)
    return await interaction.response.edit_message(embed = embed, view = view, attachments = interaction.message.attachments)

async def on_interaction_main_guide_page(interaction):
    page = int(interaction.data["custom_id"].split("page=")[1].split(";")[0])
    pages, embed, view = await create_main_guide(interaction, page)
    return await interaction.response.edit_message(embed = embed, view = view)

@bot.event
async def on_member_join(member):
    if os.path.isfile(ROOT.DATA + f"goofed/{member.id}"):
        await member.add_roles(discord.Object(ID.ROLE.GOOF), reason = "Tried to evade goof")

@bot.event
async def on_interaction(interaction: discord.Interaction):
    if "custom_id" in interaction.data and interaction.data["custom_id"].startswith("poker-"):
        return await on_poker_interaction(interaction)

    if "custom_id" in interaction.data and interaction.data["custom_id"].startswith("chips-"):
        return await on_chips_interaction(interaction)

    if "custom_id" in interaction.data and interaction.data["custom_id"].startswith("purge-"):
        return await on_purge_interaction(interaction)

    if interaction.type != discord.InteractionType.component:
        return

    # Create whisper guide
    if interaction.data["custom_id"] == "init-msg":
        return await on_interaction_whipser_guide_create(interaction)

    # Whisper Guide - Change category
    if interaction.data["custom_id"] == "change-category":
        return await on_interaction_whisper_guide_category(interaction)

    # Whisper guide - Change page
    if interaction.data["custom_id"].startswith("page="):
        return await on_interaction_whisper_guide_page(interaction)

    # XP Leaderboard - Switch page
    if interaction.data["custom_id"].startswith("xp-start="):
        return await on_interaction_xp_leaderboard_page(interaction)

    # Main Guide - Change page
    if interaction.data["custom_id"].startswith("cat-page="):
        return await on_interaction_main_guide_page(interaction)

if __name__ == "__main__":
    bot.run("oops")
