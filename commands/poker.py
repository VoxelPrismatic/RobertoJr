ROOT.GAMES.POKER = ROOT.DATA + "games/poker/"

def rng_id():
    game_id = f"{random.randint(0, 65535):04x}"
    game_ids = os.listdir(ROOT.GAMES.POKER)
    while game_id in game_ids and time.time() - os.stat(ROOT.GAMES.POKER + game_id).st_mtime < 600:
        game_id = f"{random.randint(0, 65535):04x}"

    return game_id

def shuffle_cards(cards, num_riffles = random.randint(2, 5)):
    # Scramble on table
    for x in range(len(cards)):
        bound = min(len(cards) - 1, max(0, random.randint(x - 12, x + 12)))
        cards[x], cards[bound] = cards[bound], cards[x]

    # Split and riffle
    for x in range(num_riffles):
        stack_n = random.randint(16, 36)
        stack_1 = cards[:stack_n]
        stack_2 = cards[stack_n:]
        cards = []
        while stack_1 or stack_2:
            if random.randint(0, 1) and stack_2:
                cards.append(stack_2.pop())
            elif stack_1:
                cards.append(stack_1.pop())


    stack_n = random.randint(16, 36)
    cards = cards[stack_n:] + cards[:stack_n]

    return cards

def pop_card(game_data):
    card = game_data["cards"].pop()
    game_data["used-cards"].append(card)
    return card

@tree.command(
    name = "poker",
    description = "Texas-Hold 'Em style poker, you can invite up to 8 people",
    guild = ID.GUILD_OBJ
)
@discord.app_commands.describe(
    player1 = "Who do you want to invite? You do not need to invite yourself",
    player2 = "Who do you want to invite? You do not need to invite yourself",
    player3 = "Who do you want to invite? You do not need to invite yourself",
    player4 = "Who do you want to invite? You do not need to invite yourself",
    player5 = "Who do you want to invite? You do not need to invite yourself",
    player6 = "Who do you want to invite? You do not need to invite yourself",
    player7 = "Who do you want to invite? You do not need to invite yourself",
    player8 = "Who do you want to invite? You do not need to invite yourself",
    blind_size = "How big the blinds should be. Default is 5/10 for SB/BB respectively"
)
@discord.app_commands.choices(
    blind_size = [
        discord.app_commands.Choice(name = "SB/BB = 1/2", value = 1),
        discord.app_commands.Choice(name = "SB/BB = 5/10", value = 5),
        discord.app_commands.Choice(name = "SB/BB = 20/40", value = 20),
        discord.app_commands.Choice(name = "SB/BB = 50/100", value = 50),
        discord.app_commands.Choice(name = "SB/BB = 100/200", value = 100)
    ]
)
@discord.app_commands.guild_only()
async def poker(interaction: discord.Interaction, player1: discord.Member = None, player2: discord.Member = None,
                player3: discord.Member = None, player4: discord.Member = None, player5: discord.Member = None,
                player6: discord.Member = None, player7: discord.Member = None, player8: discord.Member = None,
                blind_size: int = 5):
    if interaction.channel.id not in ID.CHANNEL.BOTS:
        msg = "Sorry, you can only play poker in the following channels:\n- "
        msg += "\n- ".join(f'<#{c}>' for c in ID.CHANNEL.BOTS)
        return await interaction.response.send_message(msg, ephemeral = True, delete_after = 10)
    players = [interaction.user]
    view = discord.ui.View(timeout = None)
    game_id = rng_id()

    if get_chips(interaction.user) == -1:
        msg = "Whoops! The guards already confiscated your cards, so you can't play poker anyway!"
        return await interaction.response.send_message(msg)
    if get_chips(interaction.user) == 0:
        msg = f"Whoops! You can't play if you don't have a bet to make! Use {COMMAND_STR('get-chips')} to get started!"
        return await interaction.response.send_message(msg)


    for player in [player1, player2, player3, player4, player5, player6, player7, player8]:
        if player is None or player in players:
            continue
        players.append(player)
        n_chips = get_chips(player)
        if n_chips == -1 or player.bot:
            msg = "Woops! You can't play with the prisoner, " + (player.nick or player.name) + "!"
            return await interaction.response.send_message(msg)
        elif n_chips == 0:
            msg = "Woops! You can't play with " + (player.nick or player.name) + ", who is completely broke!"
            return await interaction.response.send_message(msg)
        view.add_item(
            discord.ui.Button(
                style = discord.ButtonStyle.green,
                custom_id = f"poker-join={player.id};match={game_id}",
                label = (player.name if len(player.name) < 15 else player.name[:12] + "...") + ": Ready!",
                emoji = chr(0x2f + len(players)) + "\ufe0f\u20e3"
            )
        )

    open(ROOT.GAMES.POKER + game_id, "w+").write(json.dumps({
        "waiting": [str(p.id) for p in players[1:]],
        "joined": [str(players[0].id)],
        "blind-size": blind_size
    }, indent = 4))

    if len(players) == 1:
        return await interaction.response.send_message(
            "**Welcome to Poker!**\n" + \
            "You can play with up to 8 other members of the server by specifying who you want to play with in the " + \
            "`player#` argument.\nYou may not play with yourself, as I am very bad at poker, and will remain " + \
            "as your dealer. \n\n" + \
            "To set the small blind and big blind bets, use the `blind_size` argument. Default is 5/10 for SB/BB " + \
            "respectively\n\n" + \
            "But just remember, this is a lucrative business here. Your chips are taken away as the game progresses, " + \
            "and you can only get them back after the game has ended. If somebody walks away from the table, then " + \
            "everyone is screwed. This is how we make our profits around here. We need the money for legal expenses " + \
            "against the government of West Virginia, as poker is illegal...\n\n" + \
            "If you spot any issues, feel free to ping `PRIZ ;]#9244` with your suggestions"
        )
    # await interaction.response.defer(thinking = False)
    return await interaction.response.send_message(
        ", ".join(f'<@{u.id}>' for u in players[1:]) + \
            f", you have been invited to poker, Texas-Hold'em style!",
        view = view
    )

