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
        if time.time() - xp_cooldown[item] > 60:
            del xp_cooldown[item]

    if user.id in xp_cooldown and xp == 0:
        # print(xp_cooldown)
        # print(user.id in xp_cooldown)
        return

    if user.id not in xp_pickle:
        ttl_xp = 0
        # color = ""
    else:
        ttl_xp = xp_pickle[user.id]["ttl"]
        # color = xp_pickle[user.id]["color"] if "color" in xp_pickle[user.id] else ""
    ttl_xp += xp or random.randint(3, 6)
    ttl_xp = max(ttl_xp, 0)
    true_xp = ttl_xp

    for true_lvl in range(1000):
        lvl_xp = xp_equation(true_lvl)
        if true_xp - lvl_xp < 0:
            break
        true_xp -= lvl_xp

    xp_pickle[user.id] = {
        "xp": true_xp,
        "lvl": true_lvl,
        "ttl": ttl_xp,
        # "color": color
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
        if data['xp'] < 0:
            xp_pickle[user.id] = data = {"xp": 0, "lvl": 0, "ttl": 0}
    else:
        data = {"xp": 0, "lvl": 0, "ttl": 0}
    if author.id in xp_pickle and not user.bot:
        data_self = xp_pickle[author.id]
        if data_self['xp'] < 0:
            xp_pickle[author.id] = data_self = {"xp": 0, "lvl": 0, "ttl": 0}
    else:
        data_self = {"xp": 0, "lvl": 0, "ttl": 0}

    xp_needed = xp_equation(data["lvl"] + 1)
    leaders = {}
    for user_id in xp_pickle:
        if xp_pickle[user_id]["ttl"] in leaders:
            leaders[xp_pickle[user_id]["ttl"]].append(user_id)
        else:
            leaders[xp_pickle[user_id]["ttl"]] = [user_id]
    ranks = sorted(set(leaders), reverse = True)
    lb = []
    for r in ranks:
        lb.extend(leaders[r])
    try:
        rank = lb.index(user.id) + 1
    except ValueError:
        rank = len(lb)
    try:
        rank_self = lb.index(author.id) + 1
    except ValueError:
        rank_self = len(lb)

    for role in user.roles:
        if role.id == ELITE_ROLE:
            elite_emoji = ELITE_EMOJI + " "
            break
    else:
        elite_emoji = ""

    # print(data['lvl'], '|;', data['xp'], '|;', rank, '|;', 1 if elite_emoji else 0)
    profile_picture = (user.guild_avatar or user.avatar or user.default_avatar)
    saved_name = ROOT_DATA + f"levels/saved/{user.id}/{data['lvl']}-{data['xp']}-{rank}-{1 if elite_emoji else 0}.webp"
    if not os.path.isfile(saved_name):
        if not os.path.isfile(ROOT_DATA + f"levels/pfp/{user.id}/{profile_picture.key}.webp"):
            pfp_dir = ROOT_DATA + f"levels/pfp/{user.id}/"
            if not os.path.isdir(pfp_dir):
                os.mkdir(pfp_dir)
            for f in os.listdir(pfp_dir):
                os.remove(pfp_dir + f)
            await profile_picture.with_size(128).with_format("webp").save(open(pfp_dir + profile_picture.key + ".webp", "wb+"))
        proc = subprocess.Popen(["python3", ROOT_DATA + "levels/generate-card.py", str(user.id), str(data['lvl']), str(data['xp']), str(rank), str(user), '1' if elite_emoji else '0'])
        while proc.poll() is None:
            await asyncio.sleep(0.1)

    fp = discord.File(open(saved_name, "rb"), filename = f"{user.id}.webp")
    leaderboard = ""
    passed = []
    c = 0
    n = -1
    first_rank = 0
    last_rank = 0

    for amount in ranks:
        for q in leaders[amount]:
            n += 1
            if n < start:
                continue
            if c == 10:
                break
            try:
                m = lb.index(q) + 1
            except ValueError:
                m = len(lb)
            first_rank = first_rank or m
            last_rank = m
            if m == rank or m == rank_self:
                leaderboard += "> "
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
    elif (user.id in passed or user.id == author.id) and rank_self < first_rank:
        leaderboard_head += entry_self + "\n"
        if abs(rank_self - first_rank) > 1:
            leaderboard_head += "...\n"

    # User in page; Last ... Author
    elif (user.id in passed or user.id == author.id) and rank_self > last_rank:
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

    embed = discord.Embed(
        description = leaderboard + "\n\n**Note:** Your rank card will not update until you re-run the `/xp` command",
        color = 0xECB300 if elite_emoji else 0xA46B31
    )

    embed.set_footer(text = f"Total XP: {data['ttl']}")
    embed.set_author(name = str(user))


    embed.set_thumbnail(url = profile_picture.url)
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

    return embed, view, fp

async def cmd_handle_give_xp(interaction, member, amount):
    give_xp(member, amount)
    if amount < 0:
        msg = f"Took {-amount} XP away!"
    else:
        msg = f"Gave {amount} XP"
    embed, view, fp = await xp_create_embed(member, member, 0)
    await interaction.response.send_message(msg, file = fp)

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
    embed, view, fp = await xp_create_embed(interaction.user, user, 0)
    await interaction.response.send_message(
        embed = embed,
        ephemeral = interaction.channel.id not in BOT_CHANNELS,
        view = view,
        file = fp
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
    return await cmd_handle_give_xp(interaction, member, -amount)

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
    return await cmd_handle_give_xp(interaction, member, -amount)
