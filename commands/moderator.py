async def verify_perms(interaction, perms = ID.ROLE.ALL_MODERATORS):
    mbr = interaction.guild.get_member(interaction.user.id)
    if mbr is None:
        mbr = await interaction.guild.fetch_member(interaction.user.id)
    if not interaction.permissions.administrator:
        for role in mbr.roles:
            if role.id in perms:
                break
        else:
            return True
    return False

@tree.command(
    name = "goof",
    description = "Someone done goofed",
    guild = ID.GUILD_OBJ
)
@discord.app_commands.describe(
    member = "Who done goofed",
#    goofy = "Whether or not they are still goofy"
)
#@discord.app_commands.choices(
#    goofy = [
#        discord.app_commands.Choice(name = "Very goofy", value = 1),
#        discord.app_commands.Choice(name = "Ungoofed", value = 0)
#    ]
#)
@discord.app_commands.default_permissions(
    view_guild_insights = True
)
@discord.app_commands.guild_only()
async def com_done_goofed(interaction: discord.Interaction, member: discord.Member):
    await interaction.response.defer(thinking = True)
    if await verify_perms(interaction):
        return await interaction.response.send_message(
            "Sorry, you have to be a moderator to say someone goofed",
            ephemeral = True
        )
    goofed_role = discord.Object(ID.ROLE.GOOF)
    reason = f"Requested by {interaction.user}"
    if not member.get_role(ID.ROLE.GOOF):
        roles = [r for r in member.roles if r.id in ID.ROLE.ALL_MEMBERS]
        open(ROOT.DATA + f"goofed/{member.id}", "w+").write(json.dumps([r.id for r in roles], indent = 4))
        for r in roles:
            try:
                await member.remove_roles(r, reason = reason)
            except:
                pass
        await member.add_roles(goofed_role, reason = reason)
        return await interaction.edit_original_response(content = f"{str(member)} goofed hard")
    return await interaction.edit_original_response(content = f"{str(member)} is already goofed")

@tree.command(
    name = "ungoof",
    description = "Someone recovered from the goof",
    guild = ID.GUILD_OBJ
)
@discord.app_commands.describe(
    member = "Who done goofed",
#    goofy = "Whether or not they are still goofy"
)
#@discord.app_commands.choices(
#    goofy = [
#        discord.app_commands.Choice(name = "Very goofy", value = 1),
#        discord.app_commands.Choice(name = "Ungoofed", value = 0)
#    ]
#)
@discord.app_commands.default_permissions(
    view_guild_insights = True
)
@discord.app_commands.guild_only()
async def com_done_ungoofed(interaction: discord.Interaction, member: discord.Member):
    await interaction.response.defer(thinking = True)
    if await verify_perms(interaction):
        return await interaction.response.send_message(
            "Sorry, you have to be a moderator to say someone goofed",
            ephemeral = True
        )
    goofed_role = discord.Object(ID.ROLE.GOOF)
    reason = f"Requested by {interaction.user}"
    if member.get_role(ID.ROLE.GOOF):
        roles = json.loads(open(ROOT.DATA + f"goofed/{member.id}").read())
        os.remove(ROOT.DATA + f"goofed/{member.id}")
        await member.add_roles(*[discord.Object(r) for r in roles])
        await member.remove_roles(goofed_role)

        return await interaction.edit_original_response(content = f"{str(member)} recovered from an epic goof")
    return await interaction.edit_original_response(content = f"{str(member)} has not goofed yet")



