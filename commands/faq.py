_FAQ_ = {
    "Rumble/Members content not working in app":
        "Please log out and log back into the app.\n"
        "If you forget your username, you can submit a password reset request "
        "(resetting your password is not necessary, it is the easiest way to find your username",

}

@tree.command(
    name = "faq",
    description = "Frequently asked questions when it comes to trouble shooting",
    guild = ID.GUILD_OBJ
)
@discord.app_commands.describe(
    issue = "What the problem or question is"
)
async def cmd_faq(interaction: discord.Interaction, issue: str):
    try:
        issue = list(_FAQ_)[int(issue)]
    except ValueError:
        if issue not in _FAQ_:
            return await interaction.response.send_message("Question or issue not found")
    return await interaction.response.send_message(_FAQ_[issue])

@cmd_faq.autocomplete("issue")
async def cmd_faq_autofill(interaction: discord.Interaction, current: str):
    ls = []
    for i, key in enumerate(_FAQ_):
        if current.lower() in key.lower():
            ls.append(discord.app_commands.Choice(name = key, value = str(i)))
    return ls
