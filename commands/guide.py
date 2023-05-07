try:
    channel_descs = json.loads(open(ROOT_DATA + "roberto.json", "r").read())
    for key in list(channel_descs):
        if type(key) == str:
            channel_descs[int(key)] = channel_descs[key]
            del channel_descs[key]
except Exception as ex:
    channel_descs = {}

try:
    persistent_ids = [[int(x[0]), int(x[1])] for x in json.loads(open(ROOT_DATA + "persist.json", "r").read())]
except:
    persistent_ids = []



# ==================================================================================================================== #
#                                                                                                                      #
#   /main-guide                                                                                                        #
#       Main guide message for all categories                                                                          #
#                                                                                                                      #
# ==================================================================================================================== #

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



# ==================================================================================================================== #
#                                                                                                                      #
#   /set <description> [id]                                                                                            #
#       Sets the description for the current (or specified) channel                                                    #
#                                                                                                                      #
# ==================================================================================================================== #

@tree.command(
    name = "set",
    description = "Set the description for the current channel",
    guild = discord.Object(GUILD)
)
@discord.app_commands.rename(
    custom_channel = "channel"
)
@discord.app_commands.describe(
    description = "Description for the current channel",
    custom_channel = "Optional: Specify channel. Defaults to current channel/forum"
)
@discord.app_commands.default_permissions(
    administrator = True
)
@discord.app_commands.guild_only()
async def cmd_setdesc(interaction: discord.Interaction, description: str = "", custom_channel: discord.abc.GuildChannel = None):
    channel = custom_channel or interaction.channel
    if channel.type in THREADS:
        channel = channel.parent
    channel_descs[channel.id] = description
    open(ROOT_DATA + "roberto.json", "w+").write(json.dumps(channel_descs, indent = 4))
    desc = description or channel.topic
    embed = discord.Embed(
        title = channel.category.name.upper() if channel.category else "(uncategorized)",
        description = f"<#{channel.id}>\n> {desc or '*<no description set>*'}",
        color = 0x0E7FAA
    )
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
    await interaction.response.send_message(
        "Saved" if description else "Cleared",
        embed = embed,
        ephemeral = True,
        delete_after = 60
    )



# ==================================================================================================================== #
#                                                                                                                      #
#   /get [id]                                                                                                          #
#       Gets the description for the current (or specified) channel                                                    #
#                                                                                                                      #
# ==================================================================================================================== #

@tree.command(
    name = "get",
    description = "Get the description for the current channel",
    guild = discord.Object(GUILD)
)
@discord.app_commands.rename(
    custom_channel = "channel"
)
@discord.app_commands.describe(
    custom_channel = "Optional: Specify channel. Defaults to current channel/forum"
)
@discord.app_commands.guild_only()
async def cmd_getdesc(interaction: discord.Interaction, custom_channel: discord.abc.GuildChannel = None):
    channel = custom_channel or interaction.channel
    if channel.type in THREADS:
        channel = channel.parent
    if channel.id in channel_descs:
        desc = channel_descs[channel.id]
    elif channel.type in TEXT_CHATS:
        channel_descs[channel.id] = desc = channel.topic
    else:
        desc = None

    embed = discord.Embed(
        title = channel.category.name.upper() if channel.category else "(uncategorized)",
        description = f"<#{channel.id}>\n> {desc or '*<no description set>*'}",
        color = 0x0E7FAA
    )
    await interaction.response.send_message(embed = embed, ephemeral = True, delete_after = 60)



# ==================================================================================================================== #
#                                                                                                                      #
#   /guide                                                                                                             #
#       Sends the channel guide for this category                                                                      #
#                                                                                                                      #
# ==================================================================================================================== #

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
    open(ROOT_DATA + "persist.json", "w+").write(json.dumps(persistent_ids, indent = 4))
    await interaction.response.send_message("Done!", ephemeral = True, delete_after = 5)


# ==================================================================================================================== #
# ==================================================================================================================== #
# ==================================================================================================================== #


async def create_guide(interaction: discord.Interaction, category, page: int = 0):
    channels = {}
    categories = {}
    for channel in interaction.guild.channels:
        if channel.type not in ALL_CHATS:
            continue
        if not channel.permissions_for(interaction.user).view_channel:
            continue
        if channel.category == category:
            channels[channel.position] = channel
        if channel.category not in categories:
            categories[channel.category.position if channel.category else -1] = channel.category
    descs = []
    for position in sorted(list(channels)):
        channel = channels[position]
        if channel.id in channel_descs:
            desc = channel_descs[channel.id]
        elif channel.type in TEXT_CHATS:
            channel_descs[channel.id] = desc = channel.topic
        else:
            desc = None
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
            custom_id = f'page={page - 1};id={category.id if category else -1}',
            label = '<',
            disabled = (page - 1) < 0
        )
    )
    view.add_item(
        discord.ui.Button(
            style = discord.ButtonStyle.grey,
            custom_id = f'page={page}; id={category.id if category else -1}',
            label = f"{page + 1}/{len(pages)}",
            disabled = True
        )
    )
    view.add_item(
        discord.ui.Button(
            style = discord.ButtonStyle.grey if (page + 1) >= len(pages) else discord.ButtonStyle.blurple,
            custom_id = f'page={page + 1};id={category.id if category else -1}',
            label = '>',
            disabled = (page + 1) >= len(pages)
        )
    )
    view.add_item(
        discord.ui.Button(
            style = discord.ButtonStyle.green if len(pages) == 1 else discord.ButtonStyle.grey,
            custom_id = f'page={page};id={category.id if category else -1}',
            label = f"Refresh"
        )
    )
    selector = discord.ui.Select(
        custom_id = "change-category",
        placeholder = "Switch Category"
    )
    for position in sorted(list(categories)):
        cat = categories[position]
        selector.add_option(
            label = cat.name.title() if cat else "(uncategorized)",
            value = str(cat.id if cat else -1),
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
