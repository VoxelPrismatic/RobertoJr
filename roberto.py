TOP_COUNT = 10

GUILD = 1078108746410119208
CATEGORY = 1087618927154188318
STARBOARD = 1102112919732363344
EMOJI = "<:20_Sided_Die:1088929649704312914>"

import discord
from discord.ext import commands
import json
import re
import random
import time
bot = discord.Client(intents = discord.Intents.all())
tree = discord.app_commands.CommandTree(bot)

try:
    channel_descs = json.loads(open("roberto.json", "r").read())
    for key in list(channel_descs):
        if type(key) == str:
            channel_descs[int(key)] = channel_descs[key]
            del channel_descs[key]
except Exception as ex:
    channel_descs = {}

try:
    persistent_ids = [[int(x[0]), int(x[1])] for x in json.loads(open("persist.json", "r").read())]
except:
    persistent_ids = []



@tree.command(
    name = "main-guide",
    description = "Main guide for all categories",
    guild = discord.Object(GUILD)
)
@discord.app_commands.default_permissions(
    administrator = True
)
@discord.app_commands.guild_only()
async def cmd_sendmsg(interaction: discord.Interaction):
    view = discord.ui.View(timeout = None)
    view.add_item(
        discord.ui.Button(
            style = discord.ButtonStyle.blurple,
            custom_id = 'init-msg',
            label = 'Guide',
            emoji = discord.PartialEmoji.from_str(chr(129517)) #Compass emoji
        )
    )
    await interaction.channel.send("""\
**Welcome to the Timcast server!**
Click the button below to learn more about the purpose of each channel
""", view = view)
    await interaction.response.send_message("Done!", ephemeral = True, delete_after = 5)

@tree.command(
    name = "set",
    description = "Set the description for the current channel",
    guild = discord.Object(GUILD)
)
@discord.app_commands.describe(
    description = "Description for the current channel"
)
@discord.app_commands.default_permissions(
    administrator = True
)
@discord.app_commands.guild_only()
async def cmd_setdesc(interaction: discord.Interaction, description: str = ""):
    channel = bot.get_channel(interaction.channel_id)
    channel_descs[channel.id] = description
    open("roberto.json", "w+").write(json.dumps(channel_descs, indent = 4))
    desc = description or channel.topic
    for channel_id, message_id in persistent_ids:
        channel = bot.get_channel(channel_id)
        msg = await channel.fetch_message(message_id)
        pages, embed, view, selector = await create_guide(interaction, channel.category, 0)
        view.add_item(
            discord.ui.Button(
                style = discord.ButtonStyle.grey,
                custom_id = 'init-msg',
                label = 'Guide',
                emoji = discord.PartialEmoji.from_str(chr(129517)), #Compass emoji
                )
            )
        await msg.edit(embed = embed, view = view)
    embed = discord.Embed(
        title = channel.category.name.upper() if channel.category else "(uncategorized)",
        description = f"<#{channel.id}>\n> {desc or '*<no description set>*'}",
        color = 0x0E7FAA
    )
    await interaction.response.send_message(
        "Saved" if description else "Cleared",
        embed = embed,
        ephemeral = True,
        delete_after = 60
    )


@tree.command(
    name = "get",
    description = "Get the description for the current channel",
    guild = discord.Object(GUILD)
)
@discord.app_commands.default_permissions(
    administrator = True
)
@discord.app_commands.guild_only()
async def cmd_getdesc(interaction: discord.Interaction):
    channel = interaction.channel
    if channel.id in channel_descs:
        desc = channel_descs[channel.id]
    else:
        channel_descs[channel.id] = desc = channel.topic

    embed = discord.Embed(
        title = channel.category.name.upper() if channel.category else "(uncategorized)",
        description = f"<#{channel.id}>\n> {desc or '*<no description set>*'}",
        color = 0x0E7FAA
    )


    await interaction.response.send_message(embed = embed, ephemeral = True, delete_after = 60)

