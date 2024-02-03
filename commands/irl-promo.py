last_promo_sent = datetime.datetime.now().replace(year = 2016)
last_block_sent = datetime.datetime.now().replace(year = 2016)

BLOCK_MSG = f"""__**<@&1078137967727628320> members!**__
Do you have a question you wanna ask? Have you been a member for 6 months?
If so go to <#{ID.CHANNEL.BOT}> use </refresh:{ID.COMMAND.REFRESH}> to promote your account to <@&{ID.ROLE.TIER.VIP}> level.

If not, you can always upgrade to <@&{ID.ROLE.TIER.SILVER}> ($25/mo) and get INSTANT access to call ins, as well as memes and the ability to post GIFs in chat.
If you would like to upgrade and don't know how, just reply to this message and I’ll provide you instructions step by step!

__**If you are already <@&{ID.ROLE.TIER.VIP}>, <@&{ID.ROLE.TIER.SILVER}> or <@&{ID.ROLE.TIER.ELITE}>**__
Please visit <#{ID.CHANNEL.CALLIN}> and ask your questions! We all know you have questions brewing, so as long as it's open ended it will make for a fun call!"""

PROMO_MSG = f"""
Visit <#{ID.CHANNEL.CALLIN}> and ask a question or upvote one you'd like to hear with {ID.EMOJI.STAR}"""

POKER_MSG = f"""**We have poker!** Please visit <#{ID.CHANNEL.GAMES}> and use </poker:1105029819009347665> to get started"""

async def handle_irl_channel(msg):
    global last_promo_sent, last_block_sent

    now = datetime.datetime.utcnow().astimezone(pytz.timezone("America/Chicago"))

    if now.weekday() in [0, 5, 6]:
        return


    if now.hour < 19 or (now.hour == 20 and now.minute >= 45) or now.hour >= 21:
        # print(f"out: {now.hour:02}:{now.minute:02}")
        # till = now.replace(hour = 19, minute = 0, second = 0)
        # diff = int(till.timestamp() - now.timestamp())
        last_promo_sent = now.replace(year = 2016)
        last_block_sent = now.replace(year = 2016)
        # print(f"diff: {diff // 3600:02}h {diff // 60 % 60:02}m {diff % 60:02}s")
        return # Out of time slot
    if now.strftime("%a") == "Fri":
        print("Friday")
        return



    till = now.replace(hour = 20, minute = 45, second = 0)
    diff = int(till.timestamp() - now.timestamp())
    dist = int(now.timestamp() - last_promo_sent.timestamp())

    # if now.timestamp() - last_block_sent.timestamp() >= 1200: # 20 minutes
    #     last_block_sent = now
    #     await msg.channel.send(BLOCK_MSG)
    #     return

    t_s = int(till.timestamp())
    if diff >= 60 * 60:
        if dist >= 60 * 20:
            await msg.channel.send(
                POKER_MSG if random.randint(0, 9) == 0 else f"**Call-in's close <t:{t_s}:R>!**" + PROMO_MSG,
                delete_after = 30
            )
            last_promo_sent = now
            return
        print("80", dist)
    elif diff >= 60 * 30:
        if dist >= 60 * 15:
            await msg.channel.send(
                POKER_MSG if random.randint(0, 9) == 0 else f"**Call-in's close <t:{t_s}:R>!**" + PROMO_MSG,
                delete_after = 20
            )
            last_promo_sent = now
            return
        print("60", dist)
    elif diff >= 60 * 10:
        if dist >= 60 * 10:
            await msg.channel.send(
                POKER_MSG if random.randint(0, 9) == 0 else f"**Call-in's close <t:{t_s}:R>!**" + PROMO_MSG,
                delete_after = 15
            )
            last_promo_sent = now
            return
        print("30", dist)
    else:
        if dist >= 60 * 5:
            await msg.channel.send(
                POKER_MSG if random.randint(0, 9) == 0 else \
                    f"**Time's running out! \U0001f525\U0001f525\U0001f525**\n**Call-in's close <t:{t_s}:R>!**" + PROMO_MSG,
                delete_after = 10
            )
            last_promo_sent = now
            return
        print("15", dist)

@tree.command(
    name = "call-in-available",
    description = "Enables or disables call-in messages",
    guild = ID.GUILD_OBJ
)
@discord.app_commands.describe(
    availability = "Whether or not call-in's available"
)
@discord.app_commands.choices(
    availability = [
        discord.app_commands.Choice(name = "No call-in's for today", value = 2999),
        discord.app_commands.Choice(name = "Available", value = 2016)
    ]
)
@discord.app_commands.default_permissions(
    view_guild_insights = True
)
@discord.app_commands.guild_only()
async def cmd_shill_call_in(interaction: discord.Interaction, availability: int):
    global last_promo_sent, last_block_sent
    last_block_sent = last_block_sent.replace(year = availability)
    last_promo_sent = last_promo_sent.replace(year = availability)
    return await interaction.response.send_message(f"Done!", ephemeral = True)

@tree.command(
    name = "close-call-in",
    description = "Just sends a message indicating call-in's are closed for today",
    guild = ID.GUILD_OBJ
)
@discord.app_commands.default_permissions(
    view_guild_insights = True
)
@discord.app_commands.guild_only()
async def cmd_close_call_in(interaction: discord.Interaction):
    if await verify_perms(interaction, ID.ROLE.ALL_PROMOTERS):
        return await interaction.response.send_message(
            "Sorry, you have to be a promoter to end call-in's for today",
            ephemeral = True
        )

    now = datetime.datetime.utcnow().astimezone(pytz.timezone("America/Chicago")).replace(hour = 20, minute = 45, second = 0)

    block = "\u200b" + ("\n" * 60)

    if now.weekday() == 4:
        return await interaction.response.send_message(f"""{block}
## —~=:[ Call-In's Closed for {now.strftime('%B %d')} ]:=~—
No after show on Fridays! Come back Monday with questions!
""")
    await interaction.response.send_message(f"""{block}
## —~=:[ Call-In's Closed for {now.strftime('%B %d')} ]:=~—
Please try to get your questions in before <t:{int(now.timestamp())}:t> (9:45p EST); the earlier the better
""")

@tree.command(
    name = "swap",
    description = "Swaps the positions of any two categories",
    guild = ID.GUILD_OBJ
)
@discord.app_commands.default_permissions(
    administrator = True
)
@discord.app_commands.describe(
    category1 = "Category 1; Default is TMG",
    category2 = "Category 2; Default is Voice"
)
@discord.app_commands.guild_only()
async def cmd_showtime(interaction: discord.Interaction,
                       category1: discord.CategoryChannel = None,
                       category2: discord.CategoryChannel = None):
    if category1 is None:
        category1 = interaction.guild.get_channel(ID.CATEGORY.TMG)
    if category2 is None:
        category2 = interaction.guild.get_channel(ID.CATEGORY.VOICE)
    p1, p2 = category1.position, category2.position
    if p1 > p2:
        p1, p2, category1, category2 = p2, p1, category2, category1
    await category2.edit(position = p1)
    await category1.edit(position = p2)
    await interaction.response.send_message("Done!", ephemeral = True)