async def poker_player_join(interaction: discord.Interaction, game_id):
    game_data = json.loads(open(ROOT.GAMES.POKER + game_id).read())
    game_data["joined"].append(str(interaction.user.id))
    game_data["waiting"].remove(str(interaction.user.id))

    open(ROOT.GAMES.POKER + game_id, "w+").write(json.dumps(game_data, indent = 4))

    if len(game_data["waiting"]) == 0:
        return await poker_begin_seating(interaction, interaction.user.id, game_id)

    view = discord.ui.View(timeout = None)
    player_emojis = 0x31
    for player in game_data["waiting"]:
        user = interaction.guild.get_member(player)
        if user is None:
            user = await interaction.guild.fetch_member(player)
        view.add_item(
            discord.ui.Button(
                style = discord.ButtonStyle.green,
                custom_id = f"poker-join={player};match={game_id}",
                label = (user.name if len(user.name) < 15 else user.name[:12] + "...") + ": Ready!",
                emoji = chr(player_emojis) + "\ufe0f\u20e3"
            )
        )
        player_emojis += 1
    await interaction.response.send_message(
        content = ", ".join(f'<@{u}>' for u in game_data["waiting"]) + \
            f", you have been invited to poker, Texas-Hold'em style!",
        view = view
    )
    return await interaction.followup.delete_message(interaction.message.id)

CARD_SUITES = {
    "S": "\u2660",
    "H": "\u2665",
    "C": "\u2663",
    "D": "\u2666",
}

def reveal_cards(cards):
    return " | ".join(f"{c[0]}{CARD_SUITES[c[1]]}" for c in cards).replace("T", "10")

