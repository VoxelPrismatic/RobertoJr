REASON_STR = {
    1: "Horny/Simp",
    2: "Sexual Harassment",
    3: "Threats",
    4: "Drunk/Crazy",
    5: "Excessive Spam",
    6: "NSFW Content",
    7: "Sailor Mouth",
    8: "Logical Fallacy",
    0: "Other",
}

@tree.command(
    name = "report",
    description = "Anonymously report a user",
    guild = ID.GUILD_OBJ
)
@discord.app_commands.describe(
    member = "Who to report",
    reason = "Overall reason",
    explain = "Further explanation, eg quote or message content"
)
@discord.app_commands.choices(
    reason = [
        discord.app_commands.Choice(name = REASON_STR[s], value = s) for s in REASON_STR
    ]
)
@discord.app_commands.guild_only()
async def cmd_strike(interaction: discord.Interaction, member: discord.Member, reason: int, explain: str):

    if interaction.user.id == member.id:
        return await interaction.response.send_message(
            "Imagine trying to bonk yourself..."
        )

    await interaction.response.defer(ephemeral = True, thinking = True)
    cooldown_dir = ROOT.DATA + f"strike/cooldown/{interaction.user.id}/"
    cooldown_name = cooldown_dir + str(member.id)
    os.makedirs(cooldown_dir, exist_ok = True)
    for f in os.listdir(cooldown_dir):
        if time.time() - os.stat(cooldown_dir + f).st_mtime > 60 * 60 * 12:
            os.remove(cooldown_dir + f)

    if interaction.permissions.view_guild_insights:
        pass
    elif os.path.isfile(cooldown_name):
        return await interaction.edit_original_response(
            content = f"Sorry, you can only report <@{member.id}> once per day. This is to avoid spam"
        )
    elif len(os.listdir(cooldown_dir)) >= 5:
        return await interaction.edit_original_response(
            content = f"Sorry, you can only report up to {len(os.listdir(cooldown_dir))} members per day. This is to avoid spam"
        )

    open(cooldown_name, "w+").write("")

    json_name = ROOT.DATA + f"strike/history/{member.id}.json"

    try:
        data = json.loads(open(json_name, "r").read())
    except:
        data = []

    data.append(
        {
            "date": str(datetime.datetime.now().strftime("%a, %b %d, %Y; %I:%M:%S %p UTC")),
            "reason": REASON_STR[reason],
            "explain": explain,
            "channel": f"{interaction.channel.name}     <#{interaction.channel.id}>",
            "jump": f"https://discord.com/channels/{interaction.guild_id}/{interaction.channel_id}/{interaction.channel.last_message_id}",
            "reporter": f"{interaction.user.id}",
        }
    )

    open(json_name, "w+").write(json.dumps(data, indent = 4))

    embed = discord.Embed(
        color = 0xff0000,
        description = f"""# {REASON_STR[reason]}
**Total reports for this reason: {len([x for x in data if x['reason'] == REASON_STR[reason]])}**
Reported in <#{interaction.channel_id}> at <t:{int(datetime.datetime.now().timestamp())}:F>
[Jump to context]({data[-1]['jump']})
"""
    )
    embed.add_field(
        name = "Explanation",
        value = explain,
        inline = False
    )
    embed.set_author(name = str(member), icon_url = (member.guild_avatar or  member.avatar or member.default_avatar).url)

    embed2 = embed.copy()
    embed2.set_footer(text = f"This user has {len(data)} reports total")
    if len(data) >= 5:
        await bot.get_channel(ID.CHANNEL.REPORT).send(
            embed = embed2,
            file = discord.File(open(json_name), filename = f"history-{str(member)}.json")
        )
    await bot.get_channel(ID.CHANNEL.LOG).send(
            embed = embed2,
            file = discord.File(open(json_name), filename = f"history-{str(member)}.json")
    )
    return await interaction.edit_original_response(
        content = "Report sent!",
        embed = embed
    )
