import discord
import os

TOP_COUNT = 10
DEL_COUNT = 8
BAD_COUNT = 5

ROOT = os.environ["PWD"] + "/"
ROOT_DATA = ROOT + "data/"
ROOT_COMMANDS = ROOT + "commands/"

GUILD = 1078108746410119208
CATEGORY = 1087618927154188318
STARBOARD = 1102112919732363344
ELITE_ROLE = 1085998959908106280
LINK_COMMAND_ID = 1087511988311183402
VERIFY_COMMAND_ID = 1087511988311183403
ONBOARDING_CHANNEL = 1078803196383871051
ONBOARD_HELP_CHANNEL = 1090359660449648770
BEANIE_BOT_ID = 1087462464666488842

STAR_EMOJI = "<:20_Sided_Die:1088929649704312914>"
DEAD_EMOJI = "<:1_Sided_Die:1088929590296190986>"
ELITE_EMOJI = "<:TIMCASTGoldBeanie_flat:1088939968778477589>"
LISTENING_EMOJIS = [
    STAR_EMOJI,
    DEAD_EMOJI
]

BOT_CHANNELS = [
    1101367590703595570,
    1078803196383871051
]

THREADS = [
    discord.ChannelType.news_thread,
    discord.ChannelType.public_thread,
    discord.ChannelType.private_thread
]
TEXT_CHATS = [
    discord.ChannelType.text,
    discord.ChannelType.news,
    discord.ChannelType.forum
]
VOICE_CHATS = [
    discord.ChannelType.voice,
    discord.ChannelType.stage_voice
]
ALL_CHATS = [
    *THREADS,
    *TEXT_CHATS,
    *VOICE_CHATS
]


PRESENCES = [
    {"name": "with Cast Brew Coffee", "type": discord.ActivityType.playing},
    {"name": "coffee brewing", "type": discord.ActivityType.listening},
    {"name": "steam rise", "type": discord.ActivityType.watching},
    {"name": "beanie stadium", "type": discord.ActivityType.competing},
    {"name": "Bright Eyes", "type": discord.ActivityType.listening},
    {"name": "Will of the People", "type": discord.ActivityType.listening},
    {"name": "Only Ever Wanted", "type": discord.ActivityType.listening},
    {"name": "Genocide (Losing my Mind)", "type": discord.ActivityType.listening},
    {"name": "my chickens", "type": discord.ActivityType.watching},
    {"name": "coffee grow", "type": discord.ActivityType.watching},
    {"name": "eggs", "type": discord.ActivityType.playing},
    {"name": "the sunrise", "type": discord.ActivityType.watching},
    {"name": "the sunset", "type": discord.ActivityType.watching}
]
