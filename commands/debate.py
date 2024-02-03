CAGE_NAMES = [
    "luna", "aurelia", "rowan", "kai", "jasper", "leo", "chloe", "rory", "cordelia", "cyrus", "river", "rhys", "elio",
    "aurelius", "celeste", "cressida", "danica", "sienna", "maya", "seraphina", "phoenix", "kaia", "persephone", "ayla",
    "cosmo", "flynn", "mira", "talia", "zephyr", "apollo", "ash", "aria", "brooks", "juno", "astrid", "bianca", "leia",
    "jade", "tallulah", "gemma", "ren", "rowan", "cole", "deva", "kiara", "aiden", "rufus", "ignatius", "aaron", "june",
    "hayden", "marigold", "amaya", "mason", "adam", "eve", "diana", "hanwi", "ophelia", "portia", "amruta", "stella",
    "ara", "ursa", "comet", "archer", "galileo", "astra"
]

@tree.command(
    name = "debate",
    description = "Start a public debate room with another user!",
    guild = ID.GUILD_OBJ
)
@discord.app_commands.describe(
    topic = "Topic of debate",
    chicken1 = "Person 1",
    chicken2 = "Person 2",
    theme = "Whether or not it should be themed around chickens"
)
@discord.app_commands.rename(
    chicken1 = "person1",
    chicken2 = "person2"
)
@discord.app_commands.choices(
    theme = [
        discord.app_commands.Choice(name = "Debate", value = 0),
        discord.app_commands.Choice(name = "Chickens", value = 1)
    ]
)
@discord.app_commands.default_permissions(
    view_guild_insights = True
)
@discord.app_commands.guild_only()
async def cmd_debate_room(interaction: discord.Interaction, topic: str, chicken1: discord.Member, chicken2: discord.Member,
                          theme: int = 0):
    if chicken1.id == bot.user.id or chicken2.id == bot.user.id:
        return await interaction.response.send_message(
            "Trying to peck at me is a bad idea, son. I have a beak made of steel over here!"
        )
    if chicken1.bot or chicken2.bot:
        return await interaction.response.send_message(
            "Are you really going to fight a robot chicken? C'mon man"
        )
    if interaction.user in [chicken1, chicken2]:
        return await interaction.response.send_message(
            "You'll have a better time debating with the nearest wall, believe me"
        )
    category = interaction.guild.get_channel(ID.CATEGORY.DEBATE)
    await interaction.response.send_message("Preparing your cage, just a sec...")
    msg_response = await interaction.original_response()
    names = CAGE_NAMES[:]
    while len(category.channels) > 35:
        await bot.get_channel(min(c.id for c in category.channels)).delete()

    for chn in category.channels:
        if datetime.datetime.now().timestamp() - chn.created_at.timestamp() > 60 * 60 * 24 * 3:
            await chn.delete()
        else:
            if chn.name.split("-")[1] in names:
                names.remove(chn.name.split("-")[1])
    view_perm = discord.PermissionOverwrite(
        view_channel = True,
        read_messages = True,
        send_messages = False,
        create_public_threads = False,
        create_private_threads = False
    )
    debate_perm = discord.PermissionOverwrite(
        view_channel = True,
        read_messages = True,
        send_messages = True,
        create_public_threads = False,
        create_private_threads = False
    )
    overwrites = {
        interaction.guild.default_role: discord.PermissionOverwrite(view_channel = False, read_messages = False),
        interaction.guild.get_role(ID.ROLE.TIER.LOUNGE): view_perm,
        chicken1: debate_perm,
        chicken2: debate_perm,
        interaction.guild.me: debate_perm
    }
    for r in ID.ROLE.ALL_PROMOTERS:
        overwrites[interaction.guild.get_role(r)] = debate_perm
    channel = await category.create_text_channel(
        f"cage-{random.choice(names)}",
        reason = f"Requested by {str(interaction.user)}",
        overwrites = overwrites
    )
    if theme == 1:
        await interaction.followup.edit_message(
            msg_response.id,
            content = f"Two chickens are planning to fight in the Colosseum!\nLet the pecking commence in <#{channel.id}>!"
        )
    else:
        await interaction.followup.edit_message(
            msg_response.id,
            content = f"Two people are planning to fight in the Colosseum!\nLet the duel commence in <#{channel.id}>!"
        )
    await channel.send(f"""# Time to Duel!
## {topic}
With <@{chicken1.id}> and <@{chicken2.id}>\n\n**15 minutes start now!**
> Each {ID.EMOJI.STAR} gives you one point
> Each {ID.EMOJI.DEAD} takes two points away
""")


# previous =

