try:
    xp_pickle = pickle.loads(open(ROOT_DATA + "xp.pickle", "rb").read())
except:
    xp_pickle = {}


xp_cooldown = {}
xp_pickle_save = time.time()

def xp_equation(lvl):
    return 5 * (lvl ** 2) + (50 * lvl) + 100

def give_xp(user, xp = 0):
    if user.bot:
        return
    global xp_pickle_save, xp_pickle
    for item in list(xp_cooldown):
        if time.time() - item > 60:
            del xp_cooldown[item]

    if user.id in xp_cooldown:
        return

    if user.id not in xp_pickle:
        ttl_xp = 0
    else:
        ttl_xp = xp_pickle[user.id]["ttl"]
    ttl_xp += xp or random.randint(3, 6)
    true_xp = ttl_xp

    for true_lvl in range(1000):
        lvl_xp = xp_equation(true_lvl)
        if true_xp - lvl_xp < 0:
            break
        true_xp -= lvl_xp

    xp_pickle[user.id] = {
        "xp": true_xp,
        "lvl": true_lvl,
        "ttl": ttl_xp
    }

    if xp == 0:
        xp_cooldown[user.id] = time.time()

    if time.time() - xp_pickle_save > 30:
        xp_pickle_save = time.time()
        open(ROOT_DATA + "xp.pickle", "wb+").write(pickle.dumps(xp_pickle))

def get_bar(percent):
    columns = 20
    done = percent * columns
    prog = "/" * max(min(int(done), columns), 0)
    done = int(done * 10) % 10
    if done >= 8:
        prog += "|"
    elif done >= 5:
        prog += ":"
    elif done >= 2:
        prog += "."
    return prog.ljust(columns)

async def xp_create_embed(author, user, start = 0):
    if user.id in xp_pickle and not user.bot:
        data = xp_pickle[user.id]
    else:
        data = {"xp": 0, "lvl": 0, "ttl": 0}
    if author.id in xp_pickle and not user.bot:
        data_self = xp_pickle[author.id]
    else:
        data_self = {"xp": 0, "lvl": 0, "ttl": 0}

    xp_needed = xp_equation(data["lvl"] + 1)
    leaders = {}
    for user_id in xp_pickle:
        if xp_pickle[user_id]["ttl"] in leaders:
            leaders[xp_pickle[user_id]["ttl"]].append(user_id)
        else:
            leaders[xp_pickle[user_id]["ttl"]] = [user_id]
    ranks = sorted(set(leaders))
    try:
        rank = len(ranks) - ranks.index(data["ttl"])
    except ValueError:
        rank = len(ranks)
    try:
        rank_self = len(ranks) - ranks.index(data_self["ttl"])
    except ValueError:
        rank_self = len(ranks)

    for role in user.roles:
        if role.id == ELITE_ROLE:
            elite_emoji = ELITE_EMOJI + " "
            break
    else:
        elite_emoji = ""

    embed = discord.Embed(
        description = f"""\
{elite_emoji}Level **{data['lvl']}** | Rank **#{rank}**
{elite_emoji}Progress: **{data['xp']}**/{xp_needed} XP
{elite_emoji}`[{get_bar(data['xp']/xp_needed)}]`
""",
        color = 0xECB300 if elite_emoji else 0xA46B31
    )
    embed.set_footer(text = f"Total XP: {data['ttl']}")
    embed.set_author(name = str(user))
    leaderboard = ""
    passed = []
    c = 0
    n = -1
    first_rank = 0
    last_rank = 0

    for amount in ranks[::-1]:
        for q in leaders[amount]:
            n += 1
            if n < start:
                continue
            if c == 10:
                break
            try:
                m = len(ranks) - ranks.index(xp_pickle[q]["ttl"])
            except ValueError:
                m = len(ranks)
            first_rank = first_rank or m
            last_rank = m
            match m:
                case 1:
                    leaderboard += "\U0001f947"
                case 2:
                    leaderboard += "\U0001f948"
                case 3:
                    leaderboard += "\U0001f949"
                case _:
                    leaderboard += f"**{m:02}.**" if q == user.id or q == author.id else f"{m:02}."
            passed.append(q)
            leaderboard += f" <@{q}>; Lv{xp_pickle[q]['lvl']}\n"
            c += 1

    leaderboard = leaderboard.strip()
    entry_user = f"**{rank:02}.** <@{user.id}>; Lv{data['lvl']}"
    entry_self = f"**{rank_self:02}.** <@{author.id}>; Lv{data_self['lvl']}"
    leaderboard_head = ""
    leaderboard_foot = ""

    # User and Author in page
    if user.id in passed and author.id in passed:
        pass

    # User in page; Author ... First
    elif user.id in passed and rank_self < first_rank:
        leaderboard_head += entry_self + "\n"
        if abs(rank_self - first_rank) > 1:
            leaderboard_head += "...\n"

    # User in page; Last ... Author
    elif user.id in passed and rank_self > last_rank:
        if abs(rank_self - last_rank) > 1:
            leaderboard_foot += "\n..."
        leaderboard_foot += "\n" + entry_self

    # Author in page; First ... User
    elif author.id in passed and rank < first_rank:
        leaderboard_head += entry_user + "\n"
        if abs(rank - first_rank) > 1:
            leaderboard_head += "...\n"

    # Author in page; Last ... User
    elif author.id in passed and rank > last_rank:
        if abs(rank - last_rank) > 1:
            leaderboard_foot += "\n..."
        leaderboard_foot += "\n" + entry_user

    # Author ... User ... First
    elif rank_self < rank and rank < first_rank:
        leaderboard_head += entry_self + "\n"
        if abs(rank - rank_self) > 1:
            leaderboard_head += "...\n"
        leaderboard_head += entry_user + "\n"
        if abs(rank - first_rank) > 1:
            leaderboard_head += "...\n"

    # User ... Author ... First
    elif rank < rank_self and rank_self < first_rank:
        leaderboard_head += entry_user + "\n"
        if abs(rank - rank_self) > 1:
            leaderboard_head += "...\n"
        leaderboard_head += entry_self + "\n"
        if abs(rank_self - first_rank) > 1:
            leaderboard_head += "...\n"

    # Last ... Author ... User
    elif rank > rank_self and rank_self > last_rank:
        if abs(rank_self - last_rank) > 1:
            leaderboard_foot += "\n..."
        leaderboard_foot += "\n" + entry_self
        if abs(rank_self - rank) > 1:
            leaderboard_foot += "\n..."
        leaderboard_foot += "\n" + entry_user

    # Last ... User ... Author
    elif rank_self > rank and rank > last_rank:
        if abs(rank - last_rank) > 1:
            leaderboard_foot += "\n..."
        leaderboard_foot += "\n" + entry_user
        if abs(rank_self - rank) > 1:
            leaderboard_foot += "\n..."
        leaderboard_foot += "\n" + entry_self

    # User ... Page ... Author
    elif rank < first_rank and rank_self > last_rank:
        leaderboard_head += entry_user + "\n"
        if abs(rank - first_rank) > 1:
            leaderboard_head += "...\n"
        if abs(rank_self - last_rank) > 1:
            leaderboard_foot += "\n..."
        leaderboard_foot += "\n" + entry_self

    # Author ... Page ... User
    elif rank_self < first_rank and rank > last_rank:
        leaderboard_head += entry_self + "\n"
        if abs(rank_self - first_rank) > 1:
            leaderboard_head += "...\n"
        if abs(rank - last_rank) > 1:
            leaderboard_foot += "\n..."
        leaderboard_foot += "\n" + entry_user

    else:
        print("Rank:", rank, "| RankSelf:", rank_self, "| First:", first_rank, "| Last:", last_rank)

    leaderboard = leaderboard_head + leaderboard + leaderboard_foot

    embed.add_field(
        name = "Leaderboard",
        inline = False,
        value = leaderboard
    )
    pfp = user.default_avatar.url
    if user.guild_avatar:
        pfp = user.guild_avatar.url
    elif user.avatar:
        pfp = user.avatar.url
    embed.set_thumbnail(url = pfp)
    view = discord.ui.View(timeout = None)
    view.add_item(
        discord.ui.Button(
            style = discord.ButtonStyle.grey if start < 10 else discord.ButtonStyle.blurple,
            custom_id = f'xp-start={max(start - 10, 0)};user={user.id}',
            label = '<',
            disabled = start < 10
        )
    )
    view.add_item(
        discord.ui.Button(
            style = discord.ButtonStyle.grey,
            custom_id = f'xp-start=0; user={user.id}',
            label = f"{int(start / 10) + 1}/{math.ceil(len(xp_pickle) / 10)}",
            disabled = True
        )
    )
    view.add_item(
        discord.ui.Button(
            style = discord.ButtonStyle.grey if start + 10 >= len(xp_pickle) else discord.ButtonStyle.blurple,
            custom_id = f'xp-start={min(start + 10, len(xp_pickle))};user={user.id}',
            label = '>',
            disabled = start + 10 >= len(xp_pickle)
        )
    )
    view.add_item(
        discord.ui.Button(
            style = discord.ButtonStyle.grey,
            custom_id = f'xp-start={start};  user={user.id}',
            label = f"Refresh"
        )
    )
    for user_id in passed:
        if not bot.get_guild(GUILD).get_member(user_id):
            try:
                await bot.get_guild(GUILD).fetch_member(user_id)
            except:
                del xp_pickle[user_id]

    return embed, view