async def poker_create_embed(game_id, game_data):
    positions = ["\x39\ufe0f\u20e3", "\x38\ufe0f\u20e3", "\x37\ufe0f\u20e3",
                 "\x36\ufe0f\u20e3", "\x35\ufe0f\u20e3", "\x34\ufe0f\u20e3",
                 "\x33\ufe0f\u20e3", "\U0001f536", "\U0001f539"]
    position_marker = "<a:arrow:1103200368734765116>"
    position_fold = "\u274c"
    card_emoji = "\U0001f3b4"
    ttl_bet = game_data["pot"]
    description = f"\U0001f4cc <@{bot.user.id}> **Pot:** {ttl_bet}x {ID.EMOJI.DEAD}\n    "
    description += (reveal_cards(game_data["visible"][:5]) or "*still in pre-flop*") + "\n\n"
    values = {}
    game_over = len(game_data["visible"]) >= 6
    big_blind = max(list(game_data["bets"].values()))
    for player in game_data["joined"]:
        position = positions.pop()
        if player in game_data["folded"]:
            game_data['action'][player] = "" if game_over else position_fold
            description += position_fold
        elif game_over:
            description += position
        elif player == game_data["current"]:
            description += position_marker
        else:
            description += position
        description += f" <@{player}> **Bet:** {game_data['bets'][player]}x {ID.EMOJI.DEAD} {game_data['action'][player]}\n"
        if player in game_data["shown"]:
            description += reveal_cards(game_data["hands"][player]) + f" | Table: {game_data['on-table'][player]} chips\n\n"
        else:
            description += (card_emoji * len(game_data["hands"][player])) + f" Table: {game_data['on-table'][player]} chips\n\n"
        if game_over:
            if player not in game_data["folded"]:
                values[player] = evaluate_cards(*game_data["hands"][player], *game_data["visible"][:5])

    if not game_over:
        description += f"**Minimum bet amount:** {big_blind}"
        description += "\n\n**Note:** To view your hand, click the blue 'View hand' button below"

    if random.choice(PROMO_CHANCE) == 0:
        description += SHAMELESS_PROMO

    embed = discord.Embed(
        title = "Poker - Texas-Hold'em",
        description = description,
        color = 0x0088ff
    )
    embed.set_footer(text = "Totally legal by West Virginia law...")

    view = discord.ui.View(timeout = None)

    if game_over:
        for player in game_data["joined"]:
            if player in game_data["shown"]:
                continue
            mbr = bot.get_guild(ID.GUILD).get_member(player)
            if mbr is None:
                mbr = await bot.get_guild(ID.GUILD).fetch_member(player)
            view.add_item(
                discord.ui.Button(
                    label = (mbr.name if len(mbr.name) < 15 else mbr.name[:12] + "...") + ": Reveal Cards!",
                    custom_id = f"poker-reveal={player};match={game_id}",
                    style = discord.ButtonStyle.grey
                )
            )
        view.add_item(
            discord.ui.Button(
                label = "Play Again",
                custom_id = f"poker-rematch=ANY;match={game_id}",
                style = discord.ButtonStyle.blurple,
                row = 1
            )
        )
        winner = min(list(values.values()))
        for player in values:
            if values[player] == winner:
                return embed, view, player

    if game_data["on-table"][game_data["current"]] > 0:
        if big_blind >= game_data["on-table"][game_data["current"]]:
            view.add_item(
                discord.ui.Button(
                    label = "Call (all in)",
                    custom_id = f"poker-play={game_data['current']};action=call;match={game_id}",
                    style = discord.ButtonStyle.green,
                    emoji = "\U0001f64f"
                )
            )
        elif big_blind == game_data["bets"][game_data["current"]]:
            view.add_item(
                discord.ui.Button(
                    label = "Check (skip)",
                    custom_id = f"poker-play={game_data['current']};action=check;match={game_id}",
                    style = discord.ButtonStyle.green,
                    emoji = "\u2611\ufe0f"
                )
            )
        else:
            view.add_item(
                discord.ui.Button(
                    label = "Call (match bet)",
                    custom_id = f"poker-play={game_data['current']};action=call;match={game_id}",
                    style = discord.ButtonStyle.green,
                    emoji = "\U0001f919"
                )
            )
        view.add_item(
            discord.ui.Button(
                label = "Raise (increase bet)",
                custom_id = f"poker-raise-modal={game_data['current']};action=raise;match={game_id}",
                style = discord.ButtonStyle.grey,
                emoji = "\u23eb"
            )
        )
    else:
        mbr = bot.get_guild(ID.GUILD).get_member(game_data['current'])
        if mbr is None:
            mbr = await bot.get_guild(ID.GUILD).fetch_member(game_data['current'])
        view.add_item(
            discord.ui.Button(
                label = (mbr.name if len(mbr.name) < 15 else mbr.name[:12] + "...") + ": You ran out of chips",
                custom_id = f"poker-raise-modal={game_data['current']};action=call;match={game_id}",
                style = discord.ButtonStyle.grey,
                disabled = True
            )
        )
    view.add_item(
        discord.ui.Button(
            label = "Fold (resign)",
            custom_id = f"poker-play={game_data['current']};action=fold;match={game_id}",
            style = discord.ButtonStyle.red,
            emoji = "\u2716\ufe0f",
            row = 1
        )
    )
    view.add_item(
        discord.ui.Button(
            label = "View hand",
            custom_id = f"poker-view={game_data['current']};match={game_id}",
            style = discord.ButtonStyle.blurple,
            emoji = "\U0001f0cf",
            row = 1
        )
    )

    return embed, view, None


