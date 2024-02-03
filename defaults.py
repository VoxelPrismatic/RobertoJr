import discord
import os

TOP_COUNT = 10
DEL_COUNT = 8
BAD_COUNT = 5

PROMO_CHANCE = 24

class struct_ROOT_GAMES_t:
    def __init__(self):
        self.PWD = os.environ["PWD"] + "/games/"
        self.POKER = self.PWD + "poker/"

class struct_ROOT_t:
    def __init__(self):
        self.PWD = os.environ["PWD"] + "/"
        self.DATA = self.PWD + "data/"
        self.COMMANDS = self.PWD + "commands/"

        self.GAMES = struct_ROOT_GAMES_t()

global ROOT
ROOT = struct_ROOT_t()

class struct_COMMAND_t:
    def __init__(self):
        self.LINK    = 1087511988311183402
        self.VERIFY  = 1087511988311183403
        self.REFRESH = 1088189649576542379

class struct_CATEGORY_t:
    def __init__(self):
        self.TMG          = 1087618927154188318
        self.MOD_ROOM     = 1112119306629697566
        self.DEBATE       = 1112528956290248754
        self.VOICE        = 1100184111102042184

class struct_CHANNEL_TYPE_t:
    def __init__(self):
        self.THREADS = [
            discord.ChannelType.news_thread,
            discord.ChannelType.public_thread,
            discord.ChannelType.private_thread
        ]
        self.TEXT = [
            discord.ChannelType.text,
            discord.ChannelType.news,
            discord.ChannelType.forum
        ]
        self.VOICE = [
            discord.ChannelType.voice,
            discord.ChannelType.stage_voice
        ]
        self.ALL = [
            *self.THREADS,
            *self.TEXT,
            *self.VOICE
        ]

class struct_CHANNEL_t:
    def __init__(self):
        self.STARBOARD = 1102112919732363344
        self.IRL       = 1086439585392898148
        self.REPORT    = 1166892156070404216
        self.LOG       = 1203227114128678942
        self.BOT       = 1078803196383871051
        self.GAMES     = 1101367590703595570
        self.CALLIN    = 1111587226577547286
        self.SOS       = 1090359660449648770

        self.BOTS = [
            self.BOT,
            self.GAMES
        ]

        self.TYPE = struct_CHANNEL_TYPE_t()

class struct_USER_t:
    def __init__(self):
        self.BEANIE_BOT = 1087462464666488842

class struct_ROLE_CAST_t:
    def __init__(self):
        self.MEMBER = 1078137528240062484
        self.ADMIN  = 1078117523582615552

class struct_ROLE_RANK_t:
    def __init__(self):
        self.LOUNGE = 1078137967727628320
        self.VIP    = 1085655143816630312
        self.SILVER = 1093386797280669716
        self.ELITE  = 1085998959908106280

class struct_ROLE_SUPER_t:
    def __init__(self):
        self.ELITE       = 1092847186020155523
        self.MODERATOR   = 1092845420675338462
        self.COORDINATOR = 1097237212233478154
        self.PROMOTER    = 1100892266077356142

class struct_ROLE_t:
    def __init__(self):
        self.SUPER = struct_ROLE_SUPER_t()
        self.TIER = struct_ROLE_RANK_t()
        self.CAST = struct_ROLE_CAST_t()
        self.GOOF = 1093004398667509862

        self.ALL_ADMINS = [
            self.CAST.MEMBER,
            self.CAST.ADMIN
        ]

        self.ALL_MODERATORS = [
            self.SUPER.ELITE,
            self.SUPER.MODERATOR,
            *self.ALL_ADMINS
        ]

        self.ALL_PROMOTERS = [
            self.SUPER.COORDINATOR,
            self.SUPER.PROMOTER,
            *self.ALL_MODERATORS
        ]

        self.ALL_MEMBERS = [
            self.TIER.LOUNGE,
            self.TIER.VIP,
            self.TIER.SILVER,
            self.TIER.ELITE,
            *self.ALL_PROMOTERS
        ]

class struct_EMOJI_t:
    def __init__(self):
        self.STAR = "<:20_Sided_Die:1088929649704312914>"
        self.DEAD = "<:1_Sided_Die:1088929590296190986>"
        self.ELITE = "<:TIMCASTGoldBeanie_flat:1088939968778477589>"
        self.SEND = "<:send:1114385588943065099>"

        self.LISTENING = [
            self.STAR,
            self.DEAD
        ]

class struct_ID_t:
    def __init__(self):
        self.GUILD = 1078108746410119208
        self.COMMAND = struct_COMMAND_t()
        self.CATEGORY = struct_CATEGORY_t()
        self.CHANNEL = struct_CHANNEL_t()
        self.USER = struct_USER_t()
        self.ROLE = struct_ROLE_t()
        self.EMOJI = struct_EMOJI_t()
        self.GUILD_OBJ = discord.Object(self.GUILD)

    def RNG(self):
        return f"{random.randint(0, 65535):04x}"

global ID
ID = struct_ID_t()

PROMO_CHANCE = list(range(PROMO_CHANCE))
SHAMELESS_PROMO = "\n\n*shameless promo: [consider donating](https://cash.app/$VoxelPrismatic)*"


PRESENCES = [
    {"name": "with Cast Brew Coffee", "type": discord.ActivityType.playing},
    {"name": "coffee brewing", "type": discord.ActivityType.listening},
    {"name": "steam rise", "type": discord.ActivityType.watching},
    {"name": "beanie stadium", "type": discord.ActivityType.competing},
    {"name": "Cast Castle", "type": discord.ActivityType.watching},

    {"name": "Bright Eyes", "type": discord.ActivityType.listening},
    {"name": "Will of the People", "type": discord.ActivityType.listening},
    {"name": "Only Ever Wanted", "type": discord.ActivityType.listening},
    {"name": "Genocide (Losing my Mind)", "type": discord.ActivityType.listening},
    {"name": "Together Again", "type": discord.ActivityType.listening},

    {"name": "my chickens", "type": discord.ActivityType.watching},
    {"name": "coffee grow", "type": discord.ActivityType.watching},
    {"name": "with eggs", "type": discord.ActivityType.playing},
    {"name": "the sunrise", "type": discord.ActivityType.watching},
    {"name": "the sunset", "type": discord.ActivityType.watching},
]

DATA_DIRS = [
    "dead",
    "games/poker",
    "jailed",
    "levels/pfp",
    "levels/saved",
    "stars",
    "strike/history",
    "strike/cooldown",
    "notes",
    "notes/files",
    "goofed"
]
