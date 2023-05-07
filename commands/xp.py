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

def xp_create_embed(user):
    data = xp_pickle[user.id] if user.id in xp_pickle else {"xp": 0, "lvl": 0, "ttl": 0}
    xp_needed = xp_equation(data["lvl"] + 1)
    leaders = {}
    for user_id in xp_pickle:
        if xp_pickle[user_id]["ttl"] in leaders:
            leaders[xp_pickle[user_id]["ttl"]].append(user_id)
        else:
            leaders[xp_pickle[user_id]["ttl"]] = [user_id]
    ranks = sorted(set(leaders))
    rank = len(ranks) - ranks.index(data["ttl"])
    embed = discord.Embed(
        description = f"""\
**{str(user.name)}**_#{str(user.discriminator)}_    |    **{data['xp']}**_/{xp_needed} XP_
`[{get_bar(data['xp']/xp_needed)}]`
Level **{data['lvl']}**    |    Rank **#{rank + 1}**
*Total XP: {data["ttl"]}*
""",
        color = 0xA46B31
    )
    leaderboard = ""
    n = 0
    passed = []
    for amount in ranks[::-1][:10]:
        for q in leaders[amount]:
            n += 1
            match n:
                case 1:
                    leaderboard += "\U0001f947"
                case 2:
                    leaderboard += "\U0001f948"
                case 3:
                    leaderboard += "\U0001f949"
                case _:
                    leaderboard += f"**{n:02}.**"
            passed.append(q)
            leaderboard += f" <@{q}>; Lv{xp_pickle[q]['lvl']}\n"
    if user.id not in passed:
        leaderboard += f"...\n**{rank + 1:02}.** <@{user.id}>; Lv{data['lvl']}"
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
    return embed

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
    await interaction.response.send_message(
        embed = xp_create_embed(user),
        ephemeral = interaction.channel.id not in BOT_CHANNELS
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
    await interaction.response.send_message(
        msg,
        embed = xp_create_embed(member),
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
    await interaction.response.send_message(
        msg,
        embed = xp_create_embed(member),
    )
