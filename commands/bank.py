def get_time():
    return str(datetime.datetime.now().timestamp()).split(".")[0]

open(ROOT_DATA + "bank_rob_time", "w+").write(str(get_time()))

try:
    economy_pickle = pickle.loads(open(ROOT_DATA + "economy.pickle", "rb").read())
except:
    economy_pickle = {}


economy_pickle_save = time.time()

def give_chips(user, amount = 0):
    try:
        user_id = str(int(user)) # Ensure snowflake
    except:
        if user.bot:
            return
        user_id = str(user.id)

    global economy_pickle_save, economy_pickle

    if user_id not in economy_pickle:
        economy_pickle[user_id] = amount
    else:
        economy_pickle[user_id] += amount

    economy_pickle[user_id] = max(0, economy_pickle[user_id])

    if time.time() - economy_pickle_save > 30:
        economy_pickle_save = time.time()
        open(ROOT_DATA + "economy.pickle", "wb+").write(pickle.dumps(economy_pickle))

    return economy_pickle[user_id]

def get_chips(user):
    try:
        user_id = str(int(user)) # Ensure snowflake
    except:
        if user.bot:
            return
        user_id = str(user.id)

    if user_id in os.listdir(ROOT_DATA + "jailed"):
        mtime = os.stat(f"{ROOT_DATA}jailed/{user_id}").st_mtime
        if time.time() - mtime < 86400:
            return -1
        os.remove(f"{ROOT_DATA}jailed/{user_id}")
    if user_id not in economy_pickle:
        economy_pickle[user_id] = 0
    return economy_pickle[user_id]


async def chips_ponzi(interaction: discord.Interaction):
    view = discord.ui.View(timeout = None)
    if "custom_id" in interaction.data:
        payout = int(interaction.data["custom_id"].split("payout=")[1].split(";")[0])
        chances = int(interaction.data["custom_id"].split("chances=")[1].split(";")[0])


        if "action=dissolve;" in interaction.data["custom_id"]:
            if chances / 10 > 75:
                msg = f"Phew! Looks like you cached out just in time! The SEC was just starting to get suspicious...\n\n"
            else:
                msg = f"Your investors are upset, the company was just getting off the ground! The operation could "
                msg += "definitely have lasted longer...\n\n"
            msg += f"**-~=:[ MISSION SUMMARY ]:=~-**\n**Result:** Success\n**Payout:** {payout}x {DEAD_EMOJI}"
            msg += f"\n**Total Chips:** {give_chips(interaction.user, payout)}x {DEAD_EMOJI}\n"
            msg += f"**Chance of being caught this month:** {chances / 50:.2f}%"
            embed = discord.Embed(title = "Ponzi Scheme", description = msg, color = 0x22cc22)
            return await interaction.response.edit_message(embed = embed, view = view)

        chances = int(chances * random.uniform(1, 5))
        payout = int(payout * random.uniform(1.5, 3))

    else:
        chances = 1
        payout = 1

    if random.randint(1, 5000) < chances:
        msg = "As you walk towards the entrance of the company building, you see officers standing at the door. You ask "
        msg += "if anything was wrong, and they immediately show you a warrant for your arrest. It looks like one of "
        msg += "your investors was getting suspicious and reported you to the SEC, and all earnings from the operation "
        msg += "was seized permanently.\n\n"
        msg += "**-~=:[ MISSION SUMMARY ]:=~-**\n**Result:** Failure\n**Penalty:** Chips seized for 24 hours\n"
        msg += f"**Potential payout:** {payout}x {DEAD_EMOJI}\n"
        msg += f"**Chance of being caught this month:** {min(chances, 5000) / 50:.2f}%"
        chips_bank_heist_fail(interaction)
        embed = discord.Embed(title = "Ponzi Scheme", description = msg, color = 0xff0000)
        return await interaction.response.edit_message(embed = embed, view = view)

    msg = "A Ponzi Scheme is an elaborate process with heavy emphasis on trust and growth. Instead of making your money "
    msg += "from honest work, you constantly find new investors to bring money into the business. That new money, rather "
    msg += "than being used for development, is used to pay off the old investors of your business.\n\n"
    msg += "The Securities and Exchange Commission (SEC) is notoriously slow to catch on to these schemes, so you can "
    msg += "usually get away with it for a while if you hide it well enough. However, it is important to note that the "
    msg += "moment you stop finding new investors, the entire operation crumbles to the ground, and is revealed to be a "
    msg += "Ponzi immediately. So be careful out there.\n\n"
    msg += "**Note:** Performing a Ponzi Scheme is illegal, due to fraud. This is a completely satirical game, do not play "
    msg += "it in real life.\n\n"
    msg += f"**Current Earnings:** {payout}x {DEAD_EMOJI}"

    view.add_item(
        discord.ui.Button(
            label = "Run Ponzi for another month",
            custom_id = f"chips-ponzi={interaction.user.id};payout={payout};chances={chances}",
            style = discord.ButtonStyle.green
        )
    )
    view.add_item(
        discord.ui.Button(
            label = "Cash out now",
            custom_id = f"chips-ponzi={interaction.user.id};action=dissolve;payout={payout};chances={chances}",
            style = discord.ButtonStyle.grey
        )
    )

    embed = discord.Embed(title = "Ponzi Scheme", description = msg, color = 0xffaa44)

    if "custom_id" in interaction.data:
        await interaction.response.edit_message(embed = embed, view = view)
    else:
        await interaction.response.send_message(embed = embed, view = view, ephemeral = interaction.channel.id not in BOT_CHANNELS)