async def handle_debate_msg(msg):
    if msg.author.bot:
        return
    if msg.channel.name.endswith("ended"):
        return
    if msg.author in msg.channel.overwrites:
        await msg.add_reaction(ID.EMOJI.STAR)
        await msg.add_reaction(ID.EMOJI.DEAD)
    diff = datetime.datetime.now().timestamp() - msg.channel.created_at.timestamp()
    reactions = {}
    user1 = user2 = msg.author.id
    timer_reached = False
    async for message in msg.channel.history(limit = None):
        if message.author.id == bot.user.id and not timer_reached:
            tm = message.content.split()[0]
            timer_reached = True
            if tm == "##":
                # return
                pass
            elif tm == "#":
                if diff >= 60 * 5:
                    await msg.channel.send("10 minutes left!", delete_after = 60 * 5.5)
                return
            elif tm == "10":
                if diff >= 60 * 10:
                    await msg.channel.send("5 minutes left!", delete_after = 60 * 5.5)
                return
            elif tm == "5":
                if diff >= 60 * 12:
                    await msg.channel.send("3 minutes left!", delete_after = 60 * 2.5)
                return
            elif tm == "3":
                if diff >= 60 * 13:
                    await msg.channel.send("2 minutes left!", delete_after = 60 * 1.5)
                return
            elif tm == "2":
                if diff >= 60 * 14:
                    await msg.channel.send("1 minute left!", delete_after = 60 * 1.5)
                return
            elif tm == "1":
                if diff >= 60 * 14 + 30:
                    await msg.channel.send("30 seconds left!", delete_after = 45)
                return
            elif tm == "30":
                if diff >= 60 * 14 + 45:
                    await msg.channel.send("15 seconds left!", delete_after = 30)
                return
            elif tm == "15":
                continue
            else:
                timer_reached = False
        if message.author.id == bot.user.id:
            if message.content.startswith("# Time to Duel!"):
                print("hi")
                user1 = message.mentions[0].id
                user2 = message.mentions[1].id
                if user1 not in reactions:
                    reactions[user1] = {"up": 0, "dn": 0, "score": 0}
                if user2 not in reactions:
                    reactions[user2] = {"up": 0, "dn": 0, "score": 0}
            continue
        if message.author.id not in reactions:
            reactions[message.author.id] = {"up": 0, "dn": 0, "score": 0}
        # print(message.author)
        for reaction in message.reactions:
            if str(reaction.emoji) == ID.EMOJI.DEAD:
                reactions[message.author.id]["dn"] += reaction.count - 1
                reactions[message.author.id]["score"] -= (reaction.count - 1) * 2
            elif str(reaction.emoji) == ID.EMOJI.STAR:
                reactions[message.author.id]["up"] += reaction.count - 1
                reactions[message.author.id]["score"] += (reaction.count - 1)
    view_perm = discord.PermissionOverwrite(
        view_channel = True,
        read_messages = True,
        send_messages = False,
        create_public_threads = False,
        create_private_threads = False
    )
    debate_perm = discord.PermissionOverwrite(
        view_channel = True,
        read_messages = True,
        send_messages = True,
        create_public_threads = False,
        create_private_threads = False
    )
    overwrites = {
        msg.guild.default_role: discord.PermissionOverwrite(view_channel = False, read_messages = False),
        msg.guild.get_role(ID.ROLE.TIER.LOUNGE): view_perm,
        msg.guild.me: debate_perm
    }
    for r in ID.ROLE.ALL_MODERATORS:
        overwrites[msg.guild.get_role(r)] = debate_perm
    await msg.channel.edit(name = msg.channel.name + "-ended", overwrites = overwrites)
    if reactions[user1]["score"] == reactions[user2]["score"]:
        result = "And they both ended in a tie!"
    elif reactions[user1]["score"] > reactions[user2]["score"]:
        score_diff = reactions[user1]["score"] - reactions[user2]["score"]
        result = f"<@{user1}> wins the popular vote by {score_diff} point{'s' if score_diff > 1 else ''}!" + \
                 " \U0001f389\U0001f389\U0001f389"
    else:
        score_diff = reactions[user2]["score"] - reactions[user1]["score"]
        result = f"<@{user2}> wins the popular vote by {score_diff} point{'s' if score_diff > 1 else ''}!" + \
                 " \U0001f389\U0001f389\U0001f389"
    await msg.channel.send(f"""## Alright, time's up! Here are the results
<@{user1}> got {reactions[user1]['up']}x {ID.EMOJI.STAR} and {reactions[user1]['dn']}x {ID.EMOJI.DEAD}
<@{user2}> got {reactions[user2]['up']}x {ID.EMOJI.STAR} and {reactions[user2]['dn']}x {ID.EMOJI.DEAD}

{result}
""")