async def poker_begin_seating(interaction: discord.Interaction, user_id, game_id):
    game_data = json.loads(open(ROOT.GAMES.POKER + game_id).read())
    if "custom_id" in interaction.data and interaction.data["custom_id"].startswith("poker-seating"):
        position = str(interaction.data["custom_id"].split("position=")[1].split(";")[0])
        game_data["seating"][position] = user_id
    else:
        game_data["seating"] = {}
        random.shuffle(game_data["joined"])
    try:
        player = game_data["joined"].pop()
    except:
        for position in sorted(int(i) for i in game_data["seating"]):
            game_data["joined"].append(game_data["seating"][str(position)])
        open(ROOT.GAMES.POKER + game_id, "w+").write(json.dumps(game_data, indent = 4))
        return await poker_begin_bets(interaction, interaction.user.id, game_id)

    open(ROOT.GAMES.POKER + game_id, "w+").write(json.dumps(game_data, indent = 4))

    positions = {
        "1": ["the small blind", "\U0001f539"],
        "2": ["the big blind", "\U0001f536"],
        "3": ["in position 3", "\x33\ufe0f\u20e3"],
        "4": ["in position 4", "\x34\ufe0f\u20e3"],
        "5": ["in position 5", "\x35\ufe0f\u20e3"],
        "6": ["in position 6", "\x36\ufe0f\u20e3"],
        "7": ["in position 7", "\x37\ufe0f\u20e3"],
        "8": ["in position 8", "\x38\ufe0f\u20e3"],
        "9": ["in position 9", "\x39\ufe0f\u20e3"]
    }

    desc = ""
    msg = f"<@{player}>, your turn to take a seat:"

    view = discord.ui.View(timeout = None)
    for position in sorted(int(i) for i in game_data["seating"]):
        desc += f"{positions[str(position)][1]} <@{game_data['seating'][str(position)]}> is {positions[str(position)][0]}\n"
        del positions[str(position)]

    n = -1
    for position in positions:
        n += 1
        if int(position) > len(game_data["joined"]) + len(list(game_data["seating"])) + 1:
            continue
        view.add_item(
            discord.ui.Button(
                label = positions[position][0].split(" ", 1)[1].title(),
                custom_id = f"poker-seating={player};position={position};match={game_id}",
                style = discord.ButtonStyle.red if int(position) < 3 else discord.ButtonStyle.grey,
                row = n // 3
            )
        )

    embed = discord.Embed(
        title = "Choose your seats",
        description = desc,
        color = 0x0088ff
    )

    embed.set_footer(text = "Totally legal by West Virginia law...")

    await interaction.response.send_message(msg, embed = embed, view = view)
    await interaction.followup.delete_message(interaction.message.id)