async def bank_break_free(interaction: discord.Interaction, method: int):
    if get_chips(interaction.user) != -1:
        return await interaction.response.send_message(
            "You don't need to break free if you already are free!",
            ephemeral = interaction.channel.id not in BOT_CHANNELS
        )
    view = discord.ui.View(timeout = None)
    # Spoon
    if method == 1:
        rolls = [random.randint(1, 20), random.randint(1, 20), random.randint(1, 20)]
        desc = f"> You rolled: `{rolls[0]}`, `{rolls[1]}`, `{rolls[2]}`\n"
        desc += "You forage through some raw materials around your cell, and fashion together a spoon. "
        branch = random.randint(1, 4)
        if all(r >= 12 for r in rolls):
            color = 0x22cc22
            if branch == 3:
                desc += "The spoon, while dull and crooked, lasted for just long enough for you to dig around the bolts "
                desc += "on the vent, and you crawl through."
            elif branch == 2:
                desc += "Conveniently, you also have a very gritty floor, meaning you could sharpen the spoon and dig "
                desc += "your way out with ease."
            elif branch == 1:
                desc += "The spoon was too flimsy to do any digging, but was just rigid enough for you to pick the lock "
                desc += "around the window. You slipped through the window and made a safe exit."
            else:
                desc += "The spoon was poorly shaped, and couldn't be used to dig anything. However, because the materials "
                desc += "used were gold and shiny, the prison alpha was persuaded in giving you exit plans in exchange "
                desc += "for the spoon. Well done!"
            os.remove(ROOT_DATA + "jailed/" + str(interaction.user.id))
        else:
            color = 0xff0000
            if branch == 3:
                desc += "You stupidly decided to start digging during the middle of the night, meaning all the noises "
                desc += "echoed through the concrete walls of the prison, waking up guards in the process. They immediately "
                desc += "confiscated your spoon, then sent you to a solitary confinement cell..."
            elif branch == 2:
                desc += "Underwhelmingly, the spoon just shred itself to pieces..."
            elif branch == 1:
                desc += "You couldn't find anything, so the next day, you tried stealing a spoon and knife from the "
                desc += "cafeteria, but the guards caught you and threatened to perform a lobotomy with it if you get caught again..."
            else:
                desc += "You successfully dug around the bolts that closed off the vents. However, you forgot that vent "
                desc += "ducts are very weak, so as you were crawling, the duct snapped in half and you fell straight into "
                desc += "the management office of the prison..."
            view.add_item(
                discord.ui.Button(
                    label = "Try again",
                    custom_id = "chips-free=1",
                    style = discord.ButtonStyle.red
                )
            )
        embed = discord.Embed(
            title = "An attempt to break free, using a spoon",
            description = desc,
            color = color
        )
    embed.set_footer(text = "If we weren't breaking the law before, we certainly are now...")
    if "custom_id" in interaction.data:
        await interaction.response.edit_message(embed = embed, view = view)
    else:
        await interaction.response.send_message(embed = embed, ephemeral = interaction.channel.id not in BOT_CHANNELS, view = view)