@tree.command(
    name = "mod-room",
    description = "Bring a few people in a mod room",
    guild = ID.GUILD_OBJ
)
@discord.app_commands.describe(
    member1 = "Bring in member 1",
    member2 = "Bring in member 2",
    member3 = "Bring in member 3",
    member4 = "Bring in member 4",
    member5 = "Bring in member 5",
    member6 = "Bring in member 6",
    member7 = "Bring in member 7",
    member8 = "Bring in member 8",
)
@discord.app_commands.default_permissions(
    view_guild_insights = True
)
@discord.app_commands.guild_only()
async def com_mod_room(interaction: discord.Interaction, member1: discord.Member = None, member2: discord.Member = None,
                       member3: discord.Member = None, member4: discord.Member = None, member5: discord.Member = None,
                       member6: discord.Member = None, member7: discord.Member = None, member8: discord.Member = None):
    if await verify_perms(interaction, ID.ROLE.ALL_PROMOTERS):
        return await interaction.response.send_message(
            "Sorry, you have to be a coordinator to create rooms",
            ephemeral = True
        )
    view_perm = discord.PermissionOverwrite(
        view_channel = True,
        read_messages = True,
        send_messages = True,
        add_reactions = True,
        attach_files = True,
        embed_links = True,
        read_message_history = True
    )
    overwrites = {
        interaction.guild.default_role: discord.PermissionOverwrite(view_channel = False, read_messages = False),
    }
    for r in ID.ROLE.ALL_MODERATORS:
        overwrites[interaction.guild.get_role(r)] = view_perm
    members = [
        interaction.user,
        member1, member2, member3, member4,
        member5, member6, member7, member8,
        interaction.guild.me
    ]
    for member in members:
        if member is None or member in overwrites:
            continue
        overwrites[member] = view_perm

    channel = await interaction.guild.get_channel(ID.CATEGORY.MOD_ROOM).create_text_channel(
        f"room-{random.randint(0, 65535):04x}",
        reason = f"Requested by {str(interaction.user)}",
        overwrites = overwrites
    )
    await channel.send("<@" + "> <@".join(str(mbr.id) for mbr in members[:-1] if mbr is not None) + ">")
    await interaction.response.send_message(f"Alright, visit <#{channel.id}>")

@tree.command(
    name = "close-room",
    description = "Close a mod room",
    guild = ID.GUILD_OBJ
)
@discord.app_commands.default_permissions(
    view_guild_insights = True
)
@discord.app_commands.guild_only()
async def com_close_room(interaction: discord.Interaction):
    if await verify_perms(interaction, ID.ROLE.ALL_ADMINS):
        return await interaction.response.send_message(
            "Sorry, you have to be an admin to close mod rooms",
            ephemeral = True
        )
    if interaction.channel.category.id != ID.CATEGORY.MOD_ROOM:
        return await interaction.response.send_message(
            "This isn't a mod room!",
            ephemeral = True
        )
    await interaction.response.send_message(
        "Closing...",
        ephemeral = True
    )
    await interaction.channel.delete()

available_notes = {}

def rng_u_id(root):
    game_id = f"{random.randint(0, 65535):04x}"
    game_ids = os.listdir(root)
    if len(game_ids) > 65535:
        raise ValueError("Too many IDs")
    while game_id in game_ids:
        game_id = f"{random.randint(0, 65535):04x}"
    return game_id

async def reveal_notes(interaction, member, root):
    ls = os.listdir(root)
    embed = discord.Embed(
        title = "All Notes",
        description = f"Total Notes: {len(ls)}",
        color = 0x8800ff
    )
    for note in ls[:25]:
        note_data = json.loads(open(root + note).read())
        ct = "> " + note_data['content'].replace("\n", "\n> ")
        if len(ct) > 512:
            ct = ct[:512] + " [...]"
        if "file" in note_data:
            ct += "\n> *<attachment>*"
        ct += f"\nBy <@{note_data['author']}> on <t:{int(note_data['timestamp'])}:F>"
        embed.add_field(
            name = note,
            value = ct,
            inline = False
        )
    embed.set_author(name = str(member), icon_url = (member.guild_avatar or  member.avatar or member.default_avatar).url)
    return await interaction.response.send_message(
        embed = embed
    )