async def poker_begin_bets(interaction: discord.Interaction, user_id, game_id, exists = False):
    game_data = json.loads(open(ROOT.GAMES.POKER + game_id).read())
    base_bet = game_data["blind-size"]
    game_data["bets"] = {}
    game_data["action"] = {c: "" for c in game_data['joined']}
    game_data["pot"] = 0

    for i, player in enumerate(game_data["joined"]):
        if i == 0:
            game_data["bets"][player] = base_bet
        elif i == 1:
            game_data["bets"][player] = base_bet * 2
        else:
            game_data["bets"][player] = 0
        game_data["pot"] += game_data["bets"][player]


    open(ROOT.GAMES.POKER + game_id, "w+").write(json.dumps(game_data, indent = 4))
    if not exists:
        return await poker_bring_chips(interaction, interaction.user.id, game_id)
    for player in game_data['joined'][:]:
        if game_data["on-table"][player] <= 0:
            game_data["joined"].remove(player)
            continue
        game_data['on-table'][player] -= game_data['bets'][player]
        give_chips(player, -game_data['bets'][player])
        open(ROOT.GAMES.POKER + game_id, "w+").write(json.dumps(game_data, indent = 4))
    if len(game_data["joined"]) == 1:
        await interaction.response.send_message(
            "Woops! Looks like everyone has been eliminated!\n"
            f"**Congrats, <@{game_data['joined'][0]}>!** \U0001f389\U0001f389\U0001f389"
        )
        return await interaction.followup.edit_message(interaction.message.id, view = discord.ui.View(timeout = None))
    return await poker_begin_match(interaction, game_id)

async def poker_begin_match(interaction: discord.Interaction, game_id):
    game_data = json.loads(open(ROOT.GAMES.POKER + game_id).read())

    # Setup
    game_data["folded"] = []
    game_data["current"] = (game_data["joined"] * 3)[2]
    game_data["visible"] = []
    game_data["shown"] = []
    game_data["all-in"] = []

    # Create deck
    if "cards" not in game_data:
        game_data["cards"] = []
        for suit in "SHCD":
            for value in "A23456789TJQK":
                game_data["cards"].append(value + suit)
    else:
        game_data["cards"] = game_data["used-cards"] + game_data["cards"]
    game_data["used-cards"] = []

    # Shuffle deck
    game_data["cards"] = shuffle_cards(game_data["cards"], random.randint(6, 9))

    # Hand out cards
    game_data["hands"] = {u: [] for u in game_data["joined"]}

    for r in range(2):
        for player in game_data["joined"]:
            game_data["hands"][player].append(pop_card(game_data))

    game_id = rng_id()
    open(ROOT.GAMES.POKER + game_id, "w+").write(json.dumps(game_data, indent = 4))

    embed, view, winner = await poker_create_embed(game_id, game_data)
    # await interaction.delete_original_response()
    await interaction.response.send_message(
        content = f"Alright, <@{game_data['current']}> is up!",
        embed = embed,
        view = view
    )
    await interaction.followup.edit_message(interaction.message.id, view = None)
    # msg = await interaction.original_response()
    # await interaction.message.edit(content = f"Game is currently here: {msg.jump_url}", view = discord.ui.View(timeout = None))

