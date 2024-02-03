try:
    xp_pickle = pickle.loads(open(ROOT.DATA + "xp.pickle", "rb").read())
except:
    xp_pickle = {}


xp_cooldown = {}
xp_pickle_save = time.time()

def xp_equation(lvl):
    return 5 * (lvl ** 2) + (50 * lvl) + 100

def readable_num(n):
    suffix = ["", "k", "M", "B"]
    while n >= 1000:
        n /= 1000
        suffix.pop(0)
    if n >= 100:
        return f"{int(n)}{suffix[0]}"
    elif n >= 10:
        return f"{round(n, 1)}{suffix[0]}"
    return f"{round(n, 2)}{suffix[0]}"

def give_xp(user, xp = None, ret = False):
    if type(user) == discord.Member or type(user) == discord.User:
        if user.bot or user.get_role(ID.ROLE.TIER.LOUNGE) is None:
            return {"xp": 0, "lvl": 0, "ttl": 0} if ret else -1
        user_id = user.id
    else:
        user_id = int(user)

    global xp_pickle_save, xp_pickle

    for item in list(xp_cooldown):
        if time.time() - xp_cooldown[item] > 60:
            del xp_cooldown[item]

    if user_id not in xp_pickle:
        xp_pickle[user_id] = {"xp": 0, "lvl": 0, "ttl": 0}

    if ret:
        return xp_pickle[user_id]

    ttl_xp = xp_pickle[user_id]["ttl"]

    if user_id in xp_cooldown and xp is None:
        return ttl_xp

    ttl_xp += random.randint(1, 4) if xp is None else xp
    true_xp = ttl_xp = int(max(ttl_xp, 0))

    for true_lvl in range(1000):
        lvl_xp = xp_equation(true_lvl)
        if true_xp - lvl_xp < 0:
            break
        true_xp -= lvl_xp

    xp_pickle[user_id] = {
        "xp": true_xp,
        "lvl": true_lvl,
        "ttl": ttl_xp,
    }

    if xp is None:
        xp_cooldown[user_id] = time.time()

    if time.time() - xp_pickle_save > 15:
        xp_pickle_save = time.time()
        open(ROOT.DATA + "xp.pickle", "wb+").write(pickle.dumps(xp_pickle))

    return ttl_xp


async def create_chips_card(profile_picture, user, data, rank, elite_emoji):
    saved_name = ROOT.DATA + f"levels/saved/{user.id}/{data['lvl']}-{data['xp']}-{rank}-{1 if elite_emoji else 0}.webp"
    if not os.path.isfile(saved_name):
        if not os.path.isfile(ROOT.DATA + f"levels/pfp/{user.id}/{profile_picture.key}.webp"):
            pfp_dir = ROOT.DATA + f"levels/pfp/{user.id}/"

            if not os.path.isdir(pfp_dir):
                os.mkdir(pfp_dir)
            for f in os.listdir(pfp_dir):
                os.remove(pfp_dir + f)

            await profile_picture.with_size(128).with_format("webp").save(
                open(pfp_dir + profile_picture.key + ".webp", "wb+")
            )

        proc = subprocess.Popen([
            "python3",
            ROOT.DATA + "levels/generate-card.py",
            str(user.id),
            str(data['lvl']),
            str(data['xp']),
            str(rank),
            str(user),
            '1' if elite_emoji else '0'
        ])
        while proc.poll() is None:
            await asyncio.sleep(0.1)
    return discord.File(open(saved_name, "rb"), filename = f"{user.id}.webp")

def xp_create_header_footer(user, author, rank, rank_self, data, data_self, first_rank, last_rank, passed):
    entry_user = f"**{rank:02}.** <@{user.id}>; {readable_num(data['ttl'])} {ID.EMOJI.DEAD}"
    entry_self = f"**{rank_self:02}.** <@{author.id}>; {readable_num(data_self['ttl'])} {ID.EMOJI.DEAD}"

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

    return leaderboard_head, leaderboard_foot

def xp_create_view(start, user):
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
    return view