@tree.command(
    name = "chips",
    description = "View how many chips you have, and whether or not you are in jail",
    guild = discord.Object(GUILD)
)
@discord.app_commands.guild_only()
async def cmd_bank_chips(interaction: discord.Interaction):
    if get_chips(interaction.user) == -1:
        embed = discord.Embed(
            title = "Ceased",
            description = f"You are in jail, and your {give_chips(interaction.user, 0)}x {DEAD_EMOJI} have been seized. " +\
                          "If you want to break out of jail right now, you can try using `/break-free`.",
            color = 0xff0000
        )
    else:
        embed = discord.Embed(
            title = "On the run",
            description = f"You have {give_chips(interaction.user, 0)}x {DEAD_EMOJI}. But, the FBI is right on your tail, " +\
                          "so be extra cautious in your next `/get-chips` scheme.",
            color = 0x22cc22
        )
    return await interaction.response.send_message(embed = embed, ephemeral = interaction.channel.id not in BOT_CHANNELS)

@tree.command(
    name = "break-free",
    description = "When you've been caught by the police and want to break free",
    guild = discord.Object(GUILD)
)
@discord.app_commands.describe(
    method = "How to break out of jail"
)
@discord.app_commands.choices(
    method = [
        discord.app_commands.Choice(name = "Spoon", value = 1)
    ]
)
@discord.app_commands.guild_only()
async def bank_break_attempt(interaction: discord.Interaction, method: int):
    print(interaction, method)
    return await bank_break_free(interaction, method)