async def poker_continue_match(interaction: discord.Interaction, user_id, game_id, action):
    game_data = json.loads(open(ROOT.GAMES.POKER + game_id).read())
    big_blind = max(list(game_data["bets"].values()))
    if action == "fold":
        game_data["folded"].append(user_id)
    elif action == "call":
        game_data["action"][user_id] = "\U0001f919"
        if big_blind >= game_data["on-table"][user_id]:
            game_data["action"][user_id] = "\U0001f64f"
            game_data["all-in"].append(user_id)
        game_data["bets"][user_id] = min(big_blind, game_data["on-table"][user_id])
        game_data["on-table"][user_id] -= game_data["bets"][user_id]
        give_chips(user_id, -game_data["bets"][user_id])
        game_data["pot"] += game_data["bets"][user_id]
    elif action == "raise":
        game_data["action"][user_id] = "\u23eb"
        btn_id = interaction.data["custom_id"]
        amount = interaction.data["components"][0]["components"][0]["value"].strip()
        try:
            amount = int(amount)
        except:
            return await interaction.response.send_message(
                f"Whoops! `{amount}` isn't a number",
                ephemeral = True, delete_after = 10
            )
        if amount < big_blind:
            return await interaction.response.send_message(
                f"Whoops! You must bet more than the big blind of {big_blind}x {ID.EMOJI.DEAD}",
                ephemeral = True, delete_after = 10
            )
        if amount > game_data["on-table"][user_id]:
            return await interaction.response.send_message(
                f"You cannot bet more chips than you have on the table, which is {game_data['on-table'][user_id]} chips",
                ephemeral = True, delete_after = 10
            )
        game_data["bets"][user_id] = amount

        game_data["on-table"][user_id] -= amount
        if game_data["on-table"][user_id] == 0:
            game_data["action"][user_id] = "\U0001f64f"
            game_data["all-in"].append(user_id)
        give_chips(user_id, -amount)
        game_data["pot"] += amount
    elif action == "check":
        game_data["action"][user_id] = "\u2611\ufe0f"


    cur_array = game_data["joined"] * 2
    skipable = (game_data["folded"] + game_data["all-in"])
    after_second = cur_array[1]
    n = 0
    while after_second in skipable and n < 24:
        after_second = cur_array[cur_array.index(after_second) + 1]
        n += 1

    if user_id == after_second:
        for player in game_data["bets"]:
            if player in skipable:
                continue
            if game_data["bets"][player] != big_blind:
                break
        else:
            if len(game_data["visible"]) == 0:
                pop_card(game_data)
                game_data["visible"].append(pop_card(game_data))
                game_data["visible"].append(pop_card(game_data))
            game_data["visible"].append(pop_card(game_data))

    if len(game_data["joined"]) <= (len(skipable) + 1):
        game_data["visible"].append(pop_card(game_data))
        game_data["visible"].append(pop_card(game_data))
        game_data["visible"].append(pop_card(game_data))
        game_data["visible"].append(pop_card(game_data))
        game_data["visible"].append(pop_card(game_data))
        game_data["visible"].append(pop_card(game_data))


    game_data["current"] = cur_array[cur_array.index(game_data["current"]) + 1]
    n = 0
    while game_data["current"] in skipable and n < 24:
        game_data["current"] = cur_array[cur_array.index(game_data["current"]) + 1]
        n += 1

    game_data["action"][game_data["current"]] = ""
    open(ROOT.GAMES.POKER + game_id, "w+").write(json.dumps(game_data, indent = 4))

    embed, view, winner = await poker_create_embed(game_id, game_data)
    if winner:
        pot = game_data["pot"]
        give_chips(winner, pot)
        game_data['on-table'][winner] += pot
        score = evaluate_cards(*game_data["hands"][winner], *game_data["visible"][:5])
        if score == 0:
            method = "with an **Impossible Hand!"
        elif score == 1:
            method = "with a **Royal Flush!**"
        elif score < 11:
            method = "with a **Straight Flush!**"
        elif score < 170:
            method = "with **Four of a Kind!**"
        elif score < 330:
            method = "with a **Full House!**"
        elif score < 1200:
            method = "with a **Flush!**"
        elif score < 1600:
            method = "with **Three of a Kind!**"
        elif score < 3500:
            method = "with **Two Pairs!**"
        elif score < 7000:
            method = "with a **Pair!**"
        else:
            method = "with **Utter Garbage!**"
        game_data["action"] = {c: "" for c in game_data['joined']}
        open(ROOT.GAMES.POKER + game_id, "w+").write(json.dumps(game_data, indent = 4))
        msg = f"<@{winner}> wins {pot}x {ID.EMOJI.DEAD} {method}"
    else:
        msg = f"Alright, <@{game_data['current']}> is up!"

    await interaction.response.send_message(content = msg, embed = embed, view = view)
    # msg = await interaction.original_response()
    await interaction.followup.delete_message(interaction.message.id)
    # await interaction.followup.edit_message(
    #     interaction.message.id,
    #     content = f"The latest update is over here: {msg.jump_url}",
    #     view = discord.ui.View(timeout = None),
    #     embed = None
    # )

    # await interaction.delete_original_response()
    # await interaction.response.send_message(
    #     content = msg,
    #     embed = embed,
    #     view = view
    # )



