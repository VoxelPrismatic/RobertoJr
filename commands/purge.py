CMD_PURGE_LIST = []

def purge_create_del_view():
    view = discord.ui.View(timeout = None)
    view.add_item(
        discord.ui.Button(
            style = discord.ButtonStyle.red,
            custom_id = f'purge-del',
            label = 'Delete message'
        )
    )
def purge_create_view(start, user):
    view = discord.ui.View(timeout = None)
    view.add_item(
        discord.ui.Button(
            style = discord.ButtonStyle.grey if start < 10 else discord.ButtonStyle.blurple,
            custom_id = f'purge-start={max(start - 10, 0)}',
            label = '<',
            disabled = start < 10
        )
    )
    view.add_item(
        discord.ui.Button(
            style = discord.ButtonStyle.grey,
            custom_id = f'purge-start=0;',
            label = f"{int(start / 10) + 1}/{math.ceil(len(CMD_PURGE_LIST) / 10)}",
            disabled = True
        )
    )
    view.add_item(
        discord.ui.Button(
            style = discord.ButtonStyle.grey if start + 10 >= len(CMD_PURGE_LIST) else discord.ButtonStyle.blurple,
            custom_id = f'purge-start={min(start + 10, len(CMD_PURGE_LIST))};;',
            label = '>',
            disabled = start + 10 >= len(CMD_PURGE_LIST)
        )
    )
    if any(user.get_role(r) for r in ID.ROLE.ALL_ADMINS):
        view.add_item(
            discord.ui.Button(
                style = discord.ButtonStyle.red,
                custom_id = f'purge-begin={start}',
                label = f"Purge Page"
            )
        )
    else:
        view.add_item(
            discord.ui.Button(
                style = discord.ButtonStyle.grey,
                custom_id = f'purge-start={start};;;',
                label = f"Refresh"
            )
        )
    return view

def purge_create_embed(start):
    start = max(0, min(start, len(CMD_PURGE_LIST) - 10))
    listing = ""
    for i, member in enumerate(CMD_PURGE_LIST[start:start+10]):
        listing += f"\u206f{start + i + 1:02}. <@{member.id}> `{member}`\n"
        listing += f"> <t:{int(member.joined_at.timestamp())}:R>; "
        if len(member.roles) > 1:
            listing += " ".join(f'<@&{r.id}>' for r in member.roles if r.id != ID.GUILD) + "\n"
        else:
            listing += "*no roles*\n"

    listing += "\n\n**Note:** Any members that have been here for over 2 weeks and haven't received member roles " + \
               "are included on this list."

    embed = discord.Embed(
        color = 0xff0000,
        title = "Purge members",
        description = listing
    )
    embed.set_footer(text = f"Total members: {len(CMD_PURGE_LIST)}")

    return embed

@tree.command(
    name = "purge",
    description = "Lists users that will be purged",
    guild = ID.GUILD_OBJ
)
@discord.app_commands.default_permissions(
    view_guild_insights = True
)
@discord.app_commands.guild_only()
async def cmd_purge(interaction: discord.Interaction):
    return await cmd_purge_start(interaction)

async def cmd_purge_start(interaction):
    global CMD_PURGE_LIST
    CMD_PURGE_LIST = []
    await interaction.response.send_message("Please wait, fetching members...")
    # msg = await interaction.original_response()
    ttl_passed = 0
    ttl_members = interaction.guild.member_count
    now_ts = datetime.datetime.now().timestamp()

    min_days = 60 * 60 * 24 * 14

    async for member in interaction.guild.fetch_members(limit = None):
        ttl_passed += 1

        if ttl_passed % 500 == 0:
            await interaction.edit_original_response(content = f"""Please wait, fetching members...
{ttl_passed/ttl_members:.2%} [{ttl_passed}/{ttl_members}]
""")

        if now_ts - member.joined_at.timestamp() < min_days:
            continue

        if any(member.get_role(r) for r in ID.ROLE.ALL_MEMBERS):
            continue

        CMD_PURGE_LIST.append(member)

    await interaction.edit_original_response(
        content = "",
        embed = purge_create_embed(0),
        view = purge_create_view(0, interaction.user)
    )

KICK_MSG = """# Hey there!
I'm from the TIMCAST server.

Unfortunately, you have not linked your account in over two weeks, so you've been kicked from the server.
Don't worry, you can still come back and link your account at a later date.
"""

async def cmd_do_purge(interaction):
    data = interaction.data
    btn_id = data["custom_id"]

    if not any(interaction.user.get_role(r) for r in ID.ROLE.ALL_ADMINS):
        return await interaction.response.send_message(
            "Woops! You must be an admin to purge members",
            ephemeral = True
        )

    start = int(btn_id.split("purge-begin=")[1].split(";")[0])
    st = "Kicking members:\n"
    await interaction.response.send_message(st)
    for i, member in enumerate(CMD_PURGE_LIST[start:start+10]):
        CMD_PURGE_LIST.remove(member)
        try:
            await member.send_message(KICK_MSG)
        except Exception as ex:
            print(ex)

        await member.kick(reason = f"No account linked; purged. Requested by {interaction.user}")
        st += f"{i + 1}. <@{member.id}> `{member}`\n"

        await interaction.edit_original_response(content = st)

    embed = purge_create_embed(start)
    view = purge_create_view(start, interaction.user)
    await interaction.followup.edit_message(interaction.message.id, embed = embed, view = view)

async def on_purge_interaction(interaction: discord.Interaction):
    data = interaction.data
    btn_id = data["custom_id"]

    if btn_id == "purge-del":
        return await interaction.message.delete()

    if not len(CMD_PURGE_LIST):
        await cmd_purge_start(interaction)
        return await interaction.followup.delete_message(interaction.message.id)

    if btn_id.startswith("purge-start="):
        start = int(btn_id.split("purge-start=")[1].split(";")[0])
        embed = purge_create_embed(start)
        view = purge_create_view(start, interaction.user)
        return await interaction.response.edit_message(embed = embed, view = view)

    if btn_id.startswith("purge-begin="):
        return await cmd_do_purge(interaction)



    # if str(interaction.user.id) != btn_id.split("=")[1].split(";")[0]:
    #     return await interaction.response.send_message(
    #         "Sorry, you can't interfere with someone else's operation! Be a good criminal and start your own...",
    #         ephemeral = True, delete_after = 5
    #     )
    #
    # if btn_id.startswith("chips-bank="):
    #     return await get_chips_rob_bank(interaction, stage = btn_id.split("stage=")[1].split(";")[0])
    #
    # if btn_id.startswith("chips-ponzi="):
    #     return await chips_ponzi(interaction)