async def xp_create_embed(author, user, start = 0):
    data = give_xp(user, 0, 1)
    data_self = give_xp(author, 0, 1)

    xp_needed = xp_equation(data["lvl"] + 1)
    leaders = {}
    ttl_passed = start * 10 + 15
    author_passed = False
    user_passed = False

    for user_id in xp_pickle:
        ttl_ = xp_pickle[user_id]["ttl"]
        if ttl_ in leaders:
            leaders[ttl_].add(user_id)
        else:
            leaders[ttl_] = {user_id}

        if int(user_id) == author.id:
            author_passed = True
        if int(user_id) == user.id:
            user_padded = True

        ttl_passed -= 1
        if ttl_passed < 0 and author_passed and user_passed:
            break

    ranks = sorted(set(leaders), reverse = True)
    lb = []
    for r in ranks:
        lb.extend(leaders[r])

    rank = lb.index(user.id) + 1 if user.id in lb else len(lb)
    rank_self = lb.index(author.id) + 1 if author.id in lb else len(lb)

    elite_emoji = ID.EMOJI.ELITE + " " if user.get_role(ID.ROLE.TIER.ELITE) else ""

    profile_picture = (user.guild_avatar or user.avatar or user.default_avatar)

    fp = await create_chips_card(profile_picture, user, data, rank, elite_emoji) if start == 0 else None

    leaderboard = ""
    passed = []

    c = 0
    n = -1
    first_rank = 0
    last_rank = 0
    seized = '\u274c'

    for amount in ranks:
        for q in leaders[amount]:
            if (n := n + 1) < start:
                continue

            if c == 10:
                break

            m = lb.index(int(q)) + 1 if int(q) in lb else len(lb)

            first_rank = first_rank or m
            last_rank = m

            match m:
                case 1 | 2 | 3:
                    leaderboard += " \U0001f947\U0001f948\U0001f949"[m]
                case _:
                    leaderboard += f"**{m:02}.**" if q == user.id or q == author.id else f"\u206f{m:02}."

            passed.append(int(q))

            if get_chips(q) == -1:
                leaderboard += f" <@{q}>; {readable_num(xp_pickle[q]['ttl'])} {seized}\n"
            elif m == rank or m == rank_self:
                leaderboard += f" <@{q}>; {readable_num(xp_pickle[q]['ttl'])} {ID.EMOJI.DEAD}\n"
            else:
                leaderboard += f" <@{q}>; {readable_num(xp_pickle[q]['ttl'])}\n"
            c += 1

    leaderboard = leaderboard.strip()

    leaderboard_head, leaderboard_foot = xp_create_header_footer(
        user, author, rank, rank_self, data, data_self, first_rank, last_rank, passed
    )


    leaderboard = leaderboard_head + leaderboard + leaderboard_foot
    leaderboard += f"\n\n**Note:** Your rank card will not update until you run {COMMAND_STR('chips')} again"

    if random.choice(PROMO_CHANCE) == 0:
        leaderboard += SHAMELESS_PROMO


    embed = discord.Embed(
        description = leaderboard,
        color = 0xECB300 if elite_emoji else 0xA46B31,
        title = "Chips Leaderboard"
    )

    embed.set_author(name = str(user))

    embed.set_thumbnail(url = profile_picture.url)

    view = xp_create_view(start, user)

    for user_id in passed:
        if not (m := bot.get_guild(ID.GUILD).get_member(user_id)):
            try:
                m = await bot.get_guild(ID.GUILD).fetch_member(user_id)
            except:
                del xp_pickle[user_id]
                continue

        if not any(m.get_role(r) for r in ID.ROLE.ALL_MEMBERS):
            del xp_pickle[user_id]

    return embed, view, fp

@tree.command(
    name = "chips",
    description = "View how many chips you have, and whether or not you are in jail",
    guild = ID.GUILD_OBJ
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
        ephemeral = interaction.channel.id not in ID.CHANNEL.BOTS,
        view = view,
        file = fp
    )