async def on_poker_interaction(interaction: discord.Interaction):
    data = interaction.data
    btn_id = data["custom_id"]
    game_id = btn_id.split("match=")[-1]

    if btn_id.startswith("poker-n-a"):
        return await interaction.response.defer(thinking = False)
    if btn_id.startswith("poker-view="):
        game_data = json.loads(open(ROOT.GAMES.POKER + game_id).read())
        modal = discord.ui.Modal(title = "Your cards", timeout = None, custom_id = "poker-n-a")
        if str(interaction.user.id) not in game_data["joined"]:
            modal.add_item(
                discord.ui.TextInput(
                    label = "You are not part of this match",
                    custom_id = "nah",
                    default = "Please use the /poker command to start one of your own"
                )
            )
        else:
            modal.add_item(
                discord.ui.TextInput(
                    label = "Cards",
                    custom_id = "nah",
                    default = reveal_cards(game_data["hands"][str(interaction.user.id)])
                )
            )
        return await interaction.response.send_modal(modal)

    if btn_id.startswith("poker-rematch=ANY"):
        game_data = json.loads(open(ROOT.GAMES.POKER + game_id).read())
        game_data["joined"] = game_data["joined"][1:] + [game_data["joined"][0]]
        open(ROOT.GAMES.POKER + game_id, "w+").write(json.dumps(game_data, indent = 4))
        return await poker_begin_bets(interaction, str(interaction.user.id), game_id, True)

    if str(interaction.user.id) != btn_id.split("=")[1].split(";")[0]:
        modal = discord.ui.Modal(title = "Notice", timeout = None, custom_id = "poker-n-a")
        modal.add_item(
            discord.ui.TextInput(
                label = "Sorry",
                custom_id = "nah",
                default = "Sorry, you can't reveal someone else's cards!" if "reveal" in btn_id else "Sorry, it's not your turn!"
            )
        )
        return await interaction.response.send_modal(modal)

    if btn_id.startswith("poker-join="):
        return await poker_player_join(interaction, game_id)
    if btn_id.startswith("poker-start-modal="):
        modal = discord.ui.Modal(
            title = "Place your bets",
            timeout = None,
            custom_id = btn_id.replace("start-modal", "bring-chips")
        )

        modal.add_item(
            discord.ui.TextInput(
                label = "How many chips do you want to bring?",
                custom_id = "bet-amount",
                placeholder = f"You have {get_chips(interaction.user):,} chips available"
            )
        )

        return await interaction.response.send_modal(modal)

    if btn_id.startswith("poker-reveal="):
        game_data = json.loads(open(ROOT.GAMES.POKER + game_id).read())
        game_data["shown"].append(str(interaction.user.id))
        open(ROOT.GAMES.POKER + game_id, "w+").write(json.dumps(game_data, indent = 4))
        embed, view, winner = await poker_create_embed(game_id, game_data)
        return await interaction.response.edit_message(content = interaction.message.content, embed = embed, view = view)

    if btn_id.startswith("poker-bring-chips"):
        user_id = btn_id.split("=")[1].split(";")[0]
        return await poker_bring_chips(interaction, user_id, game_id)

    if btn_id.startswith("poker-seating"):
        user_id = btn_id.split("=")[1].split(";")[0]
        return await poker_begin_seating(interaction, user_id, game_id)

    if btn_id.startswith("poker-play="):
        user_id = btn_id.split("=")[1].split(";")[0]
        play_action = btn_id.split("action=")[1].split(";")[0]
        return await poker_continue_match(interaction, user_id, game_id, play_action)

    if btn_id.startswith("poker-raise-modal="):
        game_data = json.loads(open(ROOT.GAMES.POKER + game_id).read())
        modal = discord.ui.Modal(
            title = "Place your bets",
            timeout = None,
            custom_id = btn_id.replace("raise-modal", "play")
        )

        modal.add_item(
            discord.ui.TextInput(
                label = "Amount",
                custom_id = "bet-amount",
                placeholder = f"You have {game_data['on-table'][str(interaction.user.id)]:,} chips on the table"
            )
        )
        return await interaction.response.send_modal(modal)