@tree.command(
    name = "xp",
    description = "View your level and your rank on the leaderboard",
    guild = discord.Object(GUILD)
)
@discord.app_commands.describe(
    member = "View someone else's rank"
)
@discord.app_commands.guild_only()
async def cmd_xp(interaction: discord.Interaction, member: discord.Member = None):
    user = member or interaction.user
    embed, view = await xp_create_embed(interaction.user, user, 0)
    await interaction.response.send_message(
        embed = embed,
        ephemeral = interaction.channel.id not in BOT_CHANNELS,
        view = view
    )

@tree.command(
    name = "give-xp",
    description = "Give XP to a user",
    guild = discord.Object(GUILD)
)
@discord.app_commands.describe(
    member = "Who to give XP to",
    amount = "How much XP to give. Use a negative number to take away XP"
)
@discord.app_commands.default_permissions(
    administrator = True
)
@discord.app_commands.guild_only()
async def cmd_give_xp(interaction: discord.Interaction, member: discord.Member, amount: int):
    give_xp(member, amount)
    if amount < 0:
        msg = f"Took {-amount} XP away!"
    else:
        msg = f"Gave {amount} XP"
    embed, view = await xp_create_embed(member, member, 0)
    await interaction.response.send_message(
        msg,
        embed = embed,
    )

@tree.command(
    name = "take-xp",
    description = "Take XP from a user",
    guild = discord.Object(GUILD)
)
@discord.app_commands.describe(
    member = "Who to take XP from",
    amount = "How much XP to take. Use a negative number to give XP"
)
@discord.app_commands.default_permissions(
    administrator = True
)
@discord.app_commands.guild_only()
async def cmd_take_xp(interaction: discord.Interaction, member: discord.Member, amount: int):
    give_xp(member, -amount)
    if amount > 0:
        msg = f"Took {amount} XP away!"
    else:
        msg = f"Gave {-amount} XP"
    embed, view = await xp_create_embed(member, member, 0)
    await interaction.response.send_message(
        msg,
        embed = embed,
    )