@tree.command(
    name = "note",
    description = "Add or view notes on a particular user",
    guild = ID.GUILD_OBJ
)
@discord.app_commands.describe(
    member = "Who to note",
    action = "View, add or delete notes",
    note = "The note to add, or the note ID to view",
    short_name = "A short name so it's easier to find at a later date. Ignored if viewing or removing notes",
    image = "An attachment to add to the note, could also be an audio segment"
)
@discord.app_commands.rename(
    image = "attachment"
)
@discord.app_commands.choices(
    action = [
        discord.app_commands.Choice(name = "Create new note", value = 0),
        discord.app_commands.Choice(name = "View existing note", value = 1),
        discord.app_commands.Choice(name = "Delete note", value = 2)
    ]
)
@discord.app_commands.default_permissions(
    view_guild_insights = True
)
@discord.app_commands.guild_only()
async def cmd_notes(interaction: discord.Interaction, member: discord.Member, action: int, note: str, short_name: str = "",
                    image: discord.Attachment = None):
    global available_notes
    available_notes = {}
    root = ROOT.DATA + "notes/" + str(member.id) + "/"
    os.makedirs(root, exist_ok = True)
    if action == 0:
        if note.strip() == "":
            return await interaction.response.send_message(
                f"Your note cannot be blank"
            )
        note_id = rng_u_id(root)
        if not short_name:
            short_name = note[:90] + ("..." if len(note) > 90 else "")
        short_name = short_name[:90]
        note_data = {
            "content": note,
            "author": interaction.user.id,
            "timestamp": datetime.datetime.now().timestamp(),
            "short_name": short_name,
        }
        msg = "Note created!"
        if image:
            await image.save(open(ROOT.DATA + f"notes/files/{image.id}-{image.filename}", "wb+"))
            note_data["file"] = f"{image.id}-{image.filename}"
        open(root + note_id, "w+").write(json.dumps(note_data, indent = 4))
    elif action == 1:
        if note == "----":
            return await reveal_notes(interaction, member, root)
        if note not in os.listdir(root):
            return await interaction.response.send_message(
                f"No such note exists for {member}"
            )
        note_data = json.loads(open(root + note).read())
        note_id = note
        msg = "Viewing note"
    elif action == 2:
        if note not in os.listdir(root):
            return await interaction.response.send_message(
                f"No such note exists for {member}"
            )
        note_data = json.loads(open(root + note).read())
        note_id = note
        os.remove(root + note)
        msg = "The following note has been deleted"

    embed = discord.Embed(
        title = f"[{note_id}] {note_data['short_name']}",
        description = note_data["content"],
        color = 0x8800ff
    )
    name = str(member)
    if name.endswith("#0"):
        name = "@" + name[:-2]
    embed.set_author(name = name, icon_url = (member.guild_avatar or  member.avatar or member.default_avatar).url)
    embed.add_field(name = "Metadata", value = f"Written by <@{note_data['author']}> on <t:{int(note_data['timestamp'])}:F>")
    if "file" in note_data:
        await interaction.response.send_message(
            msg,
            embed = embed,
            # ephemeral = True,
            file = discord.File(open(f"{ROOT.DATA}/notes/files/{note_data['file']}", "rb"))
        )
    else:
        await interaction.response.send_message(
            msg,
            embed = embed,
            # ephemeral = True
        )
    if action == 2 and "file" in note_data:
        os.remove(f"{ROOT.DATA}/notes/files/{note_data['file']}")

@cmd_notes.autocomplete("note")
async def cmd_notes_autocomplete(interaction: discord.Interaction, current: str):
    global available_notes
    if interaction.namespace.action == 0 or interaction.namespace.action is None:
        return []#[discord.app_commands.Choice(name = "Creating new note...", value = "0000")]
    try:
        member = interaction.namespace.member
        if member.id not in available_notes:
            available_notes[member.id] = {}
            root = ROOT.DATA + "notes/" + str(member.id) + "/"
            for note in os.listdir(root):
                available_notes[member.id][note] = json.loads(open(root + note).read())
        if interaction.namespace.action == 1:
            options = [discord.app_commands.Choice(name = "View all notes", value = "----")]
        else:
            options = []
        for note in available_notes[member.id]:
            if current in note or current in available_notes[member.id][note]["short_name"]:
                options.append(discord.app_commands.Choice(
                    name = f"[{note}] {available_notes[member.id][note]['short_name']}",
                    value = note
                ))
                if len(options) >= 25:
                    break
        if len(options) <= (interaction.namespace.action % 2):
            return [discord.app_commands.Choice(name = "No notes found", value = "0000")]
        return options[:25]
    except FileNotFoundError:
        return [discord.app_commands.Choice(name = "No notes available", value = "0000")]
    except Exception as ex:
        print(ex)
        return [discord.app_commands.Choice(name = "An error occurred", value = "0000")]
    return [discord.app_commands.choice(name = "[End of function]", value = "0000")]