async def poker_bring_chips(interaction: discord.Interaction, user_id, game_id):
    game_data = json.loads(open(ROOT.GAMES.POKER + game_id).read())
    print(interaction.data)
    if "custom_id" in interaction.data and interaction.data["custom_id"].startswith("poker-bring-chips"):
        if interaction.data["custom_id"].startswith("poker-bring-chips-all"):
            amount = 0
        else:
            amount = interaction.data["components"][0]["components"][0]["value"].strip()
            try:
                amount = int(amount)
            except:
                return await interaction.response.send_message(
                    f"Woops! `{amount}` isn't a number. No fret, you can click the button to bet again",
                    ephemeral = True,
                    delete_after = 10
                )
        if len(list(game_data["on-table"])) == 0 and amount <= 0:
            return await interaction.response.send_message(
                f"Woops! You can't bet nothing. No fret, you can click the button to bet again",
                ephemeral = True,
                delete_after = 10
            )
        elif amount > get_chips(interaction.user):
            return await interaction.response.send_message(
                f"Whoops! You can't spend more than you have: {get_chips(interaction.user):,}x {ID.EMOJI.DEAD}."
                    "No fret, you can click the button to bet again",
                ephemeral = True,
                delete_after = 10
            )
        game_data["on-table"][str(user_id)] = amount
    else:
        game_data["on-table"] = {}

    open(ROOT.GAMES.POKER + game_id, "w+").write(json.dumps(game_data, indent = 4))

    desc = ""
    msg = ""
    for i, player in enumerate(game_data["joined"]):
        if str(player) not in game_data["on-table"]:
            msg += f"\n<@{player}>, you're up!"
            break
        else:
            desc += f"<@{player}> brings {game_data['on-table'][str(player)]:,}x {ID.EMOJI.DEAD}\n"
    else:
        for player in game_data['joined']:
            game_data['on-table'][player] -= game_data['bets'][player]
            give_chips(player, -game_data['bets'][player])
        open(ROOT.GAMES.POKER + game_id, "w+").write(json.dumps(game_data, indent = 4))
        return await poker_begin_match(interaction, game_id)
    warning = "\n\n**Note:** This is how many chips you are bringing, not your bet. " + \
              "We suggest bringing at least 100 chips"
    embed = discord.Embed(
        title = "Time to bring your chips!",
        description = desc + warning,
        color = 0x0088ff
    )
    embed.set_footer(text = "Totally legal by West Virginia law...")

    view = discord.ui.View(timeout = None)
    view.add_item(
        discord.ui.Button(
            label = "Choose amount",
            custom_id = f"poker-start-modal={player};match={game_id}",
            style = discord.ButtonStyle.blurple,
            emoji = ID.EMOJI.DEAD
        )
    )
    view.add_item(
        discord.ui.Button(
            label = "All in",
            custom_id = f"poker-bring-chips-all={player};match={game_id}",
            style = discord.ButtonStyle.green
        )
    )

    await interaction.response.send_message(content = msg, embed = embed, view = view)
    await interaction.followup.delete_message(interaction.message.id)
    # await interaction.message.delete()