async def create_guide(interaction: discord.Interaction, category, page: int = 0):
    channels = []
    categories = []
    types = [
        discord.ChannelType.text,
        discord.ChannelType.news,
        discord.ChannelType.forum
    ]

    for channel in interaction.guild.channels:
        if channel.type not in types:
            continue
        if not channel.permissions_for(interaction.user).view_channel:
            continue
        if channel.category == category:
            channels.append(channel)
        if channel.category not in categories:
            categories.append(channel.category)
    descs = []
    for channel in channels:
        if channel.id in channel_descs:
            desc = channel_descs[channel.id]
        else:
            channel_descs[channel.id] = desc = channel.topic
        descs.append(f"<#{channel.id}>\n> {desc or '*<no description set>*'}")
    pages = []
    st = ""
    n = 0
    for desc in descs:
        n += 1
        st += desc + "\n\n"
        if n == 8:
            pages.append(st.strip())
            st = ""
    if st:
        pages.append(st.strip())
    page = max(min(page, len(pages) - 1), 0)

    embed = discord.Embed(
        title = category.name.upper() if category else "(uncategorized)",
        description = pages[page] + "\n\n**Note:** Only channels you have access to will be displayed here",
        color = 0x0E7FAA
    )
    view = discord.ui.View(timeout = None)
    view.add_item(
        discord.ui.Button(
            style = discord.ButtonStyle.grey if (page - 1) < 0 else discord.ButtonStyle.blurple,
            custom_id = f'page={page - 1};id={category.id if category else None}',
            label = '<',
            disabled = (page - 1) < 0
        )
    )
    view.add_item(
        discord.ui.Button(
            style = discord.ButtonStyle.grey,
            custom_id = f'page={page}; id={category.id if category else None}',
            label = f"{page + 1}/{len(pages)}",
            disabled = True
        )
    )
    view.add_item(
        discord.ui.Button(
            style = discord.ButtonStyle.grey if (page + 1) >= len(pages) else discord.ButtonStyle.blurple,
            custom_id = f'page={page + 1};id={category.id if category else None}',
            label = '>',
            disabled = (page + 1) >= len(pages)
        )
    )
    view.add_item(
        discord.ui.Button(
            style = discord.ButtonStyle.green if len(pages) == 1 else discord.ButtonStyle.grey,
            custom_id = f'page={page};id={category.id if category else None}',
            label = f"Refresh"
        )
    )
    selector = discord.ui.Select(
        custom_id = "change-category",
        placeholder = "Switch Category"
    )
    for cat in categories:
        selector.add_option(
            label = cat.name.title() if cat else "(uncategorized)",
            value = str(cat.id if cat else None),
            default = cat == category
        )
    embed.set_footer(
        text = "Navigate with Roberto Jr. with /guide",
        icon_url = "https://cdn.discordapp.com/avatars/1103800725026373702/52197b98a00b8732f9bb2993ab880d1c.webp"
    )
    embed.set_author(
        name = "TIMCAST",
        icon_url = "https://cdn.discordapp.com/icons/1078108746410119208/a_6f9a91c25e9f3589f14f5c5508c1ee6c.webp"
    )

    return pages, embed, view, selector


@tree.command(
    name = "guide",
    description = "Sends the guide for this category",
    guild = discord.Object(GUILD)
)
@discord.app_commands.describe(
    persist = "Whether or not this message should persist (admin only)"
)
@discord.app_commands.guild_only()
async def cmd_guide(interaction: discord.Interaction, persist: bool = False):
    pages, embed, view, selector = await create_guide(interaction, interaction.channel.category, 0)
    if not(persist and interaction.permissions.administrator):
        view.add_item(selector)
        return await interaction.response.send_message(
            embed = embed,
            view = view,
            ephemeral = True
        )
    view.add_item(
        discord.ui.Button(
            style = discord.ButtonStyle.grey,
            custom_id = 'init-msg',
            label = 'Guide',
            emoji = discord.PartialEmoji.from_str(chr(129517)), #Compass emoji
        )
    )
    msg = await interaction.channel.send(embed = embed, view = view)
    persistent_ids.append([msg.channel.id, msg.id])
    open("persist.json", "w+").write(json.dumps(persistent_ids, indent = 4))
    await interaction.response.send_message("Done!", ephemeral = True, delete_after = 5)


@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.type != discord.InteractionType.component:
        return
    if interaction.data["custom_id"] == "init-msg":
        category = bot.get_channel(CATEGORY)
        pages, embed, view, selector = await create_guide(interaction, category, 0)
        view.add_item(selector)
        return await interaction.response.send_message(
            embed = embed,
            view = view,
            ephemeral = True
        )
    if interaction.data["custom_id"] == "change-category":
        category = bot.get_channel(int(interaction.data["values"][0]))
        pages, embed, view, selector = await create_guide(interaction, category, 0)
        view.add_item(selector)
        return await interaction.response.edit_message(embed = embed, view = view)
    if interaction.data["custom_id"].startswith("page="):
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

@bot.event
async def on_raw_reaction_add(payload):
    await handle_reaction(payload)
@bot.event
async def on_raw_reaction_remove(payload):
    await handle_reaction(payload)

presence_time = 0

async def update_presence(force = 0):
    global presence_time
    presences = [
        {"name": "with Cast Brew Coffee", "type": discord.ActivityType.playing},
        {"name": "a brew pour", "type": discord.ActivityType.listening},
        {"name": "steam rise", "type": discord.ActivityType.watching},
        {"name": "beanie stadium", "type": discord.ActivityType.competing}
    ]
    if random.randint(0, 8) != 0 and not force or time.time() - presence_time < 30:
        return
    presence = random.choice(presences)
    print("new presence", presence)
    await bot.change_presence(
        activity = discord.Activity(**presence),
        status = discord.Status.idle
    )
    presence_time = time.time()


starred_timeout = {}
async def handle_reaction(payload):
    await update_presence()
    if str(payload.emoji) != EMOJI:
        return #print("bad emoji", payload.emoji, EMOJI)
    msg = await bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
    for reaction in msg.reactions:
        if str(reaction.emoji) == str(payload.emoji):
            break
    else:
        return #print("no matching emoji found")

    if reaction.count < TOP_COUNT:
        return #print("not enough reactions", TOP_COUNT, ">", reaction.count)
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
                int(open(f"stars/{msg.id}", "r").read().strip())
            )
            if starred_msg.id in starred_timeout:
                return
            await starred_msg.edit(embed = embed, view = view)
        except:
            starred_msg = await bot.get_channel(STARBOARD).send(embed = embed, view = view)
            open(f"stars/{msg.id}", "w+").write(str(starred_msg.id))
    except Exception as ex:
        print(ex)


@bot.event
async def on_ready():
    await tree.sync(guild = discord.Object(GUILD))
    await update_presence(1)




bot.run("nah")