@tree.command(
    name = "get-chips",
    description = "When you feel like you need a few more chips to fill your bag...",
    guild = discord.Object(GUILD)
)
@discord.app_commands.describe(
    method = "How to collect your chips"
)
@discord.app_commands.choices(
    method = [
        discord.app_commands.Choice(name = "Pickpocket", value = 0),
        discord.app_commands.Choice(name = "Exchange 100 XP", value = 2),
        discord.app_commands.Choice(name = "Bank Heist", value = 1),
        discord.app_commands.Choice(name = "Ponzi Scheme", value = 3)
    ]
)
@discord.app_commands.guild_only()
async def cmd_get_chips(interaction: discord.Interaction, method: int):
    # Rob the bank
    if str(interaction.user.id) in os.listdir(ROOT_DATA + "jailed"):
        mtime = os.stat(f"{ROOT_DATA}jailed/{interaction.user.id}").st_mtime
        if time.time() - mtime < 86400:
            release = f"<t:{int(mtime) + 86400}:R>"
            embed = discord.Embed(
                title = "Jail",
                description = f"Sorry, you can only think about future schemes while you are in jail. You will be released {release}. Or, you can use `/break-free`",
                color = 0xff0000
            )
            embed.set_footer(text = "Yes, we run a risky and dirty business...")
            return await interaction.response.send_message(embed = embed, ephemeral = interaction.channel.id not in BOT_CHANNELS)
        os.remove(f"{ROOT_DATA}jailed/{interaction.user.id}")
    if method == 0:
        ttl = get_chips(interaction.user.id)
        if ttl <= 35:
            gain = random.randint(15, 50)
        elif ttl <= 10000:
            gain = random.randint(1, 5)
        else:
            return await interaction.response.send_message(
                "You are already drowning in chips! You don't need to pickpocket anymore",
                ephemeral = interaction.channel.id not in BOT_CHANNELS
            )
        ttl = give_chips(interaction.user.id, gain)
        return await interaction.response.send_message(
            f"Your pickpocket attempt netted {gain} new chips! You now have {ttl}x {DEAD_EMOJI}",
            ephemeral = interaction.channel.id not in BOT_CHANNELS
        )
    if method == 1:
        return await get_chips_rob_bank(interaction, "0")
    if method == 2:
        if interaction.user.id in xp_pickle and xp_pickle[interaction.user.id]["ttl"] > 10:
            trade = min(xp_pickle[interaction.user.id]["ttl"], 100)
            earnings = give_chips(interaction.user, trade // 5)
            give_xp(interaction.user, -trade)
            return await interaction.response.send_message(
                f"You exchanged {trade} XP for {trade // 5}x {DEAD_EMOJI}, and now have {earnings}x {DEAD_EMOJI} total.",
                ephemeral = interaction.channel.id not in BOT_CHANNELS
            )
        return await interaction.response.send_message(
            f"You don't have enough XP to trade for even one chip! Try chatting a bit in the discussion channels",
            ephemeral = interaction.channel.id not in BOT_CHANNELS
        )
    if method == 3:
        return await chips_ponzi(interaction)
    print(interaction, method)


async def cmd_handle_give_chips(interaction, member, amount, till):
    ephemeral = interaction.channel.id not in BOT_CHANNELS
    if not till and not amount:
        return await interaction.response.send_message("Success! Nothing happened...", ephemeral = ephemeral)
    if interaction.permissions.administrator:
        now = give_chips(member, amount)
        if till:
            amount = till - now
        if amount < 0:
            msg = f"Took {-amount} chip{'s' if abs(amount) == 1 else ''} away!"
        else:
            msg = f"Gave {amount} chip{'s' if abs(amount) == 1 else ''}"
        msg += f"\n{member.nick or member.name} now has {now}x {DEAD_EMOJI}"
        await interaction.response.send_message(msg, ephemeral = ephemeral)
    else:
        if amount < 0:
            return await interaction.response.send_message(
                f"You can't take chips from {member.nick or member.name}! Their safe is too secure!",
                ephemeral = ephemeral
            )
        if till:
            amount = till - give_chips(member)
        amount = min(int(get_chips(interaction.user) / 2), amount)
        give_chips(interaction.user, -amount)
        return await interaction.response.send_message(
            f"You gave {amount}x {DEAD_EMOJI} to <@{member.id}>, and no taksie-backsies. They now have {give_chips(member, amount)} total.",
            ephemeral = ephemeral
        )

@tree.command(
    name = "give-chips",
    description = "Give chips to a user",
    guild = discord.Object(GUILD)
)
@discord.app_commands.describe(
    member = "Who to give chips to",
    amount = "How many chips to give. Use a negative number to take chips away",
    till = "How many chips you want them to have, total"
)
@discord.app_commands.guild_only()
async def cmd_give_chips(interaction: discord.Interaction, member: discord.Member, amount: int = 0, till: int = 0):
    return await cmd_handle_give_chips(interaction, member, amount, till)


@tree.command(
    name = "take-chips",
    description = "Take chips from a user",
    guild = discord.Object(GUILD)
)
@discord.app_commands.describe(
    member = "Who to take chips from",
    amount = "How many chips to take. Use a negative number to give chips"
)
@discord.app_commands.default_permissions(
    administrator = True
)
@discord.app_commands.guild_only()
async def cmd_take_xp(interaction: discord.Interaction, member: discord.Member, amount: int = 0, till: int = 0):
    return await cmd_handle_give_chips(interaction, member, -amount, till)

async def on_chips_interaction(interaction: discord.Interaction):
    data = interaction.data
    btn_id = data["custom_id"]

    if btn_id.startswith("chips-free="):
        return await bank_break_free(interaction, int(btn_id.split("=")[1]))

    if str(interaction.user.id) != btn_id.split("=")[1].split(";")[0]:
        return await interaction.response.send_message(
            "Sorry, you can't interfere with someone else's operation! Be a good criminal and start your own...",
            ephemeral = True, delete_after = 5
        )

    if btn_id.startswith("chips-bank="):
        return await get_chips_rob_bank(interaction, stage = btn_id.split("stage=")[1].split(";")[0])

    if btn_id.startswith("chips-ponzi="):
        return await chips_ponzi(interaction)
